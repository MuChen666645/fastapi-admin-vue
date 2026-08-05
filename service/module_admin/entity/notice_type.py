"""通知类型定义。"""

from enum import Enum


class NoticeType(str, Enum):
    """消息中心支持的通知类型。"""

    SYSTEM = "system"
    APPROVAL = "approval"
    ALARM = "alarm"
