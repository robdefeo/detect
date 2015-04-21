from bson import ObjectId
from tornado.escape import json_encode, json_decode, url_escape
from tornado.httpclient import HTTPRequest, AsyncHTTPClient, HTTPClient
from tornado.log import app_log
from tornado.web import RequestHandler, asynchronous
from detect.settings import WIT_TOKEN, WIT_URL, WIT_URL_VERSION

__author__ = 'robdefeo'



class WitDetect(RequestHandler):
    def initialize(self, alias_data):
        self.alias_data = alias_data
        pass

    def on_finish(self):
        pass

    @asynchronous
    def get(self):
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
            r = HTTPRequest(
                "%smessage?v=%s&q=%s&msg_id=%s" % (WIT_URL, WIT_URL_VERSION, url_escape(original_q), str(detection_id)),
                headers={
                    "Authorization": "Bearer %s" % WIT_TOKEN
                }
            )
            client = AsyncHTTPClient()
            client.fetch(r, callback=self.wit_call_back)
    #         # client = HTTPClient()
    #         # response = client.fetch(r)
    #
    #         get_message_request = HTTPRequest(
    #             "%smessages/%s?v=%s" % (WIT_URL, str(detection_id), WIT_URL_VERSION),
    #             headers={
    #                 "Authorization": "Bearer %s" % WIT_TOKEN
    #             }
    #         )
    #         client = AsyncHTTPClient()
    #         client.fetch(get_message_request, callback=self.wit_get_message_call_back)
    #
    # def wit_get_message_call_back(self, response):
    #     data = json_decode(response.body)
    #     outcomes = []
    #     for outcome in data["outcomes"]:
    #         entities = []
    #         for _type in outcome["entities"].keys():
    #             for value in outcome["entities"][_type]:
    #                 key = value["value"]["value"] if type(value["value"]) is dict else value["value"]
    #                 entities.append(
    #                     {
    #                         "type": value["entity"],
    #                         "role": value["role"],
    #                         "key": key
    #                     }
    #                 )
    #
    #         outcomes.append(
    #             {
    #                 "confidence": outcome["confidence"],
    #                 "intent": outcome["intent"],
    #                 "entities": entities
    #             }
    #         )
    #     self.finish(
    #         {
    #             "q": self.get_argument("q", None),
    #             "outcomes": outcomes
    #         }
    #     )
    #     pass

    def disambiguate(self, _type, key):
        disambiguated_outcomes = []
        if key in self.alias_data["en"]:
            for x in self.alias_data["en"][key]:
                confidence = 0.999
                if x["type"] == _type:
                    confidence *= 1
                else:
                    confidence *= 0.8

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

        return {
            "type": _type,
            "key": key,
            "disambiguated_outcomes": sorted(disambiguated_outcomes, key=lambda y: y["confidence"], reverse=True)
        }


    def wit_call_back(self, response):
        data = json_decode(response.body)

        outcomes = []

        for outcome in data["outcomes"]:
            entities = []
            for _type in outcome["entities"].keys():
                if _type not in ["polite"]:
                    for value in outcome["entities"][_type]:
                        key = value["value"]["value"] if type(value["value"]) is dict else value["value"]
                        entity = self.disambiguate(_type, key)
                        #TODO this needs to be moved somewhere else preferably a seperate service call
                        entities.append(entity)

            outcomes.append(
                {
                    "confidence": outcome["confidence"],
                    "intent": outcome["intent"],
                    "entities": entities
                }
            )
        self.finish(
            {
                "q": self.get_argument("q", None),
                "outcomes": outcomes,
                "_id": data["msg_id"]
            }
        )
        pass