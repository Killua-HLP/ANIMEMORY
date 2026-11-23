import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
import os
from alembic import command
from alembic.config import Config


test_engine = create_engine(
    settings.TEST_DATABASE_URL
)

@pytest.fixture(scope="session")

def test_db():
    previous_url = os.environ.get("ALEMBIC_DATABASE_URL")

    os.environ["ALEMBIC_DATABASE_URL"] = settings.TEST_DATABASE_URL

    alembic_cfg = Config("alembic.ini")

    try:
        command.upgrade(alembic_cfg, "head")

        try:
            yield
        finally:
            command.downgrade(alembic_cfg, "base")

    finally:
        if previous_url is None:
            os.environ.pop("ALEMBIC_DATABASE_URL", None)
        else:
            os.environ["ALEMBIC_DATABASE_URL"] = previous_url

        test_engine.dispose()

@pytest.fixture
def db_session(test_db):
    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint"
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        try:
            session.close()
        finally:
            transaction.rollback()
            connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

