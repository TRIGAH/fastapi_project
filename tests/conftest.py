from fastapi.testclient import TestClient
from app.main import app
from app import schemas
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import engine,get_db
from app.database import Base
import pytest

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/fastapi_test'
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)  


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close() 

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close() 
    app.dependency_overrides[get_db] = override_get_db    
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email":"maps@gmail.com","password":"maps"}
    res=client.post("/users/",json=user_data)
    assert res.status_code == 201
    print (res.json())
    new_user = res.json()
    new_user["password"]=user_data["password"]
    return new_user