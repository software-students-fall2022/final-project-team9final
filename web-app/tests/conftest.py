import pytest
from app import app, Database
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def flask_app():
    app.config.update({'TESTING': True})
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='session')
def app_with_database(flask_app):
    Database.initialize_mock()
    yield flask_app

@pytest.fixture(scope='session')
def app_with_data(app_with_database):
    hashed_password = generate_password_hash("test")
    Database.insert_one('users', {"username": "test", 'firstName': "test", 'lastName': "test", "password": hashed_password, "stories":[], "followers":[],"following":[]})
    yield app_with_database

@pytest.fixture(scope='session')
def app_with_book(app_with_data):
    _id = Database.insert_one('books',{"title": "test", 'story': ["test"], 'shared' : False, 'liked' : []})
    Database.update('users',{"username": "test"}, {'$push' : {'stories' : ObjectId(_id.inserted_id)}})
    yield app_with_data, _id.inserted_id

# @pytest.fixture(scope='session')
# def book_id(app_with_data):
#     _id = Database.insert_one('books',{"title": "test", 'story': "test", 'shared' : False, 'liked' : []})
#     yield app_with_data, _id.inserted_id
