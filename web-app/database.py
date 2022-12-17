from pymongo import MongoClient
import mongomock
from bson.json_util import dumps, loads
import certifi
import sys

class Database(object):

    database=None
    client=None
    ca = certifi.where()

    @staticmethod
    def initialize(url):
        connection= MongoClient(url, tlsCAFile=Database.ca)
        try:
            connection.admin.command('ping')
            Database.client=connection
            Database.database = connection["project_4"]
            print(' *', 'Connected to MongoDB!', file=sys.stderr)
        except Exception as e:
            print(' *', "Failed to connect to MongoDB at", file=sys.stderr)
            print('Database connection error: ' + e, file=sys.stderr)

    @staticmethod
    def initialize_mock():
        Database.database = mongomock.MongoClient().db

    @staticmethod
    def insert_one(collection, data):
        return Database.database[collection].insert_one(data)

    @staticmethod
    def find(collection, query="", field=""):
        return (Database.database[collection].find(query,field))

    @staticmethod
    def find_one(collection, query, field=""):
        return (Database.database[collection].find_one(query,field))

    @staticmethod
    def find_first_sorted(collection, query, field=""):
        return (Database.database[collection].find(query,field).sort('time', -1).limit(1))

    @staticmethod
    def delete(collection, query):
        return Database.database[collection].delete_one(query)

    @staticmethod
    def update(collection, search, query):
        return Database.database[collection].update_one(search,query)

    @staticmethod
    def close():
        Database.client.close()