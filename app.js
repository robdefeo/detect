var 
  express = require('express'),
  pos = require('pos'),
  preProcess = require('./lib/preProcess'),
  disambiguator = require('./lib/entityDisambiguator');
  var pjson = require('./package.json');

var app = express();

app.use(express.bodyParser());

app.get('/', function(req, res) {
  var q = req.param('q');
  res.header("Access-Control-Allow-Origin", "*");
  // TODO: limit this based on environement or multiple but not *
  // res.header("Access-Control-Allow-Origin", "http://localhost:5000");
  if (!q){
    res.status(412).json({error: "Missing parameter: 'q'"});
  } else {
    console.log("received: " + q);
    preProcess.do(q, function(preResult){
      disambiguator.do(preResult, function(disambiguatorResult){
        res.json({
          // tokens: preResult.tokens,
          version: pjson.version,
          detections: disambiguatorResult.detections
        });        
      });
    });
  }
})


var port = process.env.PORT || 5001;
app.listen(port, function() {
  console.log("Express server listening on port %d in %s mode", port, app.settings.env);
});
