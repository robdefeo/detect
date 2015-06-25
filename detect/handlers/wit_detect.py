from datetime import datetime

from bson import ObjectId
from tornado.escape import json_encode, json_decode, url_escape
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.log import app_log
from tornado.web import RequestHandler, asynchronous

from detect.settings import WIT_TOKEN, WIT_URL, WIT_URL_VERSION
from detect import __version__
from detect.workers.worker import Worker


__author__ = 'robdefeo'


class WitDetect(RequestHandler):
    def initialize(self, alias_data):
        self.alias_data = alias_data

    def on_finish(self):
        pass

    @asynchronous
    def get(self):
        self.set_header('Content-Type', 'application/json')
        original_q = self.get_argument("q", None)
        user_id = self.get_argument("user_id", None)
        session_id = self.get_argument("session_id", None)
        application_id = self.get_argument("application_id", None)

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
            r = HTTPRequest(
                "%smessage?v=%s&q=%s&msg_id=%s" % (WIT_URL, WIT_URL_VERSION, url_escape(original_q), str(detection_id)),
                headers={
                    "Authorization": "Bearer %s" % WIT_TOKEN
                }
            )
            client = AsyncHTTPClient()
            client.fetch(r, callback=self.wit_call_back)

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
        self.finish(
            {
                "q": self.q(),
                "outcomes": outcomes,
                "_id": data["msg_id"],
                "version": __version__,
                "timestamp": date.isoformat()
            }
        )

        Worker(
            self.user_id(),
            self.application_id(),
            self.session_id(),
            ObjectId(data["msg_id"]),
            date,
            self.q(),
            self.skip_mongodb_log(),
            self.skip_slack_log(),
            detection_type="wit",
            outcomes=outcomes
        ).start()

    def skip_mongodb_log(self):
        return self.get_argument("skip_mongodb_log", False)

    def skip_slack_log(self):
        return self.get_argument("skip_slack_log", False)

    def q(self):
        return self.get_argument("q", None)

    def user_id(self):
        user_id = self.get_argument("user_id", None)
        return ObjectId(user_id) if user_id is not None else None

    def session_id(self):
        return ObjectId(self.get_argument("session_id"))

    def application_id(self):
        return ObjectId(self.get_argument("application_id"))