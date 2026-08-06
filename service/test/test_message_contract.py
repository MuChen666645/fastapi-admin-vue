from datetime import datetime, timezone
from types import SimpleNamespace

import anyio
import pytest
from fastapi_pagination import Params, create_page

from module_admin.dao.message_dao import MessageDao
from module_admin.entity.do.message_do import MessageDo
from module_admin.entity.dto.message_dto import (
    MessageCreateDto,
    MessageDto,
    MessageItemDto,
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


class CreateSession:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def add_all(self, items):
        self.items.extend(items)

    async def flush(self):
        return None


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


def test_message_publish_time_normalizes_utc_input_before_persistence() -> None:
    async def run() -> None:
        session = CreateSession()
        request = SimpleNamespace(
            state=SimpleNamespace(mysql=session, tenant_id=1, user_id=1)
        )
        data = MessageCreateDto(
            message_title="Scheduled message",
            message_content="Content",
            publish_time=datetime(2026, 8, 6, 1, 30, tzinfo=timezone.utc),
        )

        item = await MessageDao.create(data, request)

        assert item.publish_time == datetime(2026, 8, 6, 9, 30)

    anyio.run(run)


def test_message_response_formats_datetime_fields() -> None:
    publish_time = datetime(2026, 8, 6, 9, 30)
    read_at = datetime(2026, 8, 6, 10, 15)
    message = MessageDto(
        id=400,
        message_title="System message",
        message_type="system",
        message_content="Content",
        status="1",
        publish_time=publish_time,
        create_by=1,
        create_time=publish_time,
        update_time=read_at,
    )
    item = MessageItemDto(
        id=400,
        message_title="System message",
        message_type="system",
        message_content="Content",
        publish_time=publish_time,
        read_at=read_at,
    )

    assert message.model_dump(mode="json")["publish_time"] == "2026-08-06 09:30:00"
    assert message.model_dump(mode="json")["update_time"] == "2026-08-06 10:15:00"
    assert item.model_dump(mode="json") == {
        "id": 400,
        "message_title": "System message",
        "message_type": "system",
        "message_content": "Content",
        "publish_time": "2026-08-06 09:30:00",
        "read_at": "2026-08-06 10:15:00",
    }


def test_message_management_page_uses_formatted_response_dtos(monkeypatch) -> None:
    async def fake_list_messages(*_args, **_kwargs):
        return create_page(
            [
                MessageDo(
                    id=401,
                    tenant_id=1,
                    message_title="System message",
                    message_type="system",
                    message_content="Content",
                    status="1",
                    publish_time=datetime(2026, 8, 6, 9, 30),
                )
            ],
            total=1,
            params=Params(),
        )

    monkeypatch.setattr(MessageDao, "list_messages", fake_list_messages)

    async def run() -> None:
        page = await MessageService.list_messages(
            SimpleNamespace(),
            None,
            None,
            None,
            None,
            None,
            None,
            Params(),
        )

        assert isinstance(page.items[0], MessageDto)
        assert page.items[0].model_dump(mode="json")["publish_time"] == (
            "2026-08-06 09:30:00"
        )

    anyio.run(run)
