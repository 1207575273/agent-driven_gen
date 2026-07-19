"""依赖注入装配: session -> repository -> service。

路由只需声明 `service: XxxServiceDep`, FastAPI 自动构造整条链。
团队新增实体时照此再写一组 get_xxx_repository / get_xxx_service 即可。
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.repositories.data_import_repository import DataImportRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.holiday_repository import HolidayRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.project_category_repository import ProjectCategoryRepository
from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.capacity_audit_service import CapacityAuditService
from app.services.cross_analysis_service import CrossAnalysisService
from app.services.data_import_service import DataImportService
from app.services.drill_down_service import DrillDownService
from app.services.filter_service import FilterService
from app.services.item_service import ItemService
from app.services.system_service import SystemService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ---------- Item ----------
def get_item_repository(session: SessionDep) -> ItemRepository:
    return ItemRepository(session)


ItemRepositoryDep = Annotated[ItemRepository, Depends(get_item_repository)]


def get_item_service(repository: ItemRepositoryDep) -> ItemService:
    return ItemService(repository)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# ---------- System ----------
def get_system_service() -> SystemService:
    return SystemService()


SystemServiceDep = Annotated[SystemService, Depends(get_system_service)]


# ---------- Employee ----------
def get_employee_repository(session: SessionDep) -> EmployeeRepository:
    return EmployeeRepository(session)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]


# ---------- WorkHour ----------
def get_work_hour_repository(session: SessionDep) -> WorkHourRepository:
    return WorkHourRepository(session)


WorkHourRepositoryDep = Annotated[WorkHourRepository, Depends(get_work_hour_repository)]


# ---------- ProjectCategory ----------
def get_project_category_repository(session: SessionDep) -> ProjectCategoryRepository:
    return ProjectCategoryRepository(session)


ProjectCategoryRepositoryDep = Annotated[ProjectCategoryRepository, Depends(get_project_category_repository)]


# ---------- Holiday ----------
def get_holiday_repository(session: SessionDep) -> HolidayRepository:
    return HolidayRepository(session)


HolidayRepositoryDep = Annotated[HolidayRepository, Depends(get_holiday_repository)]


# ---------- ShouldBeCapacity ----------
def get_should_be_capacity_repository(session: SessionDep) -> ShouldBeCapacityRepository:
    return ShouldBeCapacityRepository(session)


ShouldBeCapacityRepositoryDep = Annotated[ShouldBeCapacityRepository, Depends(get_should_be_capacity_repository)]


# ---------- ThreeFastPlan ----------
def get_three_fast_plan_repository(session: SessionDep) -> ThreeFastPlanRepository:
    return ThreeFastPlanRepository(session)


ThreeFastPlanRepositoryDep = Annotated[ThreeFastPlanRepository, Depends(get_three_fast_plan_repository)]


# ---------- DataImport ----------
def get_data_import_repository(session: SessionDep) -> DataImportRepository:
    return DataImportRepository(session)


DataImportRepositoryDep = Annotated[DataImportRepository, Depends(get_data_import_repository)]


# ---------- CapacityAuditService ----------
def get_capacity_audit_service(
    emp_repo: EmployeeRepositoryDep,
    wh_repo: WorkHourRepositoryDep,
    cap_repo: ShouldBeCapacityRepositoryDep,
) -> CapacityAuditService:
    return CapacityAuditService(emp_repo, wh_repo, cap_repo)


CapacityAuditServiceDep = Annotated[CapacityAuditService, Depends(get_capacity_audit_service)]


# ---------- CrossAnalysisService ----------
def get_cross_analysis_service(
    emp_repo: EmployeeRepositoryDep,
    wh_repo: WorkHourRepositoryDep,
    cat_repo: ProjectCategoryRepositoryDep,
    cap_repo: ShouldBeCapacityRepositoryDep,
    plan_repo: ThreeFastPlanRepositoryDep,
) -> CrossAnalysisService:
    return CrossAnalysisService(emp_repo, wh_repo, cat_repo, cap_repo, plan_repo)


CrossAnalysisServiceDep = Annotated[CrossAnalysisService, Depends(get_cross_analysis_service)]


# ---------- DrillDownService ----------
def get_drill_down_service(
    wh_repo: WorkHourRepositoryDep,
    emp_repo: EmployeeRepositoryDep,
    cat_repo: ProjectCategoryRepositoryDep,
) -> DrillDownService:
    return DrillDownService(wh_repo, emp_repo, cat_repo)


DrillDownServiceDep = Annotated[DrillDownService, Depends(get_drill_down_service)]


# ---------- FilterService ----------
def get_filter_service(
    emp_repo: EmployeeRepositoryDep,
    cat_repo: ProjectCategoryRepositoryDep,
) -> FilterService:
    return FilterService(emp_repo, cat_repo)


FilterServiceDep = Annotated[FilterService, Depends(get_filter_service)]


# ---------- DataImportService ----------
def get_data_import_service(repo: DataImportRepositoryDep) -> DataImportService:
    return DataImportService(repo)


DataImportServiceDep = Annotated[DataImportService, Depends(get_data_import_service)]


# 鉴权占位(母版不含鉴权)。团队接入后在此提供:
# async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User: ...
# CurrentUserDep = Annotated[User, Depends(get_current_user)]
