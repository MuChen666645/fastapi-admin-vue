from contextlib import asynccontextmanager
from types import SimpleNamespace

import anyio
import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError

from config.mysql_serve import bind_request_mysql_session
from interceptors.http_intercept import ApiExceptionInterception


class FakeSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.closed = False
        self.commit_count = 0
        self.commit_error = commit_error
        self.rolled_back = False

    async def commit(self) -> None:
        self.commit_count += 1
        if self.commit_error is not None:
            raise self.commit_error

    async def rollback(self) -> None:
        self.rolled_back = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        self.closed = True


class FakeSessionFactory:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.sessions: list[FakeSession] = []

    def __call__(self) -> FakeSession:
        session = FakeSession(commit_error=self.commit_error)
        self.sessions.append(session)
        return session


def create_request(session_factory: FakeSessionFactory):
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(mysql_session_factory=session_factory)
        ),
        state=SimpleNamespace(),
    )


def test_request_mysql_session_is_isolated_and_closed() -> None:
    async def run() -> None:
        session_factory = FakeSessionFactory()
        first_request = create_request(session_factory)
        second_request = create_request(session_factory)
        session_context = asynccontextmanager(bind_request_mysql_session)

        async with session_context(first_request):
            first_session = first_request.state.mysql
            async with session_context(second_request):
                second_session = second_request.state.mysql
                assert first_session is not second_session

        assert first_session.closed
        assert second_session.closed
        assert first_session.commit_count == 1
        assert second_session.commit_count == 1
        assert not first_session.rolled_back
        assert not second_session.rolled_back
        assert first_request.state.mysql is None
        assert second_request.state.mysql is None

    anyio.run(run)


def test_request_mysql_session_rolls_back_on_error() -> None:
    async def run() -> None:
        session_factory = FakeSessionFactory()
        request = create_request(session_factory)
        session_context = asynccontextmanager(bind_request_mysql_session)

        with pytest.raises(RuntimeError, match="request failed"):
            async with session_context(request):
                raise RuntimeError("request failed")

        session = session_factory.sessions[0]
        assert session.commit_count == 0
        assert session.rolled_back
        assert session.closed
        assert request.state.mysql is None

    anyio.run(run)


def test_request_mysql_session_rolls_back_when_commit_fails() -> None:
    async def run() -> None:
        session_factory = FakeSessionFactory(commit_error=RuntimeError("commit failed"))
        request = create_request(session_factory)
        session_context = asynccontextmanager(bind_request_mysql_session)

        with pytest.raises(RuntimeError, match="commit failed"):
            async with session_context(request):
                pass

        session = session_factory.sessions[0]
        assert session.commit_count == 1
        assert session.rolled_back
        assert session.closed
        assert request.state.mysql is None

    anyio.run(run)


def test_commit_integrity_error_returns_sanitized_client_error() -> None:
    async def run() -> None:
        commit_error = IntegrityError(
            "INSERT INTO users",
            {},
            RuntimeError("duplicate user"),
        )
        session_factory = FakeSessionFactory(commit_error=commit_error)
        test_app = FastAPI(dependencies=[Depends(bind_request_mysql_session)])
        test_app.state.mysql_session_factory = session_factory
        ApiExceptionInterception(test_app)

        @test_app.get("/test")
        async def test_endpoint():
            return {"ok": True}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/test")

        assert response.status_code == 400
        assert response.json() == {"detail": "database anomaly"}
        assert "INSERT INTO users" not in response.text
        assert "duplicate user" not in response.text
        assert session_factory.sessions[0].rolled_back

    anyio.run(run)
