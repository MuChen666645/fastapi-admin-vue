"""应用时间工具。"""

from datetime import datetime, timedelta, timezone

# 应用统一使用东八区，数据库 DATETIME 写入时再去除时区信息。
UTC8 = timezone(timedelta(hours=8), name="UTC+08:00")


def now_utc8() -> datetime:
    """返回当前带时区的东八区时间。"""
    return datetime.now(UTC8)


def now_utc8_naive() -> datetime:
    """返回用于 MySQL DATETIME 字段存储的东八区本地时间。"""
    return now_utc8().replace(tzinfo=None)
