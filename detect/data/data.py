import logging

from detect.settings import (MONGODB_DB, MONGODB_HOST, MONGODB_PASSWORD,
                             MONGODB_USER)
from pymongo import MongoClient


class Data(object):
    LOGGER = logging.getLogger(__name__)
    collection = None
    collection_name = None
    client = None

    def create_db(self):
        self.client = MongoClient(
            "mongodb://%s:%s@%s:27017/%s" % (
                MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST, MONGODB_DB
            )
        )
        return self.client[MONGODB_DB]

    def open_connection(self):
        if self.collection_name is None:
            raise Exception("no collection name specified")

        self.collection = self.create_db()[self.collection_name]

    def close_connection(self):
        self.client.close()


