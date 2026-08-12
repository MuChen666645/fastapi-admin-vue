"""Worker 任务处理器注册点。"""

from typing import Any

from module_admin.service.job_scheduler import TaskHandler


def run_test_task(_args: dict[str, Any]) -> str:
    """提供无副作用的调度链路验证任务。"""
    return "测试任务执行成功"


HANDLERS: dict[str, TaskHandler] = {"test_task": run_test_task}
