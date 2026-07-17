"""汇总所有 ORM 模型, 供 Alembic env.py 与建表逻辑扫描 SQLModel.metadata。

团队新增实体后, 在此 import 一次即可让迁移/建表识别到。
"""

from sqlmodel import SQLModel

from app.models.employee import Employee  # noqa: F401  仅为注册元数据
from app.models.item import Item  # noqa: F401  仅为注册元数据
from app.models.work_hour import WorkHour  # noqa: F401  仅为注册元数据

metadata = SQLModel.metadata
