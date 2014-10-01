__author__ = 'robdefeo'
from motor import MotorClient
from settings import MONGODB_DB, MONGODB_HOST, MONGODB_PASSWORD, MONGODB_PORT, MONGODB_USER
from tornado.ioloop import IOLoop
class Log(object):
    def __init__(self):
        pass

    def create_db(self):
        client = MotorClient("mongodb://%s:%s@%s:27017/%s" % (
            MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST,
            MONGODB_DB
        ))
        return client[MONGODB_DB]

    def write(self, log):
        # i dont even think this does it async like i want
        def write_callback(result, error):
            IOLoop.instance().stop()

        self.create_db()["responses"].insert(
            log,
            callback=write_callback
        )
        IOLoop.instance().start()
