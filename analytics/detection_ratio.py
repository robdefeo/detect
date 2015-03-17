import requests
import logging
__author__ = 'robdefeo'

logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.info("started")
from detect.data.response import Response
data = Response()
data.open_connection()
responses = data.collection.find(
    # {
    #     non_detections: {
    #         $not: {$size: 0}
    #     },
    #     timestamp: {
    #         $gt: "2015-02-12T00:00:00"
    #     }
    # },
    # {
    #     non_detections: 1,
    #     q: 1
    # }
)
queries_dict = {

}
response_count = 0
for x in responses:
    response_count+=1
    queries_dict[x["q"]] = 1

queries = list(queries_dict.keys())
queries_with_non_detections = 0
detection_responses = {}
non_detections = {}
non_detection_count = 0
for query in queries:
    url = "http://0.0.0.0:18999/?q=%s&session_id=session_id_value&skip_slack_log=True&skip_mongodb_log=True" % query
    detection_response = requests.get(url).json()
    detection_responses[query] = detection_response
    if any(detection_response["non_detections"]):
        queries_with_non_detections += 1
        for x in detection_response["non_detections"]:
            non_detection_count += 1
            if x in non_detections:
                non_detections[x]["value"] += 1
                non_detections[x]["queries"].append(query)
            else:
                non_detections[x] = {
                    "key": x,
                    "value": 1,
                    "queries": [query]
                }

logger.info(
    """
Total_queries=%s
Unique_queries=%s
Unique_queries_with_non_detections=%s
Failed_complete_detection=%s
Total_non_detections=%s
Unique_non_detections=%s
    """,
    response_count,
    len(queries),
    queries_with_non_detections,
    (queries_with_non_detections / len(queries)) * 100,
    non_detection_count,
    len(non_detections)
)

from operator import itemgetter
for x in sorted(non_detections.values(), key=itemgetter("value"), reverse=True)[:100]:
    for y in x["queries"]:
        logger.info(
            "value=%s,count=%s,query=%s",
            x["key"],
            x["value"],
            y
        )

pass
# try detection with skip logging
# increment counters
# log failures
# summary