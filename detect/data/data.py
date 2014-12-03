import logging

from detect.settings import (MONGODB_DB, MONGODB_HOST, MONGODB_PASSWORD,
                             MONGODB_USER)
from pymongo import MongoClient


class Data(object):
    LOGGER = logging.getLogger(__name__)

    def __init__(self):
        pass

    def create_db(self):
        client =  MongoClient("mongodb://%s:%s@%s:27017/%s" % (
            MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST, MONGODB_DB
        ))
        return client[MONGODB_DB]


