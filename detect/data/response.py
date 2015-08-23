from bson import ObjectId
from detect.settings import DATA_CACHE_SIZE_RESPONSE

__author__ = 'robdefeo'
import logging
from detect.data.data import Data
from copy import deepcopy
from bson.code import Code
from bson.son import SON
from time import time
from detect import __version__
from pylru import lrucache


class Response(Data):
    LOGGER = logging.getLogger(__name__)
    collection_name = "responses"
    cache = lrucache(DATA_CACHE_SIZE_RESPONSE)

    def get(self, detection_id: ObjectId):
        if detection_id in self.cache:
            return self.cache[detection_id]
        else:
            item = next(self.collection.find({"_id": detection_id}), None)
            self.cache[detection_id] = item
            return item

    def insert(self, user_id: ObjectId, application_id: ObjectId, session_id: ObjectId,
               detection_id: ObjectId, detection_type, date, query, tokens=None, detections=None,
               non_detections=None, outcomes=None):
        data = {
            "_id": detection_id,
            "session_id": session_id,
            "application_id": application_id,
            "version": __version__,
            "timestamp": date.isoformat(),
            "q": query,
            "type": detection_type
        }
        if outcomes is not None:
            data["outcomes"] = outcomes
        if non_detections is not None:
            data["non_detections"] = non_detections
        if detections is not None:
            data["detections"] = detections
        if tokens is not None:
            data["tokens"] = tokens
        if user_id is not None:
            data["user_id"] = user_id

        self.collection.insert(data)
        self.cache[detection_id] = data

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