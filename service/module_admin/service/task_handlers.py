"""Worker 任务处理器注册点。"""

from module_admin.service.job_scheduler import TaskHandler

HANDLERS: dict[str, TaskHandler] = {}
