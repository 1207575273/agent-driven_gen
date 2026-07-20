"""通用分页信封: 列表接口统一出参形态。

团队新增实体的列表接口照此复用: `response_model=Page[XxxPublic]`。
"""

from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    total: int  # 满足条件的总条数(与分页无关)
    limit: int  # 本次返回上限
    offset: int  # 本次偏移
