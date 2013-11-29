var 
  express = require('express'),
  pos = require('pos'),
  preProcess = require('./lib/preProcess'),
  disambiguator = require('./lib/entityDisambiguator'),
  pjson = require('./package.json'),
  uuid = require('uuid'),
  mongoClient = require('mongodb').MongoClient

var app = express();
var mongoUri = process.env.MONGOHQ_DETECTION_URL || "mongodb://localhost/detection" 

var logResponse = function(detectionId, q, preProcessingResponse, disambiguatorResponse) {
  mongoClient.connect(mongoUri, function (err, db) {
    if (err) {
      return console.dir(err);
    }
    var data = {
      _id: detectionId,
      q: q,
      timestamp: new Date().toISOString(),
      tokens: preProcessingResponse.tokens,
      detections: disambiguatorResponse.detections,
      nonDetections: disambiguatorResponse.nonDetections
    };
    db.collection("responses").insert(
      data,
      { 
        safe: true
      },
      function (err, response){
        if (err) {
          return console.dir(err);
        }
    });
  });
};

app.use(express.bodyParser());

app.get('/status', function(req, res) {
  res.json({
    self: "up",
    version: pjson.version
  });
});

app.get('/', function(req, res) {
  var q = req.param('q');
  var detectionId = uuid.v4();
  res.header("Access-Control-Allow-Origin", "*");
  // TODO: limit this based on environement or multiple but not *
  // res.header("Access-Control-Allow-Origin", "http://localhost:5000");
  if (!q) {
    res.status(412).json({error: "Missing parameter: 'q'"});
  } else {
    console.log("received: " + q);
    preProcess.do(q, function(preProcessingResponse){
      disambiguator.do(preProcessingResponse, function(disambiguatorResponse){
        res.json({
          detectionId: detectionId,
          tokens: preProcessingResponse.tokens,
          version: pjson.version,
          detections: disambiguatorResponse.detections,
          nonDetections: disambiguatorResponse.nonDetections
        }); 
        
        logResponse(detectionId, q, preProcessingResponse, disambiguatorResponse);       
      });
    });
  }
});


var port = process.env.PORT || 5001;
app.listen(port, function() {
  console.log("Express server listening on port %d in %s mode", port, app.settings.env);
});
