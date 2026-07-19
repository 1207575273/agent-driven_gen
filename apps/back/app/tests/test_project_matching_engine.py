"""项目匹配引擎单元测试: 清洗 + 分类匹配(纯函数, 无 IO)。"""

from app.services.project_matching_engine import (
    build_category_map,
    clean_project_name,
    match_to_category,
)


class TestCleanProjectName:
    def test_should_trim_spaces(self) -> None:
        assert clean_project_name("  快服务项目  ") == "快服务项目"

    def test_should_remove_q1_prefix(self) -> None:
        assert clean_project_name("Q1 快服务项目") == "快服务项目"

    def test_should_remove_q2_prefix(self) -> None:
        assert clean_project_name("Q2 快服务项目") == "快服务项目"

    def test_should_remove_year_q_prefix(self) -> None:
        assert clean_project_name("2026Q1 快交付项目") == "快交付项目"

    def test_should_remove_2025q1_prefix(self) -> None:
        assert clean_project_name("2025Q1 旧项目") == "旧项目"

    def test_should_remove_prefix_with_dash(self) -> None:
        assert clean_project_name("Q1-快服务项目") == "快服务项目"

    def test_should_remove_prefix_with_underscore(self) -> None:
        assert clean_project_name("Q2_快服务项目") == "快服务项目"

    def test_should_not_alter_name_without_q_prefix(self) -> None:
        assert clean_project_name("日常运营&管理") == "日常运营&管理"

    def test_should_handle_empty_string(self) -> None:
        assert clean_project_name("") == ""

    def test_should_handle_only_spaces(self) -> None:
        assert clean_project_name("   ") == ""


class TestMatchToCategory:
    def test_should_match_exact(self) -> None:
        cat_map = {"快服务项目": 7, "快交付项目": 9}
        assert match_to_category("快服务项目", cat_map) == 7

    def test_should_return_none_for_no_match(self) -> None:
        cat_map = {"快服务项目": 7}
        assert match_to_category("不存在的项目", cat_map) is None

    def test_should_match_compact_no_spaces(self) -> None:
        cat_map = {"快服务项目": 7}
        assert match_to_category("快 服 务 项 目", cat_map) == 7

    def test_should_match_substring_contained(self) -> None:
        cat_map = {"快服务": 7}
        assert match_to_category("快服务迭代项目", cat_map) == 7

    def test_should_match_when_key_contains_name(self) -> None:
        cat_map = {"快服务迭代项目": 7}
        assert match_to_category("快服务", cat_map) == 7

    def test_should_return_none_for_empty_name(self) -> None:
        assert match_to_category("", {"a": 1}) is None


class TestBuildCategoryMap:
    def test_should_build_from_level_3_categories(self) -> None:
        cats: list[dict[str, object]] = [
            {"category_name": "三快类", "category_level": 1, "parent_id": None, "id": 1},
            {"category_name": "快服务", "category_level": 2, "parent_id": 1, "id": 2},
            {"category_name": "快服务迭代", "category_level": 3, "parent_id": 2, "id": 3},
        ]
        result = build_category_map(cats)
        assert result.get("快服务迭代") == 3

    def test_should_include_project_to_category_mapping(self) -> None:
        cats: list[dict[str, object]] = []
        project_map = {"我的项目": 5}
        result = build_category_map(cats, project_map)
        assert result.get("我的项目") == 5

    def test_should_include_level_0_projects_as_map(self) -> None:
        cats: list[dict[str, object]] = [
            {"category_name": "快服务项目", "category_level": 0, "parent_id": 3, "id": None},
        ]
        result = build_category_map(cats)
        assert result.get("快服务项目") == 3
