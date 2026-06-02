from src.infra.database import async_database_url, connect_args, sync_database_url


def test_user_model_does_not_emit_ydb_unsupported_unique_constraint():
    from sqlalchemy.schema import CreateTable
    from ydb_sqlalchemy.sqlalchemy import YqlDialect

    from src.infra.adapters.database.models import UserModel

    create_sql = str(CreateTable(UserModel.__table__).compile(dialect=YqlDialect()))

    assert "UNIQUE" not in create_sql


def test_models_do_not_emit_ydb_unsupported_foreign_key_constraints():
    from sqlalchemy.schema import CreateTable
    from ydb_sqlalchemy.sqlalchemy import YqlDialect

    from src.infra.adapters.database.models import ApplicationModel, VacancyModel

    create_vacancies_sql = str(
        CreateTable(VacancyModel.__table__).compile(dialect=YqlDialect())
    )
    create_applications_sql = str(
        CreateTable(ApplicationModel.__table__).compile(dialect=YqlDialect())
    )

    assert "FOREIGN KEY" not in create_vacancies_sql
    assert "FOREIGN KEY" not in create_applications_sql


def test_builds_ydb_urls_from_full_endpoint_dsn(monkeypatch):
    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv(
        "YDB_ENDPOINT",
        "grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1g/folder/database",
    )

    assert (
        async_database_url()
        == "yql+ydb_async://ydb.serverless.yandexcloud.net:2135/ru-central1/b1g/folder/database"
    )
    assert (
        sync_database_url()
        == "yql+ydb://ydb.serverless.yandexcloud.net:2135/ru-central1/b1g/folder/database"
    )


def test_uses_database_url_for_non_ydb_backends(monkeypatch):
    monkeypatch.delenv("DATABASE_BACKEND", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

    assert async_database_url() == "sqlite+aiosqlite:///./test.db"
    assert sync_database_url() == "sqlite:///./test.db"


def test_uses_anonymous_credentials_and_disables_discovery_for_local_ydb(monkeypatch):
    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv("YDB_AUTH_MODE", "anonymous")
    monkeypatch.setenv("YDB_DISABLE_DISCOVERY", "1")

    args = connect_args()

    assert args["credentials"].__class__.__name__ == "AnonymousCredentials"
    assert args["driver_config_kwargs"] == {"disable_discovery": True}


def test_uses_access_token_credentials_for_ydb(monkeypatch):
    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv("YDB_AUTH_MODE", "access_token")
    monkeypatch.setenv("YDB_ENDPOINT", "grpc://localhost:2136/local")
    monkeypatch.setenv("YDB_ACCESS_TOKEN", "test-token")

    args = connect_args()

    assert args["credentials"].__class__.__name__ == "AuthTokenCredentials"
    assert args["protocol"] == "grpc"


def test_uses_secure_grpc_for_serverless_ydb_endpoint_without_scheme(monkeypatch):
    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv("YDB_AUTH_MODE", "access_token")
    monkeypatch.setenv(
        "YDB_ENDPOINT",
        "grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1g/folder/database",
    )
    monkeypatch.setenv("YDB_ACCESS_TOKEN", "test-token")

    args = connect_args()

    assert args["credentials"].__class__.__name__ == "AuthTokenCredentials"
    assert args["protocol"] == "grpcs"


def test_uses_secure_grpc_for_explicit_grpcs_ydb_endpoint(monkeypatch):
    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv("YDB_AUTH_MODE", "access_token")
    monkeypatch.setenv(
        "YDB_ENDPOINT",
        "grpcs://ydb.serverless.yandexcloud.net:2135/?database=/ru-central1/b1g/folder/database",
    )
    monkeypatch.setenv("YDB_ACCESS_TOKEN", "test-token")

    args = connect_args()

    assert args["credentials"].__class__.__name__ == "AuthTokenCredentials"
    assert args["protocol"] == "grpcs"
