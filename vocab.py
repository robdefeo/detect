from pymongo import MongoClient
from settings import MONGO_DB_URI, MONGO_DB_PRODUCT_NAME, MONGO_DB_DETECTION_NAME, MONGO_COLLECTION_VOCAB_NAME
from bson.son import SON
from bson.code import Code

conn = MongoClient(MONGO_DB_URI)
product_db = conn[MONGO_DB_PRODUCT_NAME]
detection_db = conn[MONGO_DB_DETECTION_NAME]
data = {}

def generate():
  mapper = Code(open('generate_map.js', 'r').read())
  reducer = Code(open('generate_reduce.js', 'r').read())

  result = product_db.product.map_reduce(
    mapper,
    reducer,
    out=SON([
      ("replace", MONGO_COLLECTION_VOCAB_NAME),
      ("db", MONGO_DB_DETECTION_NAME)
    ])
  )

def load():
  cursor = detection_db[MONGO_COLLECTION_VOCAB_NAME].find(batch_size=10000)

  for doc in cursor:
    data_key = doc["_id"]["value"]
    if data_key in data:
      existing_item = next((x for x in data[data_key] if x["type"] == doc["_id"]["type"]), None)
      if existing_item == None:
        data[data_key].append({
          "type": doc["_id"]["type"],
          "value": doc["_id"]["value"],
          "score": doc["value"]
        })
      else:
        existing_item["score"] = doc["value"]

    else:
      data[data_key] = [
        {
          "type": doc["_id"]["type"],
          "value": doc["_id"]["value"],
          "score": doc["value"]
        }
      ]


  return data
