---
name: sqlmodel-mypy-strict-patterns
description: SQLModel 与 mypy strict 模式的已知摩擦及最小化规避方案
metadata:
  type: reference
---

## 核心摩擦

1. **`select()` 多参数 overload**: SQLModel 的 `select()` 返回类型与 SQLAlchemy 的 `Select` 泛型不完全兼容,尤其 3+ 列时 overload 匹配失败 -> `# type: ignore[call-overload]`
2. **`InstrumentedAttribute` 比较**: `Employee.is_outsourced == 1` 在 mypy 看来返回 `bool`,但运行时是 SQL Expression。`or_()` 和 `.where()` 需要 `# type: ignore[arg-type]`
3. **`.isnot(None)` / `.is_(None)`**: 对 nullable Column,直接用 `col()` 包装: `col(Employee.role).isnot(None)` 而非 `Employee.role.isnot(None)`
4. **聚合查询 base 变量**: 所有 base 变量用 `Any` 类型而非具体的 `Select[tuple[...]]`,因为 SQLModel 的 select 类型与 sqlalchemy 不一致

**Why:** SQLModel 设计上重用了 SQLAlchemy 的类型,但 mypy strict 追求精确类型推断,两者的类型系统边界不一致。完全消除摩擦需要项目级类型存根,不划算。

**How to apply:** 新增聚合仓储方法时,base 变量用 `Any`,比较表达式中用 `col()` 包装 nullable 列,`or_()` 和 `.where()` 仅对已知摩擦点加 `# type: ignore` 而非整文件关闭检查。
