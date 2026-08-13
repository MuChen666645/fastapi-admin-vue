from types import SimpleNamespace

from utils.fastapi_admin import FastApiAdmin


def test_create_three_builds_menu_tree_without_mutating_source() -> None:
    root = SimpleNamespace(menu_id=1, parent_id=0, menu_name="system")
    child = SimpleNamespace(menu_id=2, parent_id=1, menu_name="user")

    tree = FastApiAdmin.create_three(
        [root, child], id_field="menu_id", parent_field="parent_id"
    )

    assert [node["menu_id"] for node in tree] == [1]
    assert [node["menu_id"] for node in tree[0]["children"]] == [2]
    assert not hasattr(root, "children")
    assert not hasattr(child, "children")


def test_create_three_treats_missing_parent_as_root() -> None:
    tree = FastApiAdmin.create_three(
        [{"menu_id": 3, "parent_id": 99, "menu_name": "orphan"}],
        id_field="menu_id",
        parent_field="parent_id",
    )

    assert tree == [
        {
            "menu_id": 3,
            "parent_id": 99,
            "menu_name": "orphan",
            "children": [],
        }
    ]
