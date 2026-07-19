"""Excel 数据源实现: 基于 pandas + openpyxl 读取 Excel 文件。"""

from collections.abc import Iterator

import pandas as pd

from app.datasources.base import DataSourceProvider


class ExcelDataSourceProvider(DataSourceProvider):
    """基于 pandas + openpyxl 的 Excel 数据源实现。

    Args:
        work_hour_path: 工时明细 Excel 路径
        roster_path: 花名册 Excel 路径
        category_path: 项目分类&项目清单 Excel 路径
        holiday_path: 节假日 Excel 路径
        plan_path: 三快计划 Excel 路径(可选)
    """

    def __init__(
        self,
        work_hour_path: str,
        roster_path: str,
        category_path: str,
        holiday_path: str,
        plan_path: str | None = None,
    ) -> None:
        self._paths = {
            "work_hour": work_hour_path,
            "roster": roster_path,
            "category": category_path,
            "holiday": holiday_path,
            "plan": plan_path,
        }

    def provide_employees(self) -> Iterator[dict[str, object]]:
        df = pd.read_excel(self._paths["roster"], engine="openpyxl")
        for _idx, row in df.iterrows():
            yield {
                "name": _safe_str(row.get("姓名")),
                "employee_id": _safe_str_or_none(row.get("工号")),
                "position": _safe_str_or_none(row.get("岗位")),
                "level1_dept": _safe_str_or_none(row.get("一级部门")),
                "level2_dept": _safe_str_or_none(row.get("二级部门")),
                "level3_dept": _safe_str_or_none(row.get("三级部门")),
                "level4_dept": _safe_str_or_none(row.get("四级部门")),
                "actual_team": _safe_str_or_none(row.get("实际投入小组")),
                "role": _safe_str_or_none(row.get("角色")),
                "employee_type": _safe_str_or_none(row.get("员工类型")),
                "employee_status": _safe_str_or_none(row.get("员工状态")),
                "position_type": _safe_str_or_none(row.get("岗位类型")),
                "entry_date": _safe_date(row.get("入职日期")),
                "leave_date": _safe_date(row.get("离职日期")),
                "fill_note": _safe_str_or_none(row.get("工时填报说明")),
                "remarks": _safe_str_or_none(row.get("备注")),
                "planned_project1": _safe_str_or_none(row.get("计划投入项目1")),
                "planned_project2": _safe_str_or_none(row.get("计划投入项目2")),
                "planned_project3": _safe_str_or_none(row.get("计划投入项目3")),
                "planned_project4": _safe_str_or_none(row.get("计划投入项目4")),
                "planned_project5": _safe_str_or_none(row.get("计划投入项目5")),
                "fill_note": _safe_str_or_none(row.get("工时填报说明")),
                "remarks": _safe_str_or_none(row.get("备注")),
                "is_excluded": _safe_str(row.get("工时填报说明", "")) in ("勉填", "异常未填") or "无需填报" in str(row.get("备注", "")),
            }

    def provide_work_hours(self) -> Iterator[dict[str, object]]:
        df = pd.read_excel(self._paths["work_hour"], engine="openpyxl")
        for _idx, row in df.iterrows():
            yield {
                "project_name": _safe_str(row.get("项目名称", "")),
                "reporter": _safe_str(row.get("填报人", "")),
                "reporter_department": _safe_str_or_none(row.get("填报人部门")),
                "creator": _safe_str_or_none(row.get("创建人")),
                "report_date": _safe_date(row.get("产能日期")),
                "hours": _safe_float(row.get("投入工时", 0.0)),
                "description": _safe_str_or_none(row.get("工作说明")),
            }

    def provide_project_categories(self) -> list[dict[str, object]]:
        """从项目分类Excel构建三级树形分类 + 项目清单映射。

        实际 Excel 结构:
          - sheet '项目分类': 列 ['大类', '二级分类', '三级分类'], 首行为空头行
            每行: 大类/二级分类有合并单元格(前一行的非空值需沿用)
          - sheet '项目清单': 列 ['#', '项目名称', '三级分类']
            每行: 项目名 -> 三级分类名的映射

        返回: 扁平记录列表, 每条含 category_name/level/parent_id/sort_order
          - level=1: 大类 (parent_id=None)
          - level=2: 二级分类 (parent_id=level1的id)
          - level=3: 三级分类 (parent_id=level2的id)
          - level=0: 项目名 (parent_id=三级分类的id), 专用于项目清单匹配
        """
        df_cat = pd.read_excel(self._paths["category"], sheet_name="项目分类", engine="openpyxl")
        df_list = pd.read_excel(self._paths["category"], sheet_name="项目清单", engine="openpyxl")
        results: list[dict[str, object]] = []
        # key_to_id: (category_name, level) -> 1-based index in results list
        key_to_id: dict[tuple[str, int], int] = {}

        # 列定位: iloc[0]=大类, iloc[1]=二级分类, iloc[2]=三级分类
        # 合并单元格在 pandas 中表现为 NaN, 需向前填充
        cols = [df_cat.iloc[:, 0], df_cat.iloc[:, 1], df_cat.iloc[:, 2]]
        # 向前填充合并单元格
        last_major: str | None = None
        last_mid: str | None = None
        for _idx in range(len(df_cat)):
            raw_major = cols[0].iloc[_idx]
            raw_mid = cols[1].iloc[_idx]
            raw_sub = cols[2].iloc[_idx]

            # 跳过全空行
            if pd.isna(raw_major) and pd.isna(raw_mid) and pd.isna(raw_sub):
                continue

            major = _clean_cell(raw_major)
            mid = _clean_cell(raw_mid)
            sub = _clean_cell(raw_sub)

            # 合并单元格导致的 NaN: 沿用上一行的值
            if major:
                last_major = major
            else:
                major = last_major or ""
            if mid:
                last_mid = mid
            else:
                mid = last_mid or ""
            if not sub:
                continue

            # 大类 (level=1)
            key1 = (major, 1)
            if key1 not in key_to_id:
                results.append({"category_name": major, "category_level": 1, "parent_id": None, "sort_order": 0})
                key_to_id[key1] = len(results)

            # 二级分类 (level=2)
            key2 = (mid, 2)
            if key2 not in key_to_id:
                results.append(
                    {"category_name": mid, "category_level": 2, "parent_id": key_to_id[key1], "sort_order": 0}
                )
                key_to_id[key2] = len(results)

            # 三级分类 (level=3)
            key3 = (sub, 3)
            if key3 not in key_to_id:
                results.append(
                    {"category_name": sub, "category_level": 3, "parent_id": key_to_id[key2], "sort_order": 0}
                )
                key_to_id[key3] = len(results)

        # 项目清单: 项目名 -> 三级分类 的映射
        proj_col = df_list.iloc[:, 1]  # 项目名称
        cat_col = df_list.iloc[:, 2]  # 三级分类
        for _idx in range(len(df_list)):
            proj_name = _clean_cell(proj_col.iloc[_idx])
            sub_cat_raw = cat_col.iloc[_idx]
            sub_cat = _clean_cell(sub_cat_raw)
            if not proj_name or not sub_cat:
                continue

            # 匹配三级分类 id (去除所有空格后匹配)
            sub_cat_compact = sub_cat.replace(" ", "").replace("　", "")
            cat_id: int | None = None
            for (name_key, lvl), cid in key_to_id.items():
                if lvl == 3 and name_key.replace(" ", "").replace("　", "") == sub_cat_compact:
                    cat_id = cid
                    break

            results.append({"category_name": proj_name, "category_level": 0, "parent_id": cat_id, "sort_order": 0})
        return results

    def provide_holidays(self) -> list[dict[str, object]]:
        """解析节假日: 展开放假时间范围 + 补班日为逐日记录。

        实际 Excel 列: ['年份', '节假日', '放假时间', '补班时间']
        放假时间格式: "2026年2月15日到2026年2月24日"
        补班时间格式: "2026年2月14日和2026年3月1日" 或 Excel日期数字(如46151)或空
        """
        import re as _re
        from datetime import date as _date
        from datetime import timedelta as _td

        df = pd.read_excel(self._paths["holiday"], sheet_name=0, engine="openpyxl")
        results: list[dict[str, object]] = []

        # 日期解析: "2026年2月15日"
        _date_re = _re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")

        col_name = df.iloc[:, 1]  # 节假日名称
        col_off = df.iloc[:, 2]  # 放假时间
        col_supp = df.iloc[:, 3]  # 补班时间

        for _idx in range(len(df)):
            name_raw = col_name.iloc[_idx]
            off_raw = col_off.iloc[_idx]
            supp_raw = col_supp.iloc[_idx]

            if pd.isna(name_raw):
                continue
            name = str(name_raw).strip()

            # 放假时间: 展开范围 "2026年2月15日到2026年2月24日"
            off_str = str(off_raw) if pd.notna(off_raw) else ""
            off_dates = _date_re.findall(off_str)
            if len(off_dates) >= 2:
                start = _date(int(off_dates[0][0]), int(off_dates[0][1]), int(off_dates[0][2]))
                end = _date(int(off_dates[1][0]), int(off_dates[1][1]), int(off_dates[1][2]))
                d = start
                while d <= end:
                    results.append({"holiday_name": name, "holiday_date": d, "is_workday": False})
                    d += _td(days=1)
            elif len(off_dates) == 1:
                d = _date(int(off_dates[0][0]), int(off_dates[0][1]), int(off_dates[0][2]))
                results.append({"holiday_name": name, "holiday_date": d, "is_workday": False})

            # 补班时间: 展开 "2026年2月14日和2026年3月1日" 或解析Excel数字日期
            supp_str = str(supp_raw) if pd.notna(supp_raw) else ""
            supp_dates = _date_re.findall(supp_str)
            for sd in supp_dates:
                d = _date(int(sd[0]), int(sd[1]), int(sd[2]))
                results.append({"holiday_name": name + "补班", "holiday_date": d, "is_workday": True})

            # 补班时间可能是 Excel 数字日期(如 46151 -> 2026-05-02)
            if isinstance(supp_raw, (int, float)) and not pd.isna(supp_raw):
                try:
                    base = _date(1899, 12, 30)
                    d = base + _td(days=int(supp_raw))
                    # 检查是否已经添加过(避免重复)
                    already = any(
                        r["holiday_date"] == d for r in results if r.get("holiday_date") == d and r["is_workday"]
                    )
                    if not already:
                        results.append({"holiday_name": name + "补班", "holiday_date": d, "is_workday": True})
                except (ValueError, OverflowError):
                    pass

        return results

    def provide_three_fast_plans(self) -> list[dict[str, object]]:
        """三快计划: 列名[二级分类, 1~3月每月, 4月以后每月]，按月展开。"""
        if not self._paths["plan"]:
            return []
        df = pd.read_excel(self._paths["plan"], engine="openpyxl")
        results: list[dict[str, object]] = []
        for _idx, row in df.iterrows():
            cat_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            early = _safe_float(row.iloc[1]) if len(row) > 1 else 0.0
            late = _safe_float(row.iloc[2]) if len(row) > 2 else 0.0
            if cat_name:
                for m in [1, 2, 3]:
                    results.append({"plan_quarter": f"2026-{m:02d}", "category_name": cat_name, "plan_days": early})
                for m in [4, 5, 6]:
                    results.append({"plan_quarter": f"2026-{m:02d}", "category_name": cat_name, "plan_days": late})
        return results



def _clean_cell(value: object) -> str:
    """清洗单元格值: 去NBSP/去空格/转字符串。"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).replace(chr(0xa0), "").strip()

def _safe_str(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):  # type: ignore[arg-type]
        return ""
    return str(value).strip()


def _safe_str_or_none(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):  # type: ignore[arg-type]
        return None
    s = str(value).strip()
    return None if s.lower() == "nan" or not s else s


def _safe_date(value: object) -> object:
    """将值转为 date 或 None。str -> date, pd.Timestamp -> date, datetime -> date, None -> None。"""
    if value is None or (isinstance(value, float) and pd.isna(value)):  # type: ignore[arg-type]
        return None
    if isinstance(value, pd.Timestamp):
        return value.date()
    from datetime import date as _d
    from datetime import datetime as _dt

    if isinstance(value, _dt):
        return value.date()
    if isinstance(value, str):
        s = value.strip()
        try:
            return _d.fromisoformat(s)
        except ValueError:
            return None
    return value


def _safe_float(value: object) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    try:
        return float(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return 0.0


def _safe_bool(value: object) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    return s in ("true", "1", "yes", "是")


def _safe_int_or_none(value: object) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(value)  # type: ignore[arg-type, call-overload, no-any-return]
    except (ValueError, TypeError):
        return None
