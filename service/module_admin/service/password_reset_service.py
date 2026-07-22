"""邮箱和短信密码找回服务。"""

import asyncio
import hashlib
import hmac
import secrets
import smtplib
from datetime import timedelta
from email.message import EmailMessage

import httpx
from fastapi import HTTPException, Request
from loguru import logger
from sqlmodel import delete

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.user_do import PasswordResetTokenDo, UserDo
from module_admin.entity.dto.user_dto import (ConfirmPasswordResetRequestDto,
                                              ForgotPasswordRequestDto)
from module_admin.service.user_service import UserService
from utils.fastapi_admin import FastApiAdmin
from utils.time_utils import now_utc8_naive


class PasswordResetNotifier:
    """可配置的邮件和短信通知发送器。"""

    async def send(self, channel: str, destination: str, token: str) -> None:
        """发送一次性找回令牌，不向 API 响应泄露令牌。"""
        if channel == "sms":
            if not settings.PASSWORD_RESET_SMS_WEBHOOK:
                self._development_log(channel, destination, token)
                return
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    settings.PASSWORD_RESET_SMS_WEBHOOK,
                    json={"destination": destination, "token": token},
                )
                response.raise_for_status()
            return

        if not settings.PASSWORD_RESET_EMAIL_ENABLED:
            self._development_log(channel, destination, token)
            return
        if not all(
            (
                settings.SMTP_HOST,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
                settings.SMTP_FROM,
            )
        ):
            raise RuntimeError("SMTP password reset provider is not configured")
        message = EmailMessage()
        message["Subject"] = "密码重置验证码"
        message["From"] = settings.SMTP_FROM
        message["To"] = destination
        message.set_content(f"你的密码重置令牌是：{token}，有效期为 15 分钟。")
        await asyncio.to_thread(self._send_email, message)

    @staticmethod
    def _send_email(message: EmailMessage) -> None:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as smtp:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)

    @staticmethod
    def _development_log(channel: str, destination: str, token: str) -> None:
        if settings.APP_ENV == "development":
            logger.info(
                "开发环境密码找回通知 channel={} destination={} token={}",
                channel,
                destination,
                token,
            )


class PasswordResetService:
    """生成、发送、消费密码找回令牌。"""

    @staticmethod
    def _token_hash(token: str) -> str:
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            token.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    async def request_reset(
        cls,
        data: ForgotPasswordRequestDto,
        request: Request,
    ) -> dict[str, str]:
        """申请密码找回，统一返回结果避免账号枚举。"""
        user = await UserDao.get_user_by_identifier(data.identifier, request)
        if user is None:
            return {"message": "如果账号存在，密码找回通知将发送到已绑定渠道"}
        destination = user.email if data.channel == "email" else user.phone
        if not destination:
            return {"message": "如果账号存在，密码找回通知将发送到已绑定渠道"}

        token = secrets.token_urlsafe(48)
        now = now_utc8_naive()
        expires_at = now + timedelta(seconds=settings.PASSWORD_RESET_TOKEN_TTL_SECONDS)
        mysql = request.state.mysql
        await mysql.execute(
            delete(PasswordResetTokenDo).where(
                PasswordResetTokenDo.user_id == user.id,
                PasswordResetTokenDo.consumed_at.is_(None),
            )
        )
        mysql.add(
            PasswordResetTokenDo(
                user_id=user.id,
                channel=data.channel,
                token_hash=cls._token_hash(token),
                expires_at=expires_at,
            )
        )
        notifier = getattr(request.app.state, "password_reset_notifier", None)
        notifier = notifier or PasswordResetNotifier()
        try:
            await notifier.send(data.channel, destination, token)
        except Exception as exc:
            logger.exception("密码找回通知发送失败")
            raise HTTPException(status_code=503, detail="密码找回通知发送失败") from exc
        return {"message": "如果账号存在，密码找回通知将发送到已绑定渠道"}

    @classmethod
    async def confirm_reset(
        cls,
        data: ConfirmPasswordResetRequestDto,
        request: Request,
    ) -> dict[str, str]:
        """验证令牌后更新密码并撤销全部登录会话。"""
        reset = await UserDao.get_password_reset_token(cls._token_hash(data.token), request)
        now = now_utc8_naive()
        if reset is None or reset.expires_at <= now:
            raise HTTPException(status_code=400, detail="密码找回令牌无效或已过期")
        user = await request.state.mysql.get(UserDo, reset.user_id)
        if user is None:
            raise HTTPException(status_code=400, detail="密码找回令牌无效或已过期")
        await UserService._validate_new_password(data.password, user, request)
        result = await UserDao.update_password_without_scope(
            user.id,
            FastApiAdmin.password_hash(data.password),
            request,
        )
        if result is not None:
            raise HTTPException(status_code=400, detail=result)
        reset.consumed_at = now
        await UserService._record_login(
            request, user.username, "1", "密码找回成功", user.id
        )
        await Auth.revoke_all_user_tokens(request, user.id)
        return {"message": "密码已重置，请重新登录"}
