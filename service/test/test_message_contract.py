from types import SimpleNamespace

import anyio
import pytest

from module_admin.entity.do.message_do import MessageDo
from module_admin.entity.dto.message_dto import (
    MessageCreateDto,
    MessageLatestDto,
    MessageUpdateDto,
)
from module_admin.entity.message_type import MessageType
from module_admin.service.message_service import MessageService


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
        message_type = ("system", "approval", "alarm")[len(self.statements) - 1]
        message = MessageDo(
            id=400 + len(self.statements),
            tenant_id=1,
            message_title=f"{message_type} message",
            message_type=message_type,
            message_content="content",
            status="1",
        )
        return Result([(message, None)])


def test_message_create_and_update_accept_only_defined_types() -> None:
    assert (
        MessageCreateDto(
            message_title="System message", message_content="Content"
        ).message_type
        is MessageType.SYSTEM
    )
    assert (
        MessageUpdateDto(message_type=MessageType.ALARM).message_type
        is MessageType.ALARM
    )

    with pytest.raises(ValueError):
        MessageCreateDto(
            message_title="Unknown message",
            message_type="custom",
            message_content="Content",
        )


def test_latest_message_service_returns_three_groups() -> None:
    async def run() -> None:
        session = LatestSession()
        request = SimpleNamespace(
            state=SimpleNamespace(mysql=session, tenant_id=1, user_id=1)
        )

        result = await MessageService.list_latest(request)

        assert isinstance(result, MessageLatestDto)
        assert len(result.system) == 1
        assert len(result.approval) == 1
        assert len(result.alarm) == 1
        assert all(
            any(value == 5 for value in statement.compile().params.values())
            for statement in session.statements
        )

    anyio.run(run)
