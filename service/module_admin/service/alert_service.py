"""任务和依赖故障的轻量告警通知。"""

from datetime import datetime

import httpx
from loguru import logger


class AlertService:
    """通过配置的 Webhook 投递结构化告警。"""

    @staticmethod
    async def notify_job_failure(
        webhook_url: str,
        job_id: int | None,
        task_name: str,
        message: str,
        metrics=None,
    ) -> None:
        if not webhook_url:
            return
        payload = {
            "alert_type": "scheduled_job_failure",
            "job_id": job_id,
            "task_name": task_name,
            "message": message[:2000],
            "occurred_at": datetime.now().isoformat(),
        }
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            if metrics is not None:
                metrics.alerts.labels("scheduled_job_failure", "success").inc()
        except Exception:
            if metrics is not None:
                metrics.alerts.labels("scheduled_job_failure", "failed").inc()
            logger.exception("operational_alert_delivery_failed", job_id=job_id)
