from module_admin.entity.dto.menu_dto import (
    CreateMenubyIframeDto,
    CreateMenuByRouterDto,
)


def test_menu_visibility_fields_have_database_safe_defaults() -> None:
    router = CreateMenuByRouterDto(
        menu_name="系统管理",
        parent_id=0,
        menu_type="C",
        menu_path="/system",
    )
    iframe = CreateMenubyIframeDto(
        menu_name="监控页面",
        parent_id=1,
        menu_type="I",
        menu_path="/monitor",
        component="IframeView",
    )

    assert router.is_hidden == "0"
    assert router.is_cache == "0"
    assert iframe.is_hidden == "0"
    assert iframe.is_cache == "0"
