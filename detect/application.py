
__author__ = 'robdefeo'
import tornado
import tornado.web
import tornado.options
from tornado.web import url
from detect.handlers.detect import Detect
from detect.handlers.proxy import Proxy
from detect.handlers.status import Status
from detect.handlers.refresh import Refresh

class Application(tornado.web.Application):
    def __init__(self):
        from detect.parse import Parse
        handlers = [
            url(r"/", Detect, dict(parse=Parse()), name="detect"),
            url(r"/proxy.html", Proxy, name="proxy"),
            url(r"/status", Status, name="status"),
            url(r"/refresh", Refresh, name="refresh")
        ]

        settings = dict(
            # static_path = os.path.join(os.path.dirname(__file__), "static"),
            # template_path = os.path.join(os.path.dirname(__file__), "templates"),
            debug = tornado.options.options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)