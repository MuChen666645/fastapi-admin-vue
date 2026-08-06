"""消息中心类型定义。"""

from enum import Enum


class MessageType(str, Enum):
    """消息中心支持的三类业务消息。"""

    SYSTEM = "system"
    APPROVAL = "approval"
    ALARM = "alarm"


class MessageReadStatus(str, Enum):
    """个人消息列表的阅读状态筛选。"""

    ALL = "all"
    UNREAD = "unread"
    READ = "read"
