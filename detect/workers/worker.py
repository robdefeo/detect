import threading
import slack
import slack.chat
from detect.settings import SLACK_API_TOKEN, ENABLE_MONGO_LOG
from tornado.log import app_log


class Worker(threading.Thread):
    def __init__(self, user_id, application_id, session_id, detection_id, date, query, skip_mongodb_log, skip_slack_log, detection_type, tokens=None, detections=None, non_detections=None, outcomes=None,  callback=None, *args, **kwargs):
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

        self.skip_mongodb_log = skip_mongodb_log
        self.skip_slack_log = skip_slack_log


    def write_to_mongo(self):
        if ENABLE_MONGO_LOG and not self.skip_mongodb_log:
            from detect.data.response import Response
            data_response = Response()
            data_response.open_connection()
            data_response.insert(self.user_id, self.application_id, self.session_id, self.detection_id,
                                 self.detection_type, self.date, self.query, self.tokens,
                                 self.detections, self.non_detections, outcomes=self.outcomes)
            data_response.close_connection()
        else:
            app_log.warn("Mongo is not enabled")

    def run(self):
        self.write_to_mongo()

        if self.non_detections is not None and any(self.non_detections) and not self.skip_slack_log:
            slack.api_token = SLACK_API_TOKEN
            slack.chat.post_message(
                '#failed_detections',
                "q=%s,non_detections=%s" % (self.query, self.non_detections),
                username='detection'
            )

        if self.callback:
            self.callback('DONE')