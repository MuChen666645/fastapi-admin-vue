from types import SimpleNamespace

import anyio

from module_admin.dao.job_dao import JobDao
from module_admin.entity.dto.job_dto import ScheduledJobCreateDto


class CreateSession:
    def __init__(self) -> None:
        self.item = None
        self.flush_called = False

    def add(self, item) -> None:
        self.item = item

    async def flush(self) -> None:
        self.flush_called = True
        self.item.id = 42


def test_job_create_flushes_generated_id_before_returning() -> None:
    async def run() -> None:
        session = CreateSession()
        request = SimpleNamespace(
            state=SimpleNamespace(mysql=session, tenant_id=1, user_id=7)
        )
        data = ScheduledJobCreateDto(
            job_name="测试",
            job_key="test",
            task_name="test_task",
            cron_expression="*/1 * * * *",
            args_json='{"batch_size":100,"timeout":30,"operator":"system"}',
        )

        item = await JobDao.create(data, request)

        assert session.flush_called is True
        assert item.id == 42
        assert item.tenant_id == 1
        assert item.create_by == 7

    anyio.run(run)
