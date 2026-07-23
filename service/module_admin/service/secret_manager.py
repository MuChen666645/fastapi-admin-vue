"""版本化 Secret Manager 适配层。"""

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken

from config.env import Settings, settings


class SecretManager:
    """支持环境注入 key ring、兼容旧密文并执行密钥轮换。"""

    PREFIX = "enc:"

    @staticmethod
    def _settings(app_settings: Settings | None = None) -> Settings:
        return app_settings or settings

    @classmethod
    def _keys(cls, app_settings: Settings) -> dict[str, str]:
        raw = app_settings.SECRET_MANAGER_KEYS.strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("SECRET_MANAGER_KEYS 必须是 JSON 对象") from exc
        if not isinstance(data, dict):
            raise ValueError("SECRET_MANAGER_KEYS 必须是 JSON 对象")
        return {str(version): str(value) for version, value in data.items()}

    @classmethod
    def _fernet(cls, version: str, app_settings: Settings) -> Fernet:
        configured = cls._keys(app_settings).get(version)
        if configured:
            return Fernet(configured.encode("ascii"))
        # v1 沿用历史派生规则，保证已有 system_configs 密文可读取。
        suffix = "" if version == "v1" else f":{version}"
        key = base64.urlsafe_b64encode(
            hashlib.sha256((app_settings.SECRET_KEY + suffix).encode()).digest()
        )
        return Fernet(key)

    @classmethod
    def encrypt(
        cls, value: str | None, app_settings: Settings | None = None
    ) -> str | None:
        """使用当前 active version 加密文本。"""
        if value is None:
            return None
        if value.startswith(cls.PREFIX):
            return value
        configured = cls._settings(app_settings)
        version = configured.SECRET_MANAGER_ACTIVE_VERSION
        token = cls._fernet(version, configured).encrypt(value.encode()).decode("ascii")
        return f"{cls.PREFIX}{version}:{token}"

    @classmethod
    def decrypt(
        cls, value: str | None, app_settings: Settings | None = None
    ) -> str | None:
        """解密版本化密文，兼容迁移前的明文值。"""
        if value is None or not value.startswith(cls.PREFIX):
            return value
        try:
            _, version, token = value.split(":", 2)
            configured = cls._settings(app_settings)
            return cls._fernet(version, configured).decrypt(token.encode()).decode()
        except (ValueError, TypeError, KeyError, InvalidToken) as exc:
            raise ValueError("敏感配置无法解密") from exc

    @classmethod
    def rotate(
        cls, value: str | None, app_settings: Settings | None = None
    ) -> str | None:
        """解密旧版本并用当前 active version 重新加密。"""
        return cls.encrypt(cls.decrypt(value, app_settings), app_settings)
