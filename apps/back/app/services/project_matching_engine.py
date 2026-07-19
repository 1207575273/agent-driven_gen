"""项目匹配引擎: 清洗项目名 + 分类匹配。

导入流程专用: 在导入时执行, 结果存入 work_hours.category_id。
"""

import re

# 季度前缀模式: 可选年份(4位) + Q[1-4] + 可选分隔符
_QUARTER_PREFIX_RE = re.compile(r"^(?:\d{4})?Q[1-4]\s*[-_]?\s*")


def clean_project_name(raw: str) -> str:
    """清洗项目名: 去首尾空格 + 去 Q 前缀 + 去 NBSP。

    Args:
        raw: 原始项目名(可能含 "Q1 快服务项目" 等前缀)

    Returns:
        清洗后的项目名
    """
    name = raw.strip()
    # 去掉常见季度前缀: Q1/Q2/Q3/Q4/2025Q1/2026Q2 等
    name = _QUARTER_PREFIX_RE.sub("", name)
    return name.strip()


def match_to_category(
    cleaned_name: str,
    category_map: dict[str, int],
) -> int | None:
    """将清洗后的项目名匹配到三级分类(category_id)。

    Args:
        cleaned_name: 清洗后的项目名
        category_map: {"项目名": category_id} 映射表

    Returns:
        三级分类的 category_id, 匹配失败返回 None
    """
    if not cleaned_name:
        return None
    # 精确匹配
    if cleaned_name in category_map:
        return category_map[cleaned_name]
    # 进一步尝试: 去掉所有空格后匹配(处理 NBSP 残留)
    compact = re.sub(r"\s+", "", cleaned_name)
    if compact in category_map:
        return category_map[compact]
    # 模糊子串匹配(尝试项目名 包含 或 被包含于 category_map 中的 key)
    for key, cid in category_map.items():
        if key in cleaned_name or cleaned_name in key:
            return cid
    return None


def build_category_map(
    categories: list[dict[str, object]],
    project_to_category: dict[str, int] | None = None,
) -> dict[str, int]:
    """构建项目名 -> category_id 的映射表。

    从项目分类数据(含三级分类)和可选的项目-分类映射中构建。

    Args:
        categories: 项目分类 list
        project_to_category: 项目名 -> category_id 的手动映射

    Returns:
        {"项目名": category_id(三级分类id)} 映射
    """
    result: dict[str, int] = {}

    if project_to_category:
        result.update(project_to_category)

    # 同时将 category_name 本身作为可匹配项(有些项目名直接用分类名)
    for cat in categories:
        cat_name = str(cat.get("category_name", ""))
        raw_level = cat.get("category_level", 1)
        cat_level = int(raw_level) if isinstance(raw_level, (int, float, str)) else 1
        if not cat_name or cat_name in result:
            continue
        # Level 0: 项目名 -> parent_id 就是三级分类的 id
        if cat_level == 0:
            parent_id = cat.get("parent_id")
            if parent_id is not None:
                result[cat_name] = int(float(str(parent_id)))
        # Level 3: 分类名作为关键字(token)也可匹配
        elif cat_level == 3:
            raw_id = cat.get("id")
            if raw_id is not None:
                result[cat_name] = int(float(str(raw_id)))

    return result
