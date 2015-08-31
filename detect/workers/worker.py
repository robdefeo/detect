import threading
from bson import ObjectId
import slack
import slack.chat
from detect.settings import SLACK_API_TOKEN, ENABLE_MONGO_LOG
from tornado.log import app_log


class Worker(threading.Thread):
    def __init__(self, user_id: ObjectId, application_id: ObjectId, session_id: ObjectId, detection_id: ObjectId, date, query, skip_slack_log, detection_type, tokens=None, detections=None, non_detections=None, outcomes=None,  callback=None, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.callback = callback
        self.user_id = user_id
        self.application_id = application_id
        self.session_id = session_id
        self.detection_id = detection_id
        self.tokens = tokens
        self.detections = detections
        self.non_detections = non_detections
        self.date = date
        self.query = query
        self.detection_type = detection_type
        self.outcomes = outcomes

        self.skip_slack_log = skip_slack_log

    def run(self):
        low_confidence_intents = [x for x in self.outcomes if x["confidence"] <= 20]
        low_confidence_entities = [x for x in self.outcomes if x["entities"][0]["confidence"] <= 20]
        if (any(low_confidence_intents) or any(low_confidence_entities)) and not self.skip_slack_log:
            slack.api_token = SLACK_API_TOKEN
            message = "q=%s" % self.query
            fields = []
            for x in low_confidence_intents:
                fields.append(
                    {
                        "title": "Intent",
                        "value": {
                            "confidence": x["confidence"],
                            "intent": x["intent"]
                        }
                    }
                )
            for x in low_confidence_entities:
                entity = x["entities"][0]
                fields.append(
                    {
                        "title": "Entity",
                        "value": "confidence=%s,type=%s,key=%s,source=%s" % (
                            entity["confidence"], entity["type"], entity["key"], entity["source"]
                        )
                    }
                )
            slack.chat.post_message(
                '#failed_detections',
                message,
                attachments=[
                    {
                        "fallback": message,
                        "text": message,
                        "fields": fields,
                        "color": "danger"
                    }
                ],
                username='detection'
            )

        if self.callback:
            self.callback('DONE')