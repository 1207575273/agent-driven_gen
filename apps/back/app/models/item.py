"""Item 实体与传输契约(SQLModel "全家桶"模式)。

为什么一个业务对象要拆成 5 个类, 而不是一个类走天下?核心动机是
**把"数据库表"和"API 契约"解耦**, 各自的关注点不同:

- 入参不该带 id / 时间戳(那是服务端生成的, 客户端传了也无意义甚至有害);
- 出参要能显式控制"暴露哪些字段", 不能表里有什么就漏什么;
- 更新要支持"只改部分字段", 语义和新增不同。

用一个 Base 抽公共字段, 其余各类按需继承或覆写, 既解耦又不重复维护字段。
团队新增业务表照此在 app/models/ 下扩展, 并在 app/db/base.py import 一次。
"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ItemBase(SQLModel):
    """公共业务字段基类: 新增/更新/读取都要用到的字段集中在此。

    好处是字段与校验规则只写一遍, 改字段只改这里, 不用在 5 个类里同步维护。
    刻意**不含 id / 时间戳**——那些由服务端生成, 属于"表和出参", 不属于"业务输入"。
    """

    name: str = Field(min_length=1, max_length=100, index=True)  # 非空、限长、建索引(常按名查)
    description: str | None = Field(default=None, max_length=500)  # 可空
    quantity: int = Field(default=0, ge=0)  # 非负


class Item(ItemBase, table=True):
    """唯一映射到数据库表的类(table=True), 供落库用。

    在业务字段之上补两类**服务端字段**: 自增主键 id、审计时间戳。
    它们不放进 Base, 正是为了让入参契约(Create/Update)天然拿不到这些字段。
    """

    id: int | None = Field(default=None, primary_key=True)  # 默认 None, 交给数据库自增
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ItemCreate(ItemBase):
    """新增入参: 客户端只提供业务字段, 直接复用 Base 即可(故为空)。

    id 自增、时间戳由服务端打, 都不该由客户端传, 所以这里不加任何字段。
    """


class ItemUpdate(SQLModel):
    """更新入参: 刻意**不继承 Base**, 把每个字段都独立设为可选。

    更新是"部分更新"——客户端只传想改的字段, service 用
    model_dump(exclude_unset=True) 只更新传入项。若继承 Base 会带上 Base 的
    必填与默认值, 破坏"只改传入字段"的语义, 所以这里另起一套全可选字段。
    """

    name: str | None = None
    description: str | None = None
    quantity: int | None = None


class ItemPublic(ItemBase):
    """出参契约: 在业务字段之上, 显式暴露 id 与审计时间戳给前端。

    与 Item(表模型)分开, 是为了**解耦 API 与数据库**: 表以后加内部字段
    (软删标记、租户 id 等)不会自动泄露到接口响应, 出参始终由这个类显式控制。
    """

    id: int
    created_at: datetime
    updated_at: datetime
