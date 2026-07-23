"""通知渠道投递和失败重试服务。"""

import asyncio
import smtplib
from datetime import timedelta
from email.message import EmailMessage

import httpx
from fastapi import Request
from loguru import logger
from sqlmodel import select

from config.env import Settings, settings
from module_admin.dao.tenant_scope import tenant_member_clause
from module_admin.entity.do.notice_do import NoticeDo
from module_admin.entity.do.notification_do import NotificationDeliveryDo
from module_admin.entity.do.tenant_do import TenantMemberDo
from module_admin.entity.do.user_do import UserDo
from utils.time_utils import now_utc8_naive


class NotificationService:
    """创建投递任务，并以有限重试次数发送外部通知。"""

    CHANNELS = {"inbox", "webhook", "email", "sms"}

    @classmethod
    async def enqueue(cls, notice: NoticeDo, data, request: Request) -> int:
        """为公告收件人建立渠道投递记录。"""
        channels = set(data.delivery_channels or ["inbox"]) & cls.CHANNELS
        if not channels:
            raise ValueError("至少需要一个有效通知渠道")
        recipient_ids = list(dict.fromkeys(data.recipient_user_ids))
        if not recipient_ids:
            result = await request.state.mysql.execute(
                select(UserDo.id).where(
                    tenant_member_clause(UserDo, notice.tenant_id),
                    UserDo.status == "1",
                    UserDo.deleted_at.is_(None),
                )
            )
            recipient_ids = list(result.scalars().all())
        count = 0
        for user_id in recipient_ids:
            user_result = await request.state.mysql.execute(
                select(UserDo).where(
                    UserDo.id == user_id,
                    tenant_member_clause(UserDo, notice.tenant_id),
                    UserDo.status == "1",
                    UserDo.deleted_at.is_(None),
                )
            )
            user = user_result.scalars().first()
            if user is None:
                continue
            for channel in channels:
                status = "delivered" if channel == "inbox" else "pending"
                request.state.mysql.add(
                    NotificationDeliveryDo(
                        tenant_id=notice.tenant_id,
                        notice_id=notice.id,
                        user_id=user.id,
                        channel=channel,
                        destination=cls._destination(channel, user),
                        status=status,
                        delivered_at=(
                            now_utc8_naive() if status == "delivered" else None
                        ),
                    )
                )
                count += 1
        return count

    @staticmethod
    def _destination(channel: str, user: UserDo) -> str | None:
        if channel == "email":
            return user.email
        if channel == "sms":
            return user.phone
        return None

    @classmethod
    async def deliver_pending(
        cls, session_factory, app_settings: Settings | None = None, limit: int = 50
    ) -> int:
        """发送到期投递记录并按指数退避安排重试。"""
        app_settings = app_settings or settings
        now = now_utc8_naive()
        async with session_factory() as session:
            result = await session.execute(
                select(NotificationDeliveryDo)
                .join(
                    NoticeDo,
                    NotificationDeliveryDo.notice_id == NoticeDo.id,
                )
                .join(UserDo, NotificationDeliveryDo.user_id == UserDo.id)
                .join(
                    TenantMemberDo,
                    (TenantMemberDo.user_id == UserDo.id)
                    & (TenantMemberDo.tenant_id == NotificationDeliveryDo.tenant_id),
                )
                .where(
                    NotificationDeliveryDo.status == "pending",
                    NotificationDeliveryDo.next_attempt_at <= now,
                    NotificationDeliveryDo.tenant_id == NoticeDo.tenant_id,
                    TenantMemberDo.status == "1",
                    TenantMemberDo.deleted_at.is_(None),
                    UserDo.status == "1",
                    UserDo.deleted_at.is_(None),
                )
                .order_by(NotificationDeliveryDo.id)
                .limit(limit)
            )
            items = list(result.scalars().all())
            delivered = 0
            for item in items:
                notice = await session.get(NoticeDo, item.notice_id)
                user = await session.get(UserDo, item.user_id)
                try:
                    if notice is None or user is None:
                        raise ValueError("通知或用户不存在")
                    await cls._deliver(item, notice, user, app_settings)
                except Exception as exc:
                    item.attempts += 1
                    item.last_error = str(exc)[:1000]
                    if item.attempts >= app_settings.NOTIFICATION_RETRY_MAX_ATTEMPTS:
                        item.status = "failed"
                    else:
                        delay = app_settings.NOTIFICATION_RETRY_BASE_SECONDS * (
                            2 ** min(item.attempts - 1, 8)
                        )
                        item.next_attempt_at = now + timedelta(seconds=delay)
                    logger.warning("通知投递失败", delivery_id=item.id, error=str(exc))
                else:
                    item.status = "delivered"
                    item.delivered_at = now_utc8_naive()
                    delivered += 1
                item.updated_at = now_utc8_naive()
            await session.commit()
            return delivered

    @classmethod
    async def _deliver(
        cls,
        item: NotificationDeliveryDo,
        notice: NoticeDo,
        user: UserDo,
        app_settings: Settings,
    ) -> None:
        payload = {
            "notice_id": notice.id,
            "title": notice.notice_title,
            "content": notice.notice_content,
            "username": user.username,
        }
        if item.channel == "webhook":
            if not app_settings.NOTIFICATION_WEBHOOK_URL:
                raise ValueError("通知 Webhook 未配置")
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    app_settings.NOTIFICATION_WEBHOOK_URL, json=payload
                )
                response.raise_for_status()
            return
        if item.channel == "sms":
            if not app_settings.NOTIFICATION_SMS_WEBHOOK:
                raise ValueError("通知短信 Webhook 未配置")
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    app_settings.NOTIFICATION_SMS_WEBHOOK,
                    json={"phone": user.phone, **payload},
                )
                response.raise_for_status()
            return
        if item.channel == "email":
            if not user.email or not app_settings.SMTP_HOST:
                raise ValueError("邮件通知未配置")
            message = EmailMessage()
            message["Subject"] = notice.notice_title
            message["From"] = app_settings.SMTP_FROM or app_settings.SMTP_USERNAME
            message["To"] = user.email
            message.set_content(notice.notice_content)
            await asyncio.to_thread(cls._send_email, message, app_settings)
            return
        raise ValueError(f"不支持的通知渠道: {item.channel}")

    @staticmethod
    def _send_email(message: EmailMessage, app_settings: Settings) -> None:
        """在阻塞线程中发送 SMTP 邮件。"""
        with smtplib.SMTP_SSL(
            app_settings.SMTP_HOST, app_settings.SMTP_PORT, timeout=5
        ) as client:
            if app_settings.SMTP_USERNAME:
                client.login(app_settings.SMTP_USERNAME, app_settings.SMTP_PASSWORD)
            client.send_message(message)
