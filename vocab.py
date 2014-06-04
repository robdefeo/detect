from pymongo import MongoClient
from settings import MONGO_DB_URI, MONGO_DB_PRODUCT_NAME
from bson.code import Code
from bson.son import SON

conn = MongoClient(MONGO_DB_URI)
db = conn[MONGO_DB_PRODUCT_NAME]

def generate():
  mapper = Code(open('generate_map.js', 'r').read())
  reducer = Code(open('generate_reduce.js', 'r').read())

  result = db.product.map_reduce(
    mapper,
    reducer,
    out=SON([
      ("replace", "vocab"),
      ("db", "detection")
    ])
  )
