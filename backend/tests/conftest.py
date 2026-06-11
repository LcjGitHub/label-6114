import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import Base, get_db
from main import app
from models import Exchange


@pytest.fixture
def db_engine():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_url = f"sqlite:///{tmp.name}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        try:
            Path(tmp.name).unlink(missing_ok=True)
        except PermissionError:
            pass


@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def seed_exchanges(db_session):
    data = [
        Exchange(book_title="三体第一部", counterpart_nickname="书友A", is_completed=True),
        Exchange(book_title="三体第二部黑暗森林", counterpart_nickname="书友B", is_completed=False),
        Exchange(book_title="三体第三部死神永生", counterpart_nickname="书友C", is_completed=True),
        Exchange(book_title="活着", counterpart_nickname="书友D", is_completed=False),
        Exchange(book_title="活着2续篇", counterpart_nickname="书友E", is_completed=True),
        Exchange(book_title="百年孤独", counterpart_nickname="书友F", is_completed=False),
        Exchange(book_title="平凡的世界第一部", counterpart_nickname="书友G", is_completed=True),
        Exchange(book_title="平凡的世界第二部", counterpart_nickname="书友H", is_completed=False),
        Exchange(book_title="平凡的世界第三部", counterpart_nickname="书友I", is_completed=True),
        Exchange(book_title="红楼梦", counterpart_nickname="书友J", is_completed=False),
        Exchange(book_title="水浒传", counterpart_nickname="书友K", is_completed=True),
        Exchange(book_title="三国演义", counterpart_nickname="书友L", is_completed=False),
    ]
    db_session.add_all(data)
    db_session.commit()
    return data
