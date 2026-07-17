"""依赖注入装配: session -> repository -> service。

路由只需声明 `service: XxxServiceDep`, FastAPI 自动构造整条链。
团队新增实体时照此再写一组 get_xxx_repository / get_xxx_service 即可。
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.dashboard_service import DashboardService
from app.services.department_service import DepartmentService
from app.services.filter_service import FilterService
from app.services.item_service import ItemService
from app.services.project_service import ProjectService
from app.services.role_service import RoleService
from app.services.system_service import SystemService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_item_repository(session: SessionDep) -> ItemRepository:
    return ItemRepository(session)


ItemRepositoryDep = Annotated[ItemRepository, Depends(get_item_repository)]


def get_item_service(repository: ItemRepositoryDep) -> ItemService:
    return ItemService(repository)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# 系统指标: 无 session/repository, 直接构造 service。
def get_system_service() -> SystemService:
    return SystemService()


SystemServiceDep = Annotated[SystemService, Depends(get_system_service)]


# ---------------------------------------------------------------------------
# 产能分析系统依赖注入
# ---------------------------------------------------------------------------


def get_work_hour_repository(session: SessionDep) -> WorkHourRepository:
    return WorkHourRepository(session)


WorkHourRepositoryDep = Annotated[WorkHourRepository, Depends(get_work_hour_repository)]


def get_employee_repository(session: SessionDep) -> EmployeeRepository:
    return EmployeeRepository(session)


EmployeeRepositoryDep = Annotated[EmployeeRepository, Depends(get_employee_repository)]


def get_dashboard_service(wh_repo: WorkHourRepositoryDep) -> DashboardService:
    return DashboardService(wh_repo)


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]


def get_project_service(wh_repo: WorkHourRepositoryDep) -> ProjectService:
    return ProjectService(wh_repo)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


def get_department_service(wh_repo: WorkHourRepositoryDep, emp_repo: EmployeeRepositoryDep) -> DepartmentService:
    return DepartmentService(wh_repo, emp_repo)


DepartmentServiceDep = Annotated[DepartmentService, Depends(get_department_service)]


def get_role_service(wh_repo: WorkHourRepositoryDep) -> RoleService:
    return RoleService(wh_repo)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]


def get_filter_service(wh_repo: WorkHourRepositoryDep, emp_repo: EmployeeRepositoryDep) -> FilterService:
    return FilterService(wh_repo, emp_repo)


FilterServiceDep = Annotated[FilterService, Depends(get_filter_service)]


# 鉴权占位(母版不含鉴权)。团队接入后在此提供:
# async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User: ...
# CurrentUserDep = Annotated[User, Depends(get_current_user)]
