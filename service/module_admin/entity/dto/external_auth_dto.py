"""外部身份认证请求和响应模型。"""

from pydantic import BaseModel, Field


class ExternalAuthStartDto(BaseModel):
    """外部登录授权地址。"""

    authorization_url: str = Field(description="外部身份提供商授权地址")


class ExternalAuthCallbackDto(BaseModel):
    """外部登录回调结果。"""

    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="访问令牌有效秒数")
