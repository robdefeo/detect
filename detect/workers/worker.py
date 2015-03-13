import threading
import slack
import slack.chat
from detect.settings import SLACK_API_TOKEN


class Worker(threading.Thread):
    def __init__(self, log, callback=None, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.callback = callback
        self.log = log

    def write_to_mongo(self):
        from detect.data.response import Response
        data_response = Response()
        data_response.open_connection()
        data_response.insert(self.log)
        data_response.close_connection()

    def run(self):
        self.write_to_mongo()

        if any(self.log["non_detections"]):
            slack.api_token = SLACK_API_TOKEN
            slack.chat.post_message(
                '#failed_detections',
                "q=%s,non_detections=%s" % (self.log["q"], self.log["non_detections"]),
                username='detection'
            )

        if self.callback:
            self.callback('DONE')