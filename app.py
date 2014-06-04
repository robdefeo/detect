import preProcess
import vocab

from flask import Flask, jsonify
app = Flask(__name__)


@app.route('/generateVocab/', methods = ['POST'])
def vocab_generate():
  vocab.generate()
  resp = jsonify({
    "status": "ok"
  })
  resp.status_code = 200
  return resp

@app.route('/', methods = ['GET'])
def api_root():
  preprocessResult = preProcess.tag("And now for something completely different")
  resp = jsonify(preprocessResult)
  resp.status_code = 200
  return resp

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
    # print "app=detection,port=%d,mode=%s,action=started", port, app.settings.env)
