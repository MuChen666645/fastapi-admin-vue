"""验证码请求和响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


class CaptchaImageDto(BaseModel):
    """验证码标识和渲染后的图片。"""

    model_config = ConfigDict(from_attributes=True)

    captcha_id: str = Field(description="验证码ID")
    image: str = Field(description="Base64验证码图片")
