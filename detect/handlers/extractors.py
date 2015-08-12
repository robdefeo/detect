from bson import ObjectId
from bson.errors import InvalidId
from tornado.escape import json_encode
from tornado.web import RequestHandler, Finish


class Path:
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def detection_id(self, detection_id) -> ObjectId:
        try:
            return ObjectId(detection_id)
        except:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=detection_id,detection_id=%s" % detection_id
                    }
                )
            )
            raise Finish()


class Body:
    def __init__(self, handler: RequestHandler):
        self.handler = handler


class Param:
    def __init__(self, handler: RequestHandler):
        self.handler = handler
        pass

    def session_id(self):
        raw_session_id = self.handler.get_argument("session_id", None)
        if raw_session_id is None:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param(s) session_id"
                    }
                )
            )
            raise Finish()

        try:
            return ObjectId(raw_session_id)
        except InvalidId:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=session_id,session_id=%s" % raw_session_id
                    }
                )
            )
            raise Finish()

    def application_id(self):
        raw_application_id = self.handler.get_argument("application_id", None)
        if raw_application_id is None:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param(s) application_id"
                    }
                )
            )
            raise Finish()

        try:
            return ObjectId(raw_application_id)
        except InvalidId:
            self.handler.set_status(412)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=application_id,application_id=%s" %
                                   raw_application_id
                    }
                )
            )
            raise Finish()

    def user_id(self):
        raw_user_id = self.handler.get_argument("user_id", None)
        try:
            return ObjectId(raw_user_id) if raw_user_id is not None else None
        except InvalidId:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=user_id,user_id=%s" % raw_user_id
                    }
                )
            )
            raise Finish()

    def query(self):
        original_q = self.handler.get_argument("q", None)
        if original_q is None:
            self.handler.set_status(428)
            self.handler.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "missing param=q"
                    }
                )
            )
            raise Finish()
        else:
            return original_q

    def skip_slack_log(self):
        return self.handler.get_argument("skip_slack_log", False)

