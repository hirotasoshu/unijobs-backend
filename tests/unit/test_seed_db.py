import seed_db
from sqlalchemy.pool import NullPool


def test_seed_engine_uses_env_driven_database_config(monkeypatch):
    calls = {}

    def fake_create_async_engine(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return object()

    monkeypatch.setenv("DATABASE_BACKEND", "ydb")
    monkeypatch.setenv("YDB_ENDPOINT", "grpc://localhost:2136/local")
    monkeypatch.setenv("YDB_AUTH_MODE", "anonymous")
    monkeypatch.setenv("YDB_DISABLE_DISCOVERY", "1")
    monkeypatch.setattr(seed_db, "create_async_engine", fake_create_async_engine)

    engine = seed_db.create_seed_engine()

    assert engine is not None
    assert calls["url"] == "yql+ydb_async://localhost:2136/local"
    assert calls["kwargs"]["echo"] is True
    assert calls["kwargs"]["poolclass"] is NullPool
    assert calls["kwargs"]["connect_args"]["credentials"] is not None
    assert calls["kwargs"]["connect_args"]["driver_config_kwargs"] == {
        "disable_discovery": True
    }
