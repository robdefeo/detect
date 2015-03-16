__author__ = 'robdefeo'
import tornado
import tornado.options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from detect.application import Application
from detect.container import Container
from detect.vocab import Vocab

container = Container()
vocab = Vocab(container=container)
vocab.load(['en'])

from detect.settings import PORT
tornado.options.define('port', type=int, default=PORT, help='server port number (default: 9000)')
tornado.options.define('debug', type=bool, default=False, help='run in debug mode with autoreload (default: False)')


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = HTTPServer(Application())
    http_server.listen(tornado.options.options.port)
    IOLoop.instance().start()
