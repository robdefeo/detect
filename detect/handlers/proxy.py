__author__ = 'robdefeo'
from tornado.web import RequestHandler, asynchronous


class Proxy(RequestHandler):
    def initialize(self):
        pass

    def on_finish(self):
        pass

    @asynchronous
    def get(self):
        self.set_header('Content-Type', 'text/html')
        self.finish("""
<!DOCTYPE HTML>
<script src="//cdn.rawgit.com/jpillora/xdomain/0.6.17/dist/xdomain.min.js" master="*"></script>
    """)

