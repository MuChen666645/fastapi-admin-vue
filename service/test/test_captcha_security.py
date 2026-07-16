"""Captcha isolation, binding, and attempt-limit tests."""

import json
from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException

from config.env import settings
from module_admin.service.code_service import CodeService
from test.conftest import app
from utils.fastapi_admin import FastApiAdmin


def make_request(ip_address: str = "198.51.100.20") -> SimpleNamespace:
    return SimpleNamespace(
        app=app,
        client=SimpleNamespace(host=ip_address),
        headers={},
    )


def stub_captcha_image(monkeypatch: pytest.MonkeyPatch) -> None:
    async def create_captcha(*args, **kwargs):
        return "data:image/png;base64,test"

    monkeypatch.setattr(
        FastApiAdmin.CaptchaGenerator,
        "create_captcha",
        create_captcha,
    )


def test_captcha_uses_random_id_instead_of_code_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        stub_captcha_image(monkeypatch)
        monkeypatch.setattr(
            FastApiAdmin,
            "create_random_captcha",
            lambda *args, **kwargs: "1234",
        )

        result = await CodeService.get_captcha_img_services(make_request())
        assert result.image == "data:image/png;base64,test"
        assert result.captcha_id != "1234"
        assert len(result.captcha_id) >= 16

        redis_keys = list(app.state.redis._data)
        assert redis_keys == [f"captcha:{result.captcha_id}"]
        assert "1234" not in redis_keys[0]
        payload = json.loads(app.state.redis._data[redis_keys[0]])
        assert "code" not in payload
        assert payload["code_hash"] == CodeService._code_hash(
            result.captcha_id,
            "1234",
        )
        assert payload["attempts"] == 0
        assert payload["ip_hash"] != "198.51.100.20"
        assert await app.state.redis.ttl(redis_keys[0]) == settings.CAPTCHA_TTL_SECONDS

    anyio.run(run)


def test_captcha_is_bound_to_ip_and_consumed_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        stub_captcha_image(monkeypatch)
        monkeypatch.setattr(
            FastApiAdmin,
            "create_random_captcha",
            lambda *args, **kwargs: "1234",
        )
        owner_request = make_request("198.51.100.20")
        other_request = make_request("198.51.100.21")
        captcha = await CodeService.get_captcha_img_services(owner_request)

        with pytest.raises(HTTPException) as mismatch:
            await CodeService.verify_captcha_services(
                captcha.captcha_id,
                "1234",
                other_request,
            )
        assert mismatch.value.status_code == 403

        await CodeService.verify_captcha_services(
            captcha.captcha_id,
            "1234",
            owner_request,
        )
        with pytest.raises(HTTPException) as reused:
            await CodeService.verify_captcha_services(
                captcha.captcha_id,
                "1234",
                owner_request,
            )
        assert reused.value.status_code == 404

    anyio.run(run)


def test_captcha_is_deleted_after_maximum_failed_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        stub_captcha_image(monkeypatch)
        monkeypatch.setattr(
            FastApiAdmin,
            "create_random_captcha",
            lambda *args, **kwargs: "1234",
        )
        request = make_request()
        captcha = await CodeService.get_captcha_img_services(request)

        for attempt in range(1, settings.CAPTCHA_MAX_VERIFY_ATTEMPTS):
            with pytest.raises(HTTPException) as incorrect:
                await CodeService.verify_captcha_services(
                    captcha.captcha_id,
                    "9999",
                    request,
                )
            assert incorrect.value.status_code == 401
            assert str(settings.CAPTCHA_MAX_VERIFY_ATTEMPTS - attempt) in str(
                incorrect.value.detail
            )

        with pytest.raises(HTTPException) as exhausted:
            await CodeService.verify_captcha_services(
                captcha.captcha_id,
                "9999",
                request,
            )
        assert exhausted.value.status_code == 429

        with pytest.raises(HTTPException) as deleted:
            await CodeService.verify_captcha_services(
                captcha.captcha_id,
                "1234",
                request,
            )
        assert deleted.value.status_code == 404

    anyio.run(run)
