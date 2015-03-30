from detect import __version__

__author__ = 'robdefeo'
from datetime import datetime

from tornado.web import RequestHandler
from tornado.log import app_log
from bson.objectid import ObjectId
from tornado.escape import json_encode
from tornado.web import asynchronous

from detect.workers.worker import Worker


class Detect(RequestHandler):
    def initialize(self, parse):
        self.parse = parse

    def on_finish(self):
        pass

    @asynchronous
    def get(self):
        from detect.vocab import alias_data

        try:
            self.set_header('Content-Type', 'application/json')
            original_q = self.get_argument("q", None)
            user_id = self.get_argument("user_id", None)
            session_id = self.get_argument("session_id", None)
            application_id = self.get_argument("application_id", None)
            skip_mongodb_log = self.get_argument("skip_mongodb_log", False)
            skip_slack_log = self.get_argument("skip_slack_log", False)

            detection_id = ObjectId()

            app_log.info(
                "app=detection,function=detect,detection_id=%s,application_id=%s,session_id=%s,q=%s",
                detection_id,
                application_id,
                session_id,
                original_q
            )

            if original_q is None:
                self.set_status(412)
                self.finish(
                    json_encode(
                        {
                            "status": "error",
                            "message": "missing param=q"
                        }
                    )
                )

            elif not application_id:
                self.set_status(412)
                self.finish(
                    json_encode({
                        "status": "error",
                        "message": "missing param(s)",
                        "session_id": str(session_id)
                        }
                    )
                )
            elif not session_id:
                self.set_status(412)
                self.finish(
                    json_encode({
                        "status": "error",
                        "message": "missing param(s)",
                        "session_id": str(session_id)
                        }
                    )
                )

            else:
                preprocess_result = self.parse.preparation(original_q)
                disambiguate_result = self.parse.disambiguate(alias_data, preprocess_result)
                date = datetime.now()

                res = {
                    "_id": str(detection_id),
                    "detections": disambiguate_result["detections"],
                    "non_detections": disambiguate_result["non_detections"],
                    "version": __version__,
                    "timestamp": date.isoformat()
                }
                if "autocorrected_query" in disambiguate_result:
                    res["autocorrected_query"] = disambiguate_result["autocorrected_query"]

                self.set_status(200)
                self.finish(
                    json_encode(res)
                )

                log = {
                    "_id": detection_id,
                    "session_id": session_id,
                    "application_id": application_id,
                    "tokens": preprocess_result["tokens"],
                    "detections": disambiguate_result["detections"],
                    "non_detections": disambiguate_result["detections"],
                    "version": __version__,
                    "timestamp": date,
                    "q": original_q
                }
                if "autocorrected_query" in disambiguate_result:
                    log["autocorrected_query"] = disambiguate_result["autocorrected_query"]
                Worker(
                    ObjectId(user_id) if user_id is not None else None,
                    ObjectId(application_id),
                    ObjectId(session_id),
                    ObjectId(detection_id),
                    preprocess_result["tokens"], disambiguate_result["detections"], disambiguate_result["non_detections"],
                    date, original_q, skip_mongodb_log, skip_slack_log
                ).start()

        except Exception as e:
            app_log.error("error=%s" % e)
            self.set_status(500)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "exception": e
                    }
                )
            )
        finally:
            pass
