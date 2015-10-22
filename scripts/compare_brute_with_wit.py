from bson import ObjectId
from tornado.escape import url_escape

__author__ = 'robdefeo'

from detect.data import ResponseData
import requests

response_data = ResponseData()
response_data.open_connection()

application_id = ObjectId()
session_id = ObjectId()
for wit_response in response_data.collection.find(
        {
            "version": "1.0.4",
            "type": "wit"
        }
):
    url = "http://0.0.0.0:18999/?application_id=%s&session_id=%s&locale=%s&q=%s" % (
        application_id,
        session_id,
        "en_UK",
        url_escape(wit_response["q"])
        # url_escape(json_encode(context))
    )
    post_response = requests.post(url)

    get_response = requests.get("http://0.0.0.0:18999%s" % post_response.headers["Location"])
    brute_response = get_response.json()
    pass
