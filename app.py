import parse
import vocab
import traceback
from flask import Flask, jsonify, request, abort
from flask.ext.cors import cross_origin
from bson.objectid import ObjectId

app = Flask(__name__)

data = vocab.load()

@app.route('/vocab/generate/', methods = ['POST'])
def vocab_generate():
  vocab.generate()
  resp = jsonify({
    "status": "ok"
  })
  resp.status_code = 200
  return resp

@app.route('/vocab/load/', methods = ['POST'])
def vocab_load():
  data = vocab.load()
  resp = jsonify({
    "status": "ok"
  })
  resp.status_code = 200
  return resp

@app.route('/', methods = ['GET'])
@cross_origin()
def api_root():
  try:
    q = request.args.get("q")
    sessionID = request.args.get("sessionID")
    detectionID = ObjectId()

    print "app=detection,module=app,function=get,detectionId=%s,sessionID=%s,q=%s" % (detectionID, sessionID, q)
    if not q or not sessionID:
      resp = jsonify({
        "status": "error",
        "message": "missing param(s)"
      })
      resp.status_code = 412
      return resp
    else:
      preprocessResult = parse.preperation(q)
      disambiguateResult = parse.disambiguate(data, preprocessResult)
      print disambiguateResult
      log = {
        "detectionId": str(detectionID),
        "tokens": preprocessResult["tokens"],
        "detections": disambiguateResult["detections"],
        "nonDetections": disambiguateResult["nonDetections"]
      }
      res = {
        "detectionId": str(detectionID),
        # version: pjson.version,
        "detections": disambiguateResult["detections"],
        "nonDetections": disambiguateResult["nonDetections"]
      }
      resp = jsonify(res)
      resp.status_code = 200
      return resp
  except Exception,e:
    print "error=%s" % (traceback.format_exc())
    resp = jsonify({
      "status": "error",
      "exception": traceback.format_exc()
    })
    resp.status_code = 500
    return resp


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
    # print "app=detection,port=%d,mode=%s,action=started", port, app.settings.env)
