import os
import time
from collections.abc import Iterator

import pytest
import pytest_asyncio
import ydb
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.core.container import DockerContainer
from ydb_dbapi.errors import DatabaseError

from src.infra.database import connect_args, sync_database_url
from src.infra.database import async_database_url
from src.presentation.http.app import create_app


def _configure_ydb_environment(endpoint: str) -> None:
    os.environ["DATABASE_BACKEND"] = "ydb"
    os.environ["YDB_ENDPOINT"] = f"{endpoint}/local"
    os.environ["YDB_AUTH_MODE"] = "anonymous"
    os.environ["YDB_DISABLE_DISCOVERY"] = "1"


def _wait_for_ydb(endpoint: str) -> None:
    driver_config = ydb.DriverConfig(
        endpoint,
        database="/local",
        credentials=ydb.credentials.AnonymousCredentials(),
        disable_discovery=True,
    )
    driver = ydb.Driver(driver_config)
    try:
        driver.wait(timeout=30, fail_fast=True)
    finally:
        driver.stop()


def _wait_for_ydb_schema_operations() -> None:
    deadline = time.monotonic() + 30
    engine = create_engine(sync_database_url(), connect_args=connect_args())
    try:
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                with engine.connect() as connection:
                    cursor = connection.connection.driver_connection.cursor()
                    cursor.execute_scheme(
                        "CREATE TABLE pytest_ydb_ready "
                        "(id UTF8, PRIMARY KEY (id))"
                    )
                    cursor.execute_scheme("DROP TABLE pytest_ydb_ready")
                return
            except DatabaseError as exc:
                last_error = exc
                time.sleep(1)
        if last_error is not None:
            raise last_error
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def ydb_database() -> Iterator[None]:
    container = DockerContainer("ydbplatform/local-ydb:latest")
    container.with_exposed_ports(2136)
    container.start()

    try:
        endpoint = f"grpc://{container.get_container_host_ip()}:{container.get_exposed_port(2136)}"
        _configure_ydb_environment(endpoint)
        _wait_for_ydb(endpoint)
        _wait_for_ydb_schema_operations()
        command.upgrade(Config("alembic.ini"), "head")
        yield
    finally:
        container.stop()


def _clean_database() -> None:
    engine = create_engine(sync_database_url(), connect_args=connect_args())
    try:
        with engine.connect() as connection:
            for table in ("applications", "vacancies", "employers", "users"):
                connection.execute(text(f"DELETE FROM {table}"))
    finally:
        engine.dispose()


@pytest.fixture
def client(ydb_database, monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", "integration-test-secret")
    monkeypatch.setenv("AUTH_ACCESS_TOKEN_TTL_SECONDS", "3600")

    _clean_database()
    with TestClient(create_app()) as test_client:
        yield test_client
    _clean_database()


@pytest_asyncio.fixture
async def db_session(ydb_database):
    _clean_database()
    engine = create_async_engine(
        async_database_url(), connect_args=connect_args(), poolclass=NullPool
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()
    _clean_database()
