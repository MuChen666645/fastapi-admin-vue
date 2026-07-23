"""应用配置和环境文件选择。"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 所有环境文件都相对于服务项目根目录解析，避免依赖当前工作目录。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
EnvironmentName = Literal["development", "staging", "production"]
# 允许的部署环境名称，新增环境时需要同时增加对应的配置文件。
ENVIRONMENT_NAMES = {"development", "staging", "production"}
# 没有环境文件时允许直接注入进程的最小配置集合。
REQUIRED_ENVIRONMENT_VARIABLES = {
    "MYSQL_HOST",
    "MYSQL_USERNAME",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASES",
    "REDIS_HOST",
    "SECRET_KEY",
    "ACCESS_KEY_ID",
    "ACCESSKEY_SECRET",
}
# 非开发环境禁止使用这些常见的示例密钥片段。
PLACEHOLDER_SECRET_MARKERS = (
    "change-me",
    "change_me",
    "replace",
    "your_",
    "example",
    "dev-only",
    "fastapi",
)


def _resolve_environment() -> EnvironmentName:
    """在加载环境文件前解析部署配置档案。"""
    raw_environment = os.getenv("APP_ENV", "development").strip().lower()
    if raw_environment not in ENVIRONMENT_NAMES:
        supported = ", ".join(sorted(ENVIRONMENT_NAMES))
        raise RuntimeError(
            f"APP_ENV must be one of {supported}; got {raw_environment!r}"
        )
    return raw_environment  # type: ignore[return-value]


def _resolve_environment_file(environment: EnvironmentName) -> Path:
    """返回环境配置文件，开发环境兼容旧版 `.env` 回退路径。"""
    environment_file = PROJECT_ROOT / f".env.{environment}"
    if environment_file.exists():
        return environment_file
    if environment == "development":
        legacy_file = PROJECT_ROOT / ".env"
        if legacy_file.exists():
            return legacy_file
    raise RuntimeError(
        f"Missing configuration file {environment_file}. "
        f"Copy the matching .example file before starting the service."
    )


class Settings(BaseSettings):
    """从选定环境加载的类型化应用配置。"""

    class HttpResponses(BaseModel):
        """默认错误响应元数据。"""

        code: int
        message: str
        data: Any

    # 该引导默认值用于选择首个环境配置文件。
    APP_ENV: EnvironmentName = "development"

    # FastAPI 应用元数据和统一错误响应模型。
    DEBUG: bool
    TITLE: str = Field(min_length=1)
    SUMMARY: str = Field(min_length=1)
    VERSION: str = Field(min_length=1)
    OPENAPI_URL: str = Field(min_length=1)
    API_V1_PREFIX: str = Field(default="/api/v1", min_length=1)
    DOCS_AUTH_TOKEN: str = ""
    METRICS_AUTH_TOKEN: str = ""
    # 响应模型属于 API 合约，不属于部署参数。
    RESPONSES: dict[int, dict[str, str | type]] = {
        422: {"description": "Validation Error", "model": HttpResponses},
        401: {"description": "Token Error", "model": HttpResponses},
    }

    # MySQL 连接参数；字段名保持与部署环境文件一致。
    MYSQL_HOST: str = Field(min_length=1)
    MYSQL_POST: int = Field(gt=0, le=65535)
    MYSQL_USERNAME: str = Field(min_length=1)
    MYSQL_PASSWORD: str = Field(min_length=1)
    MYSQL_DATABASES: str = Field(min_length=1)
    TIMEZONE: str = Field(min_length=1)

    # Redis 连接参数；Redis 同时承载验证码、Token 和限流状态。
    REDIS_HOST: str = Field(min_length=1)
    REDIS_POST: int = Field(gt=0, le=65535)
    REDIS_PASSWORD: str
    REDIS_USERNAME: str
    REDIS_DB: int = Field(ge=0)

    # JWT 与 RBAC 配置；数据库版本跟随迁移头，不允许部署覆盖。
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(gt=0)
    ADMIN_ROLE_CODE: str = Field(min_length=1)
    DEFAULT_TENANT_ID: int = Field(default=1, gt=0)
    # 该值必须跟随迁移头，不能由部署配置覆盖。
    DATABASE_SCHEMA_VERSION: str = "0024_password_reset_tenant_permissions"

    # 限流、验证码和登录失败锁定策略。
    RATE_LIMIT_DEFAULT: str = Field(min_length=1)
    RATE_LIMIT_LOGIN: str = Field(min_length=1)
    RATE_LIMIT_CAPTCHA: str = Field(min_length=1)
    RATE_LIMIT_REFRESH_TOKEN: str = Field(default="30/minute", min_length=1)
    RATE_LIMIT_PASSWORD_RESET: str = Field(default="5/minute", min_length=1)
    RATE_LIMIT_EXTERNAL_AUTH: str = Field(default="10/minute", min_length=1)
    CAPTCHA_TTL_SECONDS: int = Field(gt=0)
    CAPTCHA_MAX_VERIFY_ATTEMPTS: int = Field(gt=0)
    LOGIN_MAX_FAILED_ATTEMPTS: int = Field(gt=0)
    LOGIN_IP_LOCK_SECONDS: int = Field(gt=0)
    LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_ACCOUNT_LOCK_SECONDS: int = Field(default=900, gt=0)
    PASSWORD_MIN_LENGTH: int = Field(default=12, ge=8, le=128)
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_HISTORY_COUNT: int = Field(default=5, ge=0, le=20)
    PASSWORD_MAX_AGE_DAYS: int = Field(default=90, ge=0)
    PASSWORD_FORCE_CHANGE_ON_CREATE: bool = True
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, gt=0, le=365)
    MFA_ISSUER: str = Field(default="FastAPI Admin", min_length=1, max_length=100)
    PASSWORD_RESET_TOKEN_TTL_SECONDS: int = Field(default=900, gt=0)
    PASSWORD_RESET_EMAIL_ENABLED: bool = False
    PASSWORD_RESET_SMS_WEBHOOK: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = Field(default=465, gt=0, le=65535)
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    READINESS_TIMEOUT_SECONDS: float = Field(gt=0)

    # 阿里云 OSS
    ACCESS_KEY_ID: str = Field(min_length=1)
    ACCESSKEY_SECRET: str = Field(min_length=1)
    OSS_ENDPOINT: str = Field(title="OSS 服务地址", default="")
    OSS_BUCKET: str = Field(title="OSS 存储桶", default="")
    OSS_PREFIX: str = Field(title="OSS 对象前缀", default="uploads")

    # 文件存储
    FILE_STORAGE_BACKEND: Literal["local", "oss"] = Field(
        title="文件存储后端", default="local"
    )
    FILE_UPLOAD_DIR: str = Field(title="本地文件目录", default="uploads")
    FILE_MAX_SIZE_BYTES: int = Field(
        title="文件大小上限", default=10 * 1024 * 1024, gt=0
    )
    FILE_PRESIGN_TTL_SECONDS: int = Field(title="预签名有效期", default=300, gt=0)
    FILE_CONTENT_SNIFF_ENABLED: bool = True
    FILE_VIRUS_SCAN_ENABLED: bool = False
    FILE_REDACTION_ENABLED: bool = False
    FILE_CHUNK_TTL_SECONDS: int = Field(default=86400, gt=0)
    FILE_SENSITIVE_PATTERNS: list[str] = Field(
        default=[
            r"(?<!\d)1[3-9]\d{9}(?!\d)",
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            r"(?<!\d)\d{15,19}(?!\d)",
        ]
    )
    CLAMAV_HOST: str = "clamav"
    CLAMAV_PORT: int = Field(default=3310, gt=0, le=65535)
    FILE_ALLOWED_EXTENSIONS: list[str] = Field(
        title="允许的文件扩展名",
        default=[
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".zip",
        ],
    )

    # 定时任务
    SCHEDULER_ENABLED: bool = Field(title="是否启用定时任务", default=False)
    SCHEDULER_TIMEZONE: str = Field(title="定时任务时区", default="Asia/Shanghai")
    SCHEDULER_DEFAULT_TIMEOUT_SECONDS: int = Field(default=300, gt=0)
    SCHEDULER_LOCK_TTL_SECONDS: int = Field(default=900, gt=0)
    SCHEDULER_DEFAULT_MAX_RETRIES: int = Field(default=0, ge=0, le=10)
    SCHEDULER_WORKER_MODE: Literal["inline", "queue"] = "inline"

    # 网络访问策略；非开发环境必须显式收紧主机和跨域范围。
    HOSTS: list[str]
    TRUSTED_PROXIES: list[str]
    ORIGINS: list[str]
    MEDOTHS: list[str]
    HEADERS: list[str]
    CREDENTIALS: bool
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "fastapi-admin"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_EXPORTER_OTLP_HEADERS: str = ""
    LOG_RETENTION_DAYS: int = Field(default=30, gt=0)
    ALERT_WEBHOOK_URL: str = ""
    NOTIFICATION_WEBHOOK_URL: str = ""
    NOTIFICATION_SMS_WEBHOOK: str = ""
    NOTIFICATION_RETRY_MAX_ATTEMPTS: int = Field(default=5, ge=1, le=20)
    NOTIFICATION_RETRY_BASE_SECONDS: int = Field(default=30, gt=0)
    BACKUP_DIR: str = "backups"
    BACKUP_ENCRYPTION_KEY: str = ""
    BACKUP_REHEARSAL_DATABASE: str = ""
    BACKUP_RETENTION_DAYS: int = Field(default=30, gt=0)
    BACKUP_TIMEOUT_SECONDS: int = Field(default=900, gt=0)
    EXPORT_WORKER_ENABLED: bool = True
    EXPORT_POLL_SECONDS: int = Field(default=2, gt=0)
    EXPORT_TASK_TTL_SECONDS: int = Field(default=86400, gt=0)
    SECRET_MANAGER_ACTIVE_VERSION: str = Field(default="v1", min_length=1)
    SECRET_MANAGER_KEYS: str = ""
    WORKER_ENABLED: bool = False
    TASK_QUEUE_STREAM: str = "fastapi:tasks"
    TASK_QUEUE_GROUP: str = "fastapi-workers"
    TASK_WORKER_CONSUMER: str = ""
    TASK_HANDLER_MODULE: str = "module_admin.service.task_handlers"
    TASK_HEARTBEAT_SECONDS: int = Field(default=15, gt=0)
    TASK_LOCK_RENEW_SECONDS: int = Field(default=30, gt=0)
    OIDC_ENABLED: bool = False
    OIDC_AUTHORIZATION_URL: str = ""
    OIDC_TOKEN_URL: str = ""
    OIDC_USERINFO_URL: str = ""
    OIDC_CLIENT_ID: str = ""
    OIDC_CLIENT_SECRET: str = ""
    OIDC_REDIRECT_URI: str = ""
    OIDC_SCOPES: str = "openid profile email"
    OIDC_ISSUER: str = ""
    OIDC_AUDIENCE: str = ""
    OIDC_JWKS_URL: str = ""
    LDAP_ENABLED: bool = False
    LDAP_SERVER_URL: str = ""
    LDAP_BASE_DN: str = ""
    LDAP_BIND_DN: str = ""
    LDAP_BIND_PASSWORD: str = ""
    LDAP_USER_FILTER: str = "(uid={username})"

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="before")
    @classmethod
    def load_secret_files(cls, values: Any) -> Any:
        """支持 Docker/Kubernetes Secret 通过 *_FILE 注入，避免密钥进入环境变量。"""
        data = dict(values or {})
        secret_fields = (
            "MYSQL_PASSWORD",
            "MYSQL_ROOT_PASSWORD",
            "MYSQL_USERNAME",
            "REDIS_PASSWORD",
            "REDIS_USERNAME",
            "SECRET_KEY",
            "ACCESS_KEY_ID",
            "ACCESSKEY_SECRET",
            "BACKUP_ENCRYPTION_KEY",
            "SMTP_PASSWORD",
            "PASSWORD_RESET_SMS_WEBHOOK",
            "OIDC_CLIENT_SECRET",
            "LDAP_BIND_PASSWORD",
            "ALERT_WEBHOOK_URL",
            "NOTIFICATION_WEBHOOK_URL",
            "NOTIFICATION_SMS_WEBHOOK",
            "DOCS_AUTH_TOKEN",
            "METRICS_AUTH_TOKEN",
            "SECRET_MANAGER_KEYS",
        )
        for field in secret_fields:
            file_value = data.get(f"{field}_FILE") or os.getenv(f"{field}_FILE")
            if not file_value:
                continue
            path = Path(str(file_value))
            if path.is_file():
                data[field] = path.read_text(encoding="utf-8").strip()
        return data

    @model_validator(mode="after")
    def validate_environment_security(self) -> "Settings":
        """拒绝共享环境使用开发默认值。"""
        if self.APP_ENV == "development":
            return self

        secret_values = {
            "SECRET_KEY": self.SECRET_KEY,
            "MYSQL_PASSWORD": self.MYSQL_PASSWORD,
            "REDIS_PASSWORD": self.REDIS_PASSWORD,
            "ACCESS_KEY_ID": self.ACCESS_KEY_ID,
            "ACCESSKEY_SECRET": self.ACCESSKEY_SECRET,
        }
        placeholder_values = [
            name
            for name, value in secret_values.items()
            if any(marker in value.casefold() for marker in PLACEHOLDER_SECRET_MARKERS)
        ]
        if len(self.SECRET_KEY) < 32 or placeholder_values:
            fields = ", ".join(placeholder_values or ["SECRET_KEY"])
            raise ValueError(
                "Generated non-placeholder secrets are required outside "
                f"development: {fields}"
            )
        if self.DEBUG:
            raise ValueError("DEBUG must be false outside development")
        if "*" in self.HOSTS or "*" in self.ORIGINS or "*" in self.HEADERS:
            raise ValueError(
                "HOSTS, ORIGINS, and HEADERS must be restricted outside development"
            )
        if not self.REDIS_PASSWORD:
            raise ValueError("REDIS_PASSWORD is required outside development")
        if not self.DOCS_AUTH_TOKEN or not self.METRICS_AUTH_TOKEN:
            raise ValueError(
                "DOCS_AUTH_TOKEN and METRICS_AUTH_TOKEN are required outside development"
            )
        if self.FILE_STORAGE_BACKEND == "oss" and (
            not self.OSS_ENDPOINT or not self.OSS_BUCKET
        ):
            raise ValueError("OSS_ENDPOINT and OSS_BUCKET are required for OSS storage")
        if self.OIDC_ENABLED and not all(
            (self.OIDC_ISSUER, self.OIDC_AUDIENCE, self.OIDC_JWKS_URL)
        ):
            raise ValueError(
                "OIDC_ISSUER, OIDC_AUDIENCE, and OIDC_JWKS_URL are required "
                "when OIDC is enabled"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """根据 APP_ENV 和对应环境文件加载配置。"""
    environment = _resolve_environment()
    try:
        environment_file = _resolve_environment_file(environment)
    except RuntimeError:
        if not REQUIRED_ENVIRONMENT_VARIABLES.issubset(os.environ):
            raise
        environment_file = None
    return Settings(_env_file=environment_file)


settings = get_settings()
