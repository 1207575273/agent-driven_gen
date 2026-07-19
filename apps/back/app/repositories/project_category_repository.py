"""ProjectCategory 仓储层(DAO): 项目分类数据访问。"""

from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.project_category import ProjectCategory


class ProjectCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[ProjectCategory]:
        result = await self._session.exec(
            select(ProjectCategory).order_by(col(ProjectCategory.sort_order), col(ProjectCategory.id))
        )
        return result.all()

    async def get_by_level(self, level: int) -> Sequence[ProjectCategory]:
        """获取指定层级的分类。"""
        result = await self._session.exec(
            select(ProjectCategory)
            .where(ProjectCategory.category_level == level)
            .order_by(col(ProjectCategory.sort_order), col(ProjectCategory.id))
        )
        return result.all()

    async def get_by_parent(self, parent_id: int) -> Sequence[ProjectCategory]:
        """获取某节点的直接子节点。"""
        result = await self._session.exec(
            select(ProjectCategory)
            .where(ProjectCategory.parent_id == parent_id)
            .order_by(col(ProjectCategory.sort_order), col(ProjectCategory.id))
        )
        return result.all()

    async def get(self, category_id: int) -> ProjectCategory | None:
        return await self._session.get(ProjectCategory, category_id)

    async def get_by_name(self, category_name: str) -> ProjectCategory | None:
        stmt = select(ProjectCategory).where(ProjectCategory.category_name == category_name)
        result = await self._session.exec(stmt)
        return result.first()

    async def get_major_categories(self) -> list[dict[str, object]]:
        """返回大类列表(level=1), 含 children 子节点。"""
        majors = await self.get_by_level(1)
        result: list[dict[str, object]] = []
        for m in majors:
            children = await self.get_by_parent(m.id)  # type: ignore[arg-type]
            child_list = [
                {"category_id": c.id, "category_name": c.category_name, "category_level": c.category_level}
                for c in children
            ]
            result.append(
                {
                    "category_id": m.id,
                    "category_name": m.category_name,
                    "category_level": m.category_level,
                    "children": child_list,
                }
            )
        return result

    async def get_children(self, category_id: int) -> Sequence[ProjectCategory]:
        """获取某分类的所有子节点。"""
        result = await self._session.exec(
            select(ProjectCategory)
            .where(ProjectCategory.parent_id == category_id)
            .order_by(col(ProjectCategory.sort_order), col(ProjectCategory.id))
        )
        return result.all()

    async def get_by_level3(self) -> Sequence[ProjectCategory]:
        """获取全部三级分类。"""
        return await self.get_by_level(3)
