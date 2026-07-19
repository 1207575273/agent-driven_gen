"""CLI 导入脚本: 离线导入 Excel 数据到 SQLite。

用法:
  cd apps/back
  uv run python scripts/import_data.py --work-hour data/工时明细.xlsx --roster data/花名册.xlsx \
    --category data/项目分类.xlsx --holiday data/节假日.xlsx --plan data/三快计划.xlsx

依赖关系:
  - 数据源抽象层(DataSourceProvider, ExcelDataSourceProvider)
  - DataImportService 编排导入流程
  - 母版数据库 session(需在项目根目录运行)
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.datasources.excel_provider import ExcelDataSourceProvider
from app.db.session import async_session_factory
from app.repositories.data_import_repository import DataImportRepository
from app.services.data_import_service import DataImportService


async def main() -> None:
    parser = argparse.ArgumentParser(description="产能分析系统数据导入脚本")
    parser.add_argument("--work-hour", required=True, help="工时明细 Excel 路径")
    parser.add_argument("--roster", required=True, help="花名册 Excel 路径")
    parser.add_argument("--category", required=True, help="项目分类 Excel 路径")
    parser.add_argument("--holiday", required=True, help="节假日 Excel 路径")
    parser.add_argument("--plan", default=None, help="三快计划 Excel 路径(可选)")
    args = parser.parse_args()

    provider = ExcelDataSourceProvider(
        work_hour_path=args.work_hour,
        roster_path=args.roster,
        category_path=args.category,
        holiday_path=args.holiday,
        plan_path=args.plan,
    )

    async with async_session_factory() as session:
        try:
            repo = DataImportRepository(session)
            service = DataImportService(repo)
            result = await service.import_all(provider)

            stats = result.get("stats", {})
            print("=" * 60)
            print("  产能分析系统数据导入结果")
            print("=" * 60)

            if result.get("success"):
                print("  [PASS] 导入成功")
            else:
                print(f"  [FAIL] 导入失败: {result.get('error')}")

            if isinstance(stats, dict):
                print(f"  花名册:     {stats.get('employees_imported', 0)} 人")
                print(f"  工时明细:   {stats.get('work_hours_imported', 0)} 条")
                print(f"  项目分类:   {stats.get('categories_imported', 0)} 个")
                print(f"  节假日:     {stats.get('holidays_imported', 0)} 条")
                print(f"  应有产能:   {stats.get('capacity_records_created', 0)} 条")
                print(f"  三快计划:   {stats.get('plans_imported', 0)} 条")
                print(f"  人员匹配率: {stats.get('employee_match_rate', 0)}%")
                print(f"  项目匹配率: {stats.get('project_match_rate', 0)}%")

                unmatched = stats.get("unmatched_projects", [])
                if isinstance(unmatched, list) and unmatched:
                    print(f"  未匹配项目: {len(unmatched)} 个")
                    for proj in unmatched[:20]:
                        print(f"    - {proj}")
                    if len(unmatched) > 20:
                        print(f"    ... 共 {len(unmatched)} 个")

                errors = stats.get("errors", [])
                if isinstance(errors, list) and errors:
                    print(f"  错误: {errors}")

                unmatched = stats.get("unmatched_projects", [])
                if isinstance(unmatched, list) and unmatched:
                    print(f"  未匹配项目: {len(unmatched)} 个")
                    for proj in unmatched[:20]:
                        print(f"    - {proj}")
                    if len(unmatched) > 20:
                        print(f"    ... 共 {len(unmatched)} 个")

                errors = stats.get("errors", [])
                if isinstance(errors, list) and errors:
                    print(f"  错误: {errors}")

            await session.commit()
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"[FAIL] 导入异常: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
