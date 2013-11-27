var 
  express = require('express'),
  pos = require('pos'),
  preProcess = require('./lib/preProcess'),
  // colourDetector = require('./lib/colourDetector'),
  disambiguator = require('./lib/entityDisambiguator');
  // materialDetector = require('./lib/materialDetector')

var app = express();

app.use(express.bodyParser());


// app.param('collectionName', function(req, res, next, collectionName){
//   req.collection = db.collection(collectionName)
//   return next()
// })
app.get('/', function(req, res) {
  var q = req.param('q');
  if (!q){
    res.status(412).json({error: "Missing parameter: 'q'"});
  } else {
    preProcess.do(q, function(preResult){
      disambiguator.do(preResult, function(disambiguatorResult){
        res.json({
          tokens: preResult.tokens,
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
