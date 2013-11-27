var 
  express = require('express'),
  pos = require('pos'),
  preProcess = require('./lib/preProcess'),
  colourDetector = require('./lib/colourDetector'),
  materialDetector = require('./lib/materialDetector')

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
      colourDetector.do(preResult, function(colourDetectionResult){
        res.json({
          tokens: preResult.tokens,
          detections: colourDetectionResult.detections
        });        
      });
    });
  }
})


var port = process.env.PORT || 5001;
app.listen(port, function() {
  console.log("Express server listening on port %d in %s mode", port, app.settings.env);
});
