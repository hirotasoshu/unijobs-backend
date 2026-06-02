import os
import time
from urllib.parse import parse_qs, urlparse

import ydb
from sqlalchemy import create_engine
from ydb_dbapi.errors import DatabaseError

from src.infra.database import connect_args, sync_database_url


def wait_for_driver() -> None:
    parsed_endpoint = urlparse(os.environ["YDB_ENDPOINT"])
    database = parse_qs(parsed_endpoint.query).get("database", [None])[0]
    database = database or parsed_endpoint.path
    config = ydb.DriverConfig(
        f"{parsed_endpoint.scheme}://{parsed_endpoint.netloc}",
        database=database,
        credentials=ydb.credentials.AnonymousCredentials(),
        disable_discovery=True,
    )
    driver = ydb.Driver(config)
    try:
        driver.wait(timeout=60, fail_fast=True)
    finally:
        driver.stop()


def wait_for_schema_operations() -> None:
    deadline = time.monotonic() + 60
    last_error: Exception | None = None
    engine = create_engine(sync_database_url(), connect_args=connect_args())
    try:
        while time.monotonic() < deadline:
            try:
                with engine.connect() as connection:
                    cursor = connection.connection.driver_connection.cursor()
                    cursor.execute_scheme(
                        "CREATE TABLE compose_ydb_ready "
                        "(id UTF8, PRIMARY KEY (id))"
                    )
                    cursor.execute_scheme("DROP TABLE compose_ydb_ready")
                return
            except DatabaseError as exc:
                last_error = exc
                time.sleep(1)

        raise last_error or RuntimeError("YDB schema operations are not ready")
    finally:
        engine.dispose()


if __name__ == "__main__":
    wait_for_driver()
    wait_for_schema_operations()
