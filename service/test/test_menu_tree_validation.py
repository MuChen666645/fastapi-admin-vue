from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException

from module_admin.dao.menu_dao import MenuDao
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.dto.menu_dto import UpdMenuDto
from module_admin.service.menu_service import MenuService


class FakeScalarResult:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def first(self) -> int | None:
        return self.values[0] if self.values else None


class FakeResult:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.values)


class FakeMenuSession:
    def __init__(
        self,
        menus: list[MenuDo],
        child_ids: list[int] | None = None,
    ) -> None:
        self.menus = {menu.menu_id: menu for menu in menus}
        self.child_ids = child_ids or []
        self.flush_count = 0

    async def get(self, model, menu_id: int) -> MenuDo | None:
        return self.menus.get(menu_id)

    async def execute(self, statement) -> FakeResult:
        return FakeResult(self.child_ids)

    async def flush(self) -> None:
        self.flush_count += 1


def make_menu(
    menu_id: int,
    parent_id: int,
    menu_type: str = "C",
) -> MenuDo:
    return MenuDo(
        menu_id=menu_id,
        menu_name=f"menu-{menu_id}",
        parent_id=parent_id,
        menu_type=menu_type,
    )


def run_update(
    session: FakeMenuSession,
    menu_id: int,
    update: UpdMenuDto,
) -> str | None:
    async def run() -> str | None:
        request = SimpleNamespace(state=SimpleNamespace(mysql=session))
        return await MenuDao.upd_menu_by_id(menu_id, update, request)

    return anyio.run(run)


def test_menu_update_rejects_missing_parent() -> None:
    session = FakeMenuSession([make_menu(1, 0)])

    result = run_update(session, 1, UpdMenuDto(parent_id=999))

    assert result == "父菜单不存在"
    assert session.menus[1].parent_id == 0
    assert session.flush_count == 0


def test_menu_update_rejects_itself_as_parent() -> None:
    session = FakeMenuSession([make_menu(1, 0)])

    result = run_update(session, 1, UpdMenuDto(parent_id=1))

    assert result == "父菜单不能是当前菜单"
    assert session.menus[1].parent_id == 0
    assert session.flush_count == 0


def test_menu_update_rejects_descendant_as_parent() -> None:
    session = FakeMenuSession(
        [
            make_menu(1, 0),
            make_menu(2, 1),
            make_menu(3, 2),
        ]
    )

    result = run_update(session, 1, UpdMenuDto(parent_id=3))

    assert result == "父菜单不能是当前菜单的后代节点"
    assert session.menus[1].parent_id == 0
    assert session.flush_count == 0


def test_menu_update_rejects_button_as_parent() -> None:
    session = FakeMenuSession(
        [
            make_menu(1, 0),
            make_menu(2, 1),
            make_menu(3, 1, menu_type="F"),
        ]
    )

    result = run_update(session, 2, UpdMenuDto(parent_id=3))

    assert result == "按钮不能作为父菜单"
    assert session.menus[2].parent_id == 1
    assert session.flush_count == 0


def test_menu_with_children_cannot_be_changed_to_button() -> None:
    session = FakeMenuSession(
        [make_menu(1, 0), make_menu(2, 1), make_menu(3, 0)],
        child_ids=[2],
    )

    result = run_update(
        session,
        1,
        UpdMenuDto(parent_id=3, menu_type="F"),
    )

    assert result == "存在子菜单的菜单不能修改为按钮"
    assert session.menus[1].parent_id == 0
    assert session.menus[1].menu_type == "C"
    assert session.flush_count == 0


def test_menu_update_accepts_valid_parent() -> None:
    session = FakeMenuSession([make_menu(1, 0), make_menu(2, 1), make_menu(3, 2)])

    result = run_update(session, 3, UpdMenuDto(parent_id=1))

    assert result is None
    assert session.menus[3].parent_id == 1
    assert session.flush_count == 1


def test_menu_update_normalizes_root_parent_to_null() -> None:
    session = FakeMenuSession([make_menu(1, 0), make_menu(2, 1)])

    result = run_update(session, 2, UpdMenuDto(parent_id=0))

    assert result is None
    assert session.menus[2].parent_id is None
    assert session.flush_count == 1


@pytest.mark.parametrize(
    ("dao_result", "expected_status"),
    [
        ("菜单不存在", 404),
        ("父菜单不存在", 400),
        ("父菜单不能是当前菜单", 400),
    ],
)
def test_menu_service_maps_update_errors(
    monkeypatch: pytest.MonkeyPatch,
    dao_result: str,
    expected_status: int,
) -> None:
    async def update_menu(*args, **kwargs):
        return dao_result

    async def get_menu(*args, **kwargs):
        return None

    async def run() -> None:
        monkeypatch.setattr(MenuDao, "upd_menu_by_id", update_menu)
        monkeypatch.setattr(MenuDao, "get_menu_by_id", get_menu)
        with pytest.raises(HTTPException) as exception:
            await MenuService.upd_menu_by_id_services(
                1,
                UpdMenuDto(parent_id=2),
                SimpleNamespace(),
            )
        assert exception.value.status_code == expected_status
        assert exception.value.detail == dao_result

    anyio.run(run)
