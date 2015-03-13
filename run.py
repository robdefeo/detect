__author__ = 'robdefeo'
import sys

import tornado
import tornado.options
from tornado.httpserver import HTTPServer
import tornado.ioloop
from detect.application import Application

from detect.container import Container
container = Container()
from detect.vocab import Vocab

vocab = Vocab(container=container)
vocab.generate()
vocab.load()

from detect.vocab import alias_data

from detect.settings import PORT
tornado.options.define('port', type=int, default=PORT, help='server port number (default: 9000)')
tornado.options.define('debug', type=bool, default=False, help='run in debug mode with autoreload (default: False)')


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = HTTPServer(Application(vocab))
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
