from datetime import datetime

from bson.errors import InvalidId
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPError

from detect.settings import WIT_URL, WIT_URL_VERSION, WIT_TOKEN

__author__ = 'robdefeo'

from tornado.web import RequestHandler, MissingArgumentError, Finish
from tornado.log import app_log
from bson.objectid import ObjectId
from tornado.escape import json_encode, url_escape, json_decode
from tornado.web import asynchronous

from detect.workers.worker import Worker


class Detect(RequestHandler):
    parse = None
    alias_data = None

    def data_received(self, chunk):
        pass

    def initialize(self, alias_data):
        self.alias_data = alias_data
        # self.parse = parse

    def on_finish(self):
        pass

    @asynchronous
    def post(self, *args, **kwargs):
        self.set_header('Content-Type', 'application/json')

        detection_id = ObjectId()

        app_log.info(
            "app=detection,function=detect,detection_id=%s,application_id=%s,session_id=%s,q=%s",
            detection_id,
            self.application_id(),
            self.session_id(),
            self.query()
        )

        if True:
            url = "%smessage?v=%s&q=%s&msg_id=%s" % (
                WIT_URL, WIT_URL_VERSION, url_escape(self.query()), str(detection_id)
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
            pass
            # TODO option for old style detection
            # preprocess_result = self.parse.preparation(original_q)
            # disambiguate_result = self.parse.disambiguate(self.alias_data, preprocess_result)
            # date = datetime.now()
            #
            # res = {
            #     "_id": str(detection_id),
            #     "detections": disambiguate_result["detections"],
            #     "non_detections": disambiguate_result["non_detections"],
            #     "version": __version__,
            #     "timestamp": date.isoformat()
            # }
            # if "autocorrected_query" in disambiguate_result:
            #     res["autocorrected_query"] = disambiguate_result["autocorrected_query"]

    @asynchronous
    def get(self, *args, **kwargs):
        # self.finish(
        #     {
        #         "q": self.query(),
        #         "outcomes": outcomes,
        #         "_id": data["msg_id"],
        #         "version": __version__,
        #         "timestamp": date.isoformat()
        #     }
        # )
        pass

    def type_match_score(self, _type_a, _type_b, multiple_key_matches):
        if _type_a == _type_b:
            return 1
        elif len({"lob", "division", "style"}.intersection([_type_a, _type_b])) == 2:
            return 0.999
        elif len({"lob", "division", "theme"}.intersection([_type_a, _type_b])) == 2:
            return 0.990
        elif len({"style", "theme"}.intersection([_type_a, _type_b])) == 2:
            return 0.999
        elif multiple_key_matches:
            return 0.8
        else:
            return 0.9

    def disambiguate(self, _type, key, suggested):
        disambiguated_outcomes = []
        if key in self.alias_data["en"]:
            for x in self.alias_data["en"][key]:
                # TODO can suggest flag be used for somehthing not sure
                confidence = 99.99999  # to make it out of 100

                confidence *= self.type_match_score(x["type"], _type, len(self.alias_data["en"][key]) > 1)

                if x["match_type"] == "alias":
                    confidence *= 1
                elif x["match_type"] == "spelling":
                    confidence *= 0.9

                disambiguated_outcomes.append(
                    {
                        "key": x["key"],
                        "type": x["type"],
                        "source": x["source"],
                        "display_name": x["display_name"],
                        "confidence": confidence
                    }
                )

        else:
            pass

        if not any(x for x in disambiguated_outcomes if x["key"] == key and x["type"] == _type):
            disambiguated_outcomes.append(
                {
                    "key": key,
                    "type": _type,
                    "source": "unknown",
                    "display_name": key,
                    "confidence": 20.0
                }
            )

        sorted_disambiguations = sorted(disambiguated_outcomes, key=lambda y: y["confidence"], reverse=True)

        ret = {
            "confidence": sorted_disambiguations[0]["confidence"],
            "key": sorted_disambiguations[0]["key"],
            "type": sorted_disambiguations[0]["type"],
            "source": sorted_disambiguations[0]["source"],
            "display_name": sorted_disambiguations[0]["display_name"]
        }

        if len(sorted_disambiguations) > 1:
            ret["disambiguate"] = sorted_disambiguations[1:]

        return ret

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
                        entity = self.disambiguate(_type, key, suggested)

                        # TODO this needs to be moved somewhere else preferably a seperate service call
                        entities.append(entity)

            outcomes.append(
                {
                    "confidence": outcome["confidence"] * 100,
                    "intent": outcome["intent"],
                    "entities": entities
                }
            )

        self.set_status(202)
        self.set_header("Location", "/%s" % data["msg_id"])
        self.finish()

        Worker(
            self.user_id(),
            self.application_id(),
            self.session_id(),
            ObjectId(data["msg_id"]),
            date,
            self.query(),
            self.skip_slack_log(),
            detection_type="wit",
            outcomes=outcomes
        ).start()

    def skip_slack_log(self):
        return self.get_argument("skip_slack_log", False)

    def query(self):
        original_q = self.get_argument("q", None)
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
            raise MissingArgumentError("q")
        else:
            return original_q

    def session_id(self):
        raw_session_id = self.get_argument("session_id", None)
        if not raw_session_id:
            self.set_status(412)
            self.finish(
                json_encode({
                    "status": "error",
                    "message": "missing param(s) session_id"
                }
                )
            )
            raise Finish()

        try:
            return ObjectId(raw_session_id)
        except InvalidId:
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=session_id,session_id=%s" % raw_session_id
                    }
                )
            )
            raise Finish()

    def application_id(self):
        raw_application_id = self.get_argument("application_id", None)
        if raw_application_id is None:
            self.set_status(412)
            self.finish(
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
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=application_id,application_id=%s" % raw_application_id
                    }
                )
            )
            raise Finish()

    def user_id(self):
        raw_user_id = self.get_argument("user_id", None)
        try:
            return ObjectId(raw_user_id) if raw_user_id is not None else None
        except InvalidId:
            self.set_status(412)
            self.finish(
                json_encode(
                    {
                        "status": "error",
                        "message": "invalid param=user_id,user_id=%s" % raw_user_id
                    }
                )
            )
            raise Finish()
