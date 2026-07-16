"""Captcha request and response DTOs."""

from pydantic import BaseModel, ConfigDict, Field


class CaptchaImageDto(BaseModel):
    """Captcha identifier and rendered image."""

    model_config = ConfigDict(from_attributes=True)

    captcha_id: str = Field(description="验证码ID")
    image: str = Field(description="Base64验证码图片")
