from datetime import datetime
from bson.json_util import dumps
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from detect.detector import Detector
from detect.entity import EntityFactory

from detect.settings import WIT_URL, WIT_URL_VERSION, WIT_TOKEN


from tornado.web import RequestHandler
from tornado.log import app_log
from bson.objectid import ObjectId
from tornado.escape import json_encode, url_escape, json_decode
from tornado.web import asynchronous

from detect.workers.worker import Worker
from detect import __version__
from detect.handlers.extractors import ParamExtractor, PathExtractor


class Detect(RequestHandler):
    brute_detector = None
    alias_data = None
    data_response = None
    param_extractor = None
    path_extractor = None
    entity_factory = None

    def data_received(self, chunk):
        pass

    def initialize(self, alias_data):
        from detect.data.response import Response
        self.data_response = Response()
        self.data_response.open_connection()
        self.alias_data = alias_data
        self.param_extractor = ParamExtractor(self)
        self.path_extractor = PathExtractor(self)
        self.entity_factory = EntityFactory(self.alias_data)
        self.brute_detector = Detector(self.alias_data)


    def on_finish(self):
        pass

    @asynchronous
    def post(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json')

        detection_id = ObjectId()

        app_log.info(
            "app=detection,function=detect,detection_id=%s,application_id=%s,session_id=%s,q=%s",
            detection_id,
            self.param_extractor.application_id(),
            self.param_extractor.session_id(),
            self.param_extractor.query()
        )

        if False:
            url = "%smessage?v=%s&q=%s&msg_id=%s" % (
                WIT_URL, WIT_URL_VERSION, url_escape(self.param_extractor.query()), str(detection_id)
            )
            r = HTTPRequest(
                url,
                headers={
                    "Authorization": "Bearer %s" % WIT_TOKEN
                }
            )
            client = AsyncHTTPClient()
            client.fetch(r, callback=self.wit_call_back)
        else:
            date = datetime.now()
            outcomes = self.brute_detector.detect(self.param_extractor.query())
            self.data_response.insert(
                self.param_extractor.user_id(),
                self.param_extractor.application_id(),
                self.param_extractor.session_id(),
                detection_id,
                "brute",
                date,
                self.param_extractor.query(),
                outcomes=outcomes
            )

            self.set_status(202)
            self.set_header("Location", "/%s" % str(detection_id))
            self.set_header("_id", str(detection_id))
            self.finish()

            Worker(
                self.param_extractor.user_id(),
                self.param_extractor.application_id(),
                self.param_extractor.session_id(),
                detection_id,
                date,
                self.param_extractor.query(),
                self.param_extractor.skip_slack_log(),
                detection_type="wit",
                outcomes=outcomes
            ).start()



    @asynchronous
    def get(self, detection_id, *args, **kwargs):
        data = self.data_response.get(self.path_extractor.detection_id(detection_id))
        if data is not None:
            self.set_header('Content-Type', 'application/json')
            self.set_status(200)
            self.finish(
                dumps(
                    {
                        "type": data["type"],
                        "q": data["q"],
                        "outcomes": data["outcomes"],
                        "_id": data["_id"],
                        "version": data["version"],
                        "timestamp": data["timestamp"]
                    }
                )
            )
        else:
            self.set_status(404)
            self.finish()

    def wit_call_back(self, response):
        data = json_decode(response.body)
        outcomes = []
        date = datetime.now()
        for outcome in data["outcomes"]:
            entities = []
            for _type in outcome["entities"].keys():
                if _type not in ["polite"]:
                    for value in outcome["entities"][_type]:
                        suggested = value["suggested"] if "suggested" in value else False
                        key = value["value"]["value"] if type(value["value"]) is dict else value["value"]
                        entity = self.entity_factory.create(_type, key, suggested)

                        # TODO this needs to be moved somewhere else preferably a seperate service call
                        entities.append(entity)

            outcomes.append(
                {
                    "confidence": outcome["confidence"] * 100,
                    "intent": outcome["intent"],
                    "entities": entities
                }
            )

        self.data_response.insert(
            self.param_extractor.user_id(),
            self.param_extractor.application_id(),
            self.param_extractor.session_id(),
            ObjectId(data["msg_id"]),
            "wit",
            date,
            self.param_extractor.query(),
            outcomes=outcomes
        )

        self.set_status(202)
        self.set_header("Location", "/%s" % data["msg_id"])
        self.set_header("_id", data["msg_id"])
        self.finish()

        Worker(
            self.param_extractor.user_id(),
            self.param_extractor.application_id(),
            self.param_extractor.session_id(),
            ObjectId(data["msg_id"]),
            date,
            self.param_extractor.query(),
            self.param_extractor.skip_slack_log(),
            detection_type="wit",
            outcomes=outcomes
        ).start()

