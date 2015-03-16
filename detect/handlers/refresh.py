from tornado.web import RequestHandler, asynchronous
from detect.container import Container
from detect.vocab import Vocab

__author__ = 'robdefeo'

class Refresh(RequestHandler):
    def on_finish(self):
        pass

    @asynchronous
    def get(self):
        container = Container()
        vocab = Vocab(container=container)
        vocab.load(['en'])
        self.set_header('Content-Type', 'application/json')
        self.set_status(200)
        self.finish({
            "status": "OK"
        })