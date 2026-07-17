"""数据导入脚本: 从两份 Excel 读取工时明细和花名册, 清洗后落库 SQLite。

每次运行全量替换(先 DELETE 旧数据再 INSERT), 保证幂等。
调用方式:
    cd apps/back
    uv run python scripts/import_data.py
    uv run python scripts/import_data.py --workhour path/to/工时.xlsx --roster path/to/花名册.xlsx
"""

import argparse
import logging
import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, create_engine, text

# 确保项目根目录在 sys.path, 以便 import app 模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.base import metadata
from app.models.employee import Employee
from app.models.work_hour import WorkHour

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 默认文件路径(相对于项目根目录 apps/back)
DEFAULT_WORKHOUR_PATH = "../../docs/res/2026-01-01~2026-06-30工时明细.xlsx"
DEFAULT_ROSTER_PATH = "../../docs/res/完整花名册_合并整理.xlsx"

# 花名册 Excel 列的索引 -> 模型字段映射
ROSTER_COL_MAP: dict[int, str] = {
    0: "name",
    1: "employee_id",
    2: "position",
    3: "level1_dept",
    4: "level2_dept",
    5: "level3_dept",
    6: "level4_dept",
    7: "actual_team",
    8: "role",
    # 9-13: 计划投入项目1-5, 不导入
    14: "remarks",
    15: "employee_type",
    16: "employee_status",
    17: "position_name",
    18: "entry_date",
    19: "leave_date",
    20: "temp_report_note",
}

# 工时明细 Excel 列的索引 -> 模型字段映射
WORKHOUR_COL_MAP: dict[int, str] = {
    0: "project_name",
    1: "reporter",
    2: "reporter_department",
    3: "creator",
    4: "report_date",
    5: "hours",
    6: "description",
}


def _parse_date(val: object) -> date | None:
    """解析日期为 date 对象。"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, date):
        return val
    val_str = str(val).strip() if not isinstance(val, str) else val.strip()
    if not val_str:
        return None
    try:
        return pd.to_datetime(val_str).date()
    except Exception:
        logger.warning("无法解析日期: %r", val)
        return None


def _safe_str(val: object) -> str:
    """安全转为字符串, 清洗空值和 NaN。"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


def _safe_float(val: object) -> float:
    """安全转为浮点数。"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    try:
        return float(val)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return 0.0


def import_roster(engine: Engine, filepath: str) -> dict[str, int]:
    """导入花名册, 返回 name -> employee_id(int) 的映射字典。"""
    logger.info("读取花名册: %s", filepath)
    df = pd.read_excel(filepath)

    name_to_eid: dict[str, int] = {}
    import_count = 0

    table = Employee.__table__  # type: ignore[attr-defined]
    with engine.begin() as conn:
        for _, row in df.iterrows():
            name = _safe_str(row.iloc[0])
            if not name:
                continue

            emp_data: dict[str, object] = {
                "match_status": "roster_only",
                "is_outsourced": 0,
            }

            for col_idx, field_name in ROSTER_COL_MAP.items():
                if col_idx >= len(row):
                    continue
                val = row.iloc[col_idx]
                if field_name == "name":
                    emp_data[field_name] = name
                elif field_name == "employee_id":
                    eid_str = _safe_str(val)
                    eid_str = eid_str.split(".")[0] if "." in eid_str else eid_str
                    emp_data[field_name] = eid_str if eid_str else None
                elif field_name in ("entry_date", "leave_date"):
                    emp_data[field_name] = _parse_date(val)
                else:
                    raw = _safe_str(val)
                    emp_data[field_name] = raw if raw else None

            result = conn.execute(table.insert().values(**emp_data))
            pk = result.inserted_primary_key
            name_to_eid[name] = pk[0] if pk else 0
            import_count += 1

    logger.info("花名册导入完成: %d 人", import_count)
    return name_to_eid


def _match_reporter(reporter: str, name_to_eid: dict[str, int]) -> tuple[int | None, list[int]]:
    """匹配填报人到花名册。

    返回 (employee_id, [需要标记为 outsourced 的 employee_id 列表])
    """
    reporter = reporter.strip()
    if not reporter:
        return None, []

    # 精确匹配
    if reporter in name_to_eid:
        return name_to_eid[reporter], []

    # 去除 _sz 后缀匹配
    if reporter.endswith("_sz"):
        base_name = reporter[:-3]
        if base_name in name_to_eid:
            return name_to_eid[base_name], [name_to_eid[base_name]]

    return None, []


def import_workhours(engine: Engine, filepath: str, name_to_eid: dict[str, int]) -> int:
    """导入工时明细, 逐行匹配 reporter 到花名册。"""
    logger.info("读取工时明细: %s", filepath)
    df = pd.read_excel(filepath)

    import_count = 0
    matched_count = 0
    outsourced_eids: set[int] = set()

    table = WorkHour.__table__  # type: ignore[attr-defined]
    with engine.begin() as conn:
        for _, row in df.iterrows():
            wh_data: dict[str, object] = {}

            for col_idx, field_name in WORKHOUR_COL_MAP.items():
                if col_idx >= len(row):
                    continue
                val = row.iloc[col_idx]
                if field_name == "project_name":
                    wh_data[field_name] = _safe_str(val)
                elif field_name == "reporter":
                    reporter_name = _safe_str(val)
                    wh_data[field_name] = reporter_name
                    eid, oids = _match_reporter(reporter_name, name_to_eid)
                    wh_data["employee_id"] = eid
                    if eid is not None:
                        matched_count += 1
                    outsourced_eids.update(oids)
                elif field_name == "report_date":
                    wh_data[field_name] = _parse_date(val)
                elif field_name == "hours":
                    wh_data[field_name] = _safe_float(val)
                elif field_name == "description":
                    raw = _safe_str(val)
                    wh_data[field_name] = raw if raw else None
                else:
                    raw = _safe_str(val)
                    wh_data[field_name] = raw if raw else None

            conn.execute(table.insert().values(**wh_data))
            import_count += 1

    logger.info("工时明细导入完成: %d 条, 匹配成功: %d 条", import_count, matched_count)
    return len(outsourced_eids)


def update_post_import(engine: Engine) -> None:
    """导入后处理: 更新 match_status, 标记外包人员。"""
    with engine.begin() as conn:
        conn.execute(text("UPDATE employees SET match_status = 'roster_only'"))
        conn.execute(
            text(
                "UPDATE employees SET match_status = 'matched' "
                "WHERE id IN (SELECT DISTINCT employee_id FROM work_hours WHERE employee_id IS NOT NULL)"
            ),
        )
        conn.execute(
            text(
                "UPDATE employees SET is_outsourced = 1 "
                "WHERE id IN ("
                "  SELECT DISTINCT e.id FROM employees e "
                "  INNER JOIN work_hours wh ON wh.employee_id = e.id "
                "  WHERE wh.reporter LIKE '%_sz' AND e.name = REPLACE(wh.reporter, '_sz', '')"
                ")"
            ),
        )

    logger.info("match_status 与外包标记已更新")


def print_stats(engine: Engine) -> None:
    """打印导入统计信息。"""
    with engine.begin() as conn:
        emp_count = conn.execute(text("SELECT COUNT(*) FROM employees")).scalar()
        wh_count = conn.execute(text("SELECT COUNT(*) FROM work_hours")).scalar()
        matched = conn.execute(text("SELECT COUNT(*) FROM employees WHERE match_status = 'matched'")).scalar()
        roster_only = conn.execute(text("SELECT COUNT(*) FROM employees WHERE match_status = 'roster_only'")).scalar()
        outsourced = conn.execute(text("SELECT COUNT(*) FROM employees WHERE is_outsourced = 1")).scalar()
        null_eid = conn.execute(text("SELECT COUNT(*) FROM work_hours WHERE employee_id IS NULL")).scalar()
        distinct_reporters = conn.execute(text("SELECT COUNT(DISTINCT reporter) FROM work_hours")).scalar()
        distinct_projects = conn.execute(text("SELECT COUNT(DISTINCT project_name) FROM work_hours")).scalar()

    logger.info("=== 导入统计 ===")
    logger.info("花名册总人数: %d", emp_count)
    logger.info("工时明细条数: %d", wh_count)
    logger.info("匹配成功: %d 人", matched)
    logger.info("仅花名册(无工时): %d 人", roster_only)
    logger.info("外部人力资源标记: %d 人", outsourced)
    logger.info("无匹配工时的记录(employee_id=NULL): %d 条", null_eid)
    logger.info("填报人数: %d 人", distinct_reporters)
    logger.info("项目数: %d 个", distinct_projects)


def main() -> None:
    parser = argparse.ArgumentParser(description="产能分析系统数据导入脚本")
    parser.add_argument("--workhour", default=None, help="工时明细 Excel 路径")
    parser.add_argument("--roster", default=None, help="花名册 Excel 路径")
    parser.add_argument("--db", default="dev.db", help="SQLite 数据库文件路径 (默认: dev.db)")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent

    workhour_path = args.workhour or str(base_dir / DEFAULT_WORKHOUR_PATH)
    roster_path = args.roster or str(base_dir / DEFAULT_ROSTER_PATH)

    if not os.path.exists(workhour_path):
        logger.error("工时明细文件不存在: %s", workhour_path)
        sys.exit(1)
    if not os.path.exists(roster_path):
        logger.error("花名册文件不存在: %s", roster_path)
        sys.exit(1)

    db_path = str(base_dir / args.db) if not os.path.isabs(args.db) else args.db
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)

    logger.info("开始导入: workhour=%s, roster=%s, db=%s", workhour_path, roster_path, db_path)

    # 建表(幂等)
    metadata.create_all(engine)

    # 清空旧数据(全量替换)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM work_hours"))
        conn.execute(text("DELETE FROM employees"))

    # 导入花名册
    name_to_eid = import_roster(engine, roster_path)

    # 导入工时明细
    import_workhours(engine, workhour_path, name_to_eid)

    # 更新 match_status 和外包标记
    update_post_import(engine)

    # 统计
    print_stats(engine)
    engine.dispose()

    logger.info("数据导入完成!")


if __name__ == "__main__":
    main()
