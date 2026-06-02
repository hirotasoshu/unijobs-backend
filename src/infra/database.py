import json
import os
from pathlib import Path
from typing import Any


def database_backend() -> str:
    return os.getenv("DATABASE_BACKEND", "sqlite")


def _ydb_endpoint() -> str:
    return os.environ["YDB_ENDPOINT"].removeprefix("grpcs://").removeprefix("grpc://")


def async_database_url() -> str:
    if database_backend() == "ydb":
        return f"yql+ydb_async://{_ydb_endpoint()}{os.environ['YDB_DATABASE']}"

    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")


def sync_database_url() -> str:
    if database_backend() == "ydb":
        return f"yql+ydb://{_ydb_endpoint()}{os.environ['YDB_DATABASE']}"

    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)


def _service_account_json() -> dict[str, Any]:
    if key_file := os.getenv("YC_SERVICE_ACCOUNT_KEY_FILE"):
        return json.loads(Path(key_file).read_text())

    return json.loads(os.environ["YC_SA_JSON_CREDENTIALS"])


def connect_args() -> dict[str, Any]:
    if database_backend() != "ydb":
        return {}

    args: dict[str, Any] = {}
    if os.getenv("YDB_DISABLE_DISCOVERY") == "1":
        args["driver_config_kwargs"] = {"disable_discovery": True}

    auth_mode = os.getenv("YDB_AUTH_MODE", "metadata")
    if auth_mode == "anonymous":
        import ydb.credentials

        args["credentials"] = ydb.credentials.AnonymousCredentials()
        return args

    if auth_mode == "access_token":
        import ydb.credentials

        args.update(
            {
                "credentials": ydb.credentials.AuthTokenCredentials(
                    os.environ["YDB_ACCESS_TOKEN"]
                ),
                "protocol": "grpc",
            }
        )
        return args

    if auth_mode == "service_account_json":
        args.update({
            "credentials": {
                "service_account_json": _service_account_json(),
            },
            "protocol": "grpc",
        })
        return args

    import ydb.iam

    args.update({
        "credentials": ydb.iam.MetadataUrlCredentials(),
        "protocol": "grpc",
    })
    return args
