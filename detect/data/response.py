__author__ = 'robdefeo'
import logging
from detect.data.data import Data
from copy import deepcopy
from bson.code import Code
from bson.son import SON
from time import time


class Response(Data):
    LOGGER = logging.getLogger(__name__)
    collection_name = "responses"

    def insert(self, data):
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