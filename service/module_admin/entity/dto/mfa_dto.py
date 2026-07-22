"""多因素认证请求和响应模型。"""

from pydantic import BaseModel, Field


class MfaSetupDto(BaseModel):
    """MFA 初始化结果，仅在初始化时返回恢复码。"""

    secret: str = Field(description="MFA 密钥")
    otpauth_uri: str = Field(description="TOTP 注册 URI")
    recovery_codes: list[str] = Field(description="一次性恢复码")


class MfaCodeDto(BaseModel):
    """MFA 验证码请求模型。"""

    code: str = Field(min_length=6, max_length=32, description="MFA 验证码或恢复码")
