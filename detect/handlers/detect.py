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
            session_id = self.get_argument("session_id", None)
            detection_id = ObjectId()

            app_log.info(
                "app=detection,function=detect,detection_id=%s,session_id=%s,q=%s",
                detection_id,
                session_id,
                original_q
            )

            if original_q is None:
                self.set_status(412)
                self.finish(
                    json_encode(
                        {
                            "status": "error",
                            "message": "missing param=q",
                            "detection_id": str(detection_id)
                        }
                    )
                )

            elif not session_id:
                self.set_status(412)
                self.finish(
                    json_encode({
                        "status": "error",
                        "message": "missing param(s)",
                        "session_id": str(session_id),
                        "detection_id": str(detection_id)
                        }
                    )
                )

            else:
                q = original_q.lower().strip()

                preprocess_result = self.parse.preparation(q)
                disambiguate_result = self.parse.disambiguate(alias_data, preprocess_result)
                date = datetime.now().isoformat()
                version = "1.0.0"

                res = {
                    "detection_id": str(detection_id),
                    "detections": disambiguate_result["detections"],
                    "non_detections": disambiguate_result["non_detections"],
                    "version": version,
                    "timestamp": date

                }

                self.set_status(200)
                self.finish(
                    json_encode(res)
                )

                log = {
                    "_id": detection_id,
                    "session_id": session_id,
                    "tokens": preprocess_result["tokens"],
                    "detections": disambiguate_result["detections"],
                    "non_detections": disambiguate_result["non_detections"],
                    "version": version,
                    "timestamp": date,
                    "q": original_q
                }
                Worker(log).start()

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
