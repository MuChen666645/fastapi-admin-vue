from types import SimpleNamespace

import anyio
import pytest

from module_admin.entity.do.notice_do import NoticeDo
from module_admin.entity.dto.notice_dto import (
    NoticeCreateDto,
    NoticeLatestDto,
    NoticeUpdateDto,
)
from module_admin.entity.notice_type import NoticeType
from module_admin.service.notice_service import NoticeService


class Result:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class LatestSession:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        notice_type = ("system", "approval", "alarm")[len(self.statements) - 1]
        notice = NoticeDo(
            id=400 + len(self.statements),
            tenant_id=1,
            notice_title=f"{notice_type} notice",
            notice_type=notice_type,
            notice_content="content",
            status="1",
        )
        return Result([(notice, None)])


def test_notice_create_and_update_accept_only_defined_types() -> None:
    assert (
        NoticeCreateDto(
            notice_title="System notice", notice_content="Content"
        ).notice_type
        is NoticeType.SYSTEM
    )
    assert NoticeUpdateDto(notice_type=NoticeType.ALARM).notice_type is NoticeType.ALARM

    with pytest.raises(ValueError):
        NoticeCreateDto(
            notice_title="Unknown notice",
            notice_type="custom",
            notice_content="Content",
        )


def test_latest_notice_service_returns_three_groups() -> None:
    async def run() -> None:
        session = LatestSession()
        request = SimpleNamespace(
            state=SimpleNamespace(mysql=session, tenant_id=1, user_id=1)
        )

        result = await NoticeService.list_latest(request)

        assert isinstance(result, NoticeLatestDto)
        assert len(result.system) == 1
        assert len(result.approval) == 1
        assert len(result.alarm) == 1
        assert all(
            any(value == 5 for value in statement.compile().params.values())
            for statement in session.statements
        )

    anyio.run(run)
