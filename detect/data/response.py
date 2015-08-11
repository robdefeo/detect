from bson import ObjectId

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

    def get(self, detection_id: ObjectId):
        docs = self.collection.find({"_id": detection_id})

        return next(docs, None)

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

        self.collection.insert(data, )

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