""" Code Controller Model."""

from fastapi import APIRouter, FastAPI, Request, Query
from module_admin.entity.dto.code_dto import CaptchaImageDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.code_service import CodeService
from config.env import settings
from config.rate_limit import limiter


class CodeController(APIRouter):
    """Code Controller Class."""

    code = APIRouter(prefix="/captcha", tags=["验证码模块"])

    def __init__(self, app: FastAPI):
        """初始化方法."""
        super().__init__()
        self.app = app

    @staticmethod
    @code.get(
        "/image",
        summary="获取图形验证码",
        responses={200: {"model": ApiResponseDto[CaptchaImageDto]}},
    )
    @limiter.limit(settings.RATE_LIMIT_CAPTCHA)
    async def get_captcha_img(request: Request):
        """获取图形验证码."""
        return await CodeService.get_captcha_img_services(request)

    @staticmethod
    @code.get(
        "/number",
        summary="已停用的数字验证码接口",
        deprecated=True,
        responses={410: {"model": ApiResponseDto[None]}},
    )
    async def get_captcha_num(request: Request):
        """Reject requests to the insecure plaintext captcha endpoint."""
        return await CodeService.get_captcha_num_services(request)

    @staticmethod
    @code.get(
        "/verify",
        summary="校验并消费验证码",
        responses={200: {"model": ApiResponseDto[None]}},
    )
    @limiter.limit(settings.RATE_LIMIT_CAPTCHA)
    async def verify_captcha(
        request: Request,
        captcha_id: str = Query(
            min_length=16,
            max_length=128,
            description="验证码ID",
        ),
        code: str = Query(description="验证码"),
    ):
        """校验并消费验证码."""
        return await CodeService.verify_captcha_services(captcha_id, code, request)
