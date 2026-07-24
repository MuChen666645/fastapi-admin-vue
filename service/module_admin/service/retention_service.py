"""数据库日志和临时记录保留期清理服务。"""

from datetime import timedelta

from sqlalchemy import and_, delete, or_

from config.env import Settings
from module_admin.entity.do.log_do import ExceptionLogDo, LoginLogDo, OperationLogDo
from module_admin.entity.do.notification_do import NotificationDeliveryDo
from module_admin.entity.do.operation_do import BatchOperationAuditDo, IdempotencyKeyDo
from utils.time_utils import now_utc8_naive


class RetentionService:
    """按配置删除已完成且超过保留期的运行记录。"""

    @staticmethod
    async def cleanup(session_factory, app_settings: Settings) -> dict[str, int]:
        now = now_utc8_naive()
        idempotency_cutoff = now - timedelta(
            days=app_settings.IDEMPOTENCY_RETENTION_DAYS
        )
        log_cutoff = now - timedelta(days=app_settings.LOG_RETENTION_DAYS)
        batch_cutoff = now - timedelta(days=app_settings.BATCH_AUDIT_RETENTION_DAYS)
        notification_cutoff = now - timedelta(
            days=app_settings.NOTIFICATION_RETENTION_DAYS
        )
        statements = {
            "idempotency_keys": delete(IdempotencyKeyDo).where(
                or_(
                    IdempotencyKeyDo.expires_at <= now,
                    IdempotencyKeyDo.created_at < idempotency_cutoff,
                )
            ),
            "batch_operation_audits": delete(BatchOperationAuditDo).where(
                BatchOperationAuditDo.created_at < batch_cutoff
            ),
            "login_logs": delete(LoginLogDo).where(LoginLogDo.login_time < log_cutoff),
            "operation_logs": delete(OperationLogDo).where(
                OperationLogDo.operation_time < log_cutoff
            ),
            "exception_logs": delete(ExceptionLogDo).where(
                ExceptionLogDo.exception_time < log_cutoff
            ),
            "notification_deliveries": delete(NotificationDeliveryDo).where(
                and_(
                    NotificationDeliveryDo.status.in_(
                        ("delivered", "failed", "cancelled")
                    ),
                    NotificationDeliveryDo.updated_at < notification_cutoff,
                )
            ),
        }
        deleted: dict[str, int] = {}
        async with session_factory() as session:
            for table_name, statement in statements.items():
                result = await session.execute(statement)
                deleted[table_name] = int(result.rowcount or 0)
            await session.commit()
        return deleted
