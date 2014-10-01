from detect.settings import MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST, \
    MONGODB_DB
from motor import MotorClient
from tornado import gen
from tornado.ioloop import IOLoop

__author__ = 'robdefeo'
import logging
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
import parse
import traceback
from log import Log
# Define the blueprint: 'detect', set its url prefix: app.url/
mod_detect = Blueprint('detect', __name__, url_prefix='/')
LOGGER = logging.getLogger(__name__)
ioloop = IOLoop()

@mod_detect.route('/')
def detect():
    from detect.vocab import alias_data
    try:
        q = request.args.get("q")
        session_id = request.args.get("session_id")
        detection_id = ObjectId()

        LOGGER.info(
            "app=detection,function=detect,detection_id=%s,session_id=%s,q=%s",
            detection_id,
            session_id,
            q
        )

        if not q or not session_id:
            resp = jsonify({
                "status": "error",
                "message": "missing param(s)",
                "q": q,
                "session_id": str(session_id),
                "detection_id": str(detection_id)
            })
            resp.status_code = 412
            return resp

        q = q.lower().strip()

        preprocess_result = parse.preparation(q)
        disambiguate_result = parse.disambiguate(alias_data, preprocess_result)

        log = {
            "_id": detection_id,
            "session_id": session_id,
            "tokens": preprocess_result["tokens"],
            "detections": disambiguate_result["detections"],
            "non_detections": disambiguate_result["non_detections"]
        }
        # ioloop.stop()
        Log().write(log)
        # ioloop.start()
        # IOLoop.instance().start()
        # IOLoop.instance().stop()

        res = {
            "detection_id": str(detection_id),
            "detections": disambiguate_result["detections"],
            "non_detections": disambiguate_result["non_detections"],
            "version": "1.0.0"
        }
        resp = jsonify(res)
        resp.status_code = 200
        return resp

    except Exception as e:
        print "error=%s" % (traceback.format_exc())
        resp = jsonify({
            "status": "error",
            "exception": traceback.format_exc()
        })
        resp.status_code = 500
        return resp