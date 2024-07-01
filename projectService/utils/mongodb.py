# utils/mongodb.py

from pymongo import MongoClient
from django.conf import settings

def get_mongo_client():
    client = MongoClient(
        f'mongodb://{settings.MONGO_DB_USER}:{settings.MONGO_DB_PASSWORD}@{settings.MONGO_DB_HOST}:{settings.MONGO_DB_PORT}/'
    )
    return client

def get_mongo_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]
