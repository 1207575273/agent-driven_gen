"""数据导入路由(薄控制器): 上传 Excel 文件全量导入 + 重新匹配分类。"""

import os
import tempfile
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, File, UploadFile

from app.api.deps import DataImportServiceDep

router = APIRouter(prefix="/data-import", tags=["data-import"])

_FILE_DEFAULT = File(...)
_FILE_OPTIONAL = File(default=None)


def _save_upload(upload: UploadFile, field: str) -> str:
    """保存上传文件到临时目录, 返回路径。统一写 .xlsx 扩展名。"""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, f"{field}.xlsx")
    # 同步方式写入
    content = upload.file.read()  # UploadFile.file 是 SpooledTemporaryFile
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


@router.post("/import")
async def import_data(
    service: DataImportServiceDep,
    work_hour_file: UploadFile = _FILE_DEFAULT,
    roster_file: UploadFile = _FILE_DEFAULT,
    project_category_file: UploadFile = _FILE_DEFAULT,
    holiday_file: UploadFile = _FILE_DEFAULT,
    three_fast_plan_file: UploadFile | None = _FILE_OPTIONAL,
) -> dict[str, Any]:
    """全量导入: 上传 Excel 文件, 清空旧数据后重新导入。"""
    saved_paths: list[str] = []

    try:
        wh_path = _save_upload(work_hour_file, "work_hour")
        saved_paths.append(wh_path)
        roster_path = _save_upload(roster_file, "roster")
        saved_paths.append(roster_path)
        cat_path = _save_upload(project_category_file, "category")
        saved_paths.append(cat_path)
        hol_path = _save_upload(holiday_file, "holiday")
        saved_paths.append(hol_path)

        plan_path: str | None = None
        if three_fast_plan_file:
            plan_path = _save_upload(three_fast_plan_file, "plan")
            saved_paths.append(plan_path)

        from app.datasources.excel_provider import ExcelDataSourceProvider

        provider = ExcelDataSourceProvider(
            work_hour_path=wh_path,
            roster_path=roster_path,
            category_path=cat_path,
            holiday_path=hol_path,
            plan_path=plan_path,
        )

        result = await service.import_all(provider)
        return result

    finally:
        for p in saved_paths:
            with suppress(OSError):
                os.remove(p)


@router.post("/rematch-categories")
async def rematch_categories(service: DataImportServiceDep) -> dict[str, Any]:
    """重新匹配项目分类(不重新导入数据)。"""
    return await service.rematch_categories()