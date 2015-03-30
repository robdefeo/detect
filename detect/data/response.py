__author__ = 'robdefeo'
import logging
from detect.data.data import Data
from copy import deepcopy
from bson.code import Code
from bson.son import SON
from time import time
from detect import __version__

class Response(Data):
    LOGGER = logging.getLogger(__name__)
    collection_name = "responses"

    def insert(self, user_id, application_id, session_id, detection_id, tokens, detections, non_detections, date, query):
        data = {
            "_id": detection_id,
            "session_id": session_id,
            "application_id": application_id,
            "tokens": tokens,
            "detections": detections,
            "non_detections": non_detections,
            "version": __version__,
            "timestamp": date.isoformat(),
            "q": query
        }
        if user_id is not None:
            data["user_id"] = user_id

        self.collection.insert(data)

    def map_reduce_typeahead(self):
        mapper = Code("""
        function(
            emit(this.q.toLowerCase(), 1);
        )
        """)
        reducer = Code("""
        function(key, values){
            return values.length
        }
        """)

        result = self.collection.map_reduce(
            mapper,
            reducer,
            query={
                "non_detections": {
                    "$size": 0
                },
                "detections": {
                    "$not": {
                        "$size": 0
                    }
                }
            },
            out=SON(
                [
                    ("replace", "typeahead_suggestions")
                    # , ("db", "outdb")
                ]
            )
        )

        return result