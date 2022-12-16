from pymongo import MongoClient
import mongomock
import pytest
from app import app
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def flask_app():
    app.config.update({'TESTING': True})
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def app_with_database(flask_app):
    database = mongomock.MongoClient().db
    yield database

@pytest.fixture(scope='session')
def app_with_data(app_with_database):
    hashed_password = generate_password_hash("test")
    app_with_database.database.insert_one('user', {"username": "test", 'firstName': "test", 'lastName': "test",  "password": hashed_password})
    yield app_with_database

