var 
  express = require('express'),
  pos = require('pos'),
  preProcess = require('./lib/preProcess'),
  disambiguator = require('./lib/entityDisambiguator'),
  pjson = require('./package.json'),
  uuid = require('uuid'),
  mongoClient = require('mongodb').MongoClient,
  nodemailer = require("nodemailer"),
  _ = require("underscore"),
  vocabLoader = require('./lib/vocabLoader');
  
var app = express();
var mongoUri = process.env.MONGOHQ_DETECTION_URL || "mongodb://localhost/detection" 

var db;
mongoClient.connect(mongoUri, function (err, connectDb) {
  if (err) {
    console.error("app=detection,resource=mongo,error=%s", err);
  }
  db = connectDb;
});


var logResponse = function(detectionId, q, preProcessingResponse, disambiguatorResponse) {  
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
        console.err("app=detection,resource=mongo,error=%s", err);
      }
  });
};

app.use(express.bodyParser());
app.use(express.compress());

app.get('/status', function(req, res) {
  res.json({
    self: vocabLoader.status().self,
    info: vocabLoader.status(),
    version: pjson.version
  });
});

app.get('/', function(req, res) {
  var q = req.param('q');
  var detectionId = uuid.v4();
  res.header("Access-Control-Allow-Origin", "*");
  // TODO: limit this based on environement or multiple but not *
  // res.header("Access-Control-Allow-Origin", "http://localhost:5000");
    // res.header("Access-Control-Allow-Origin", "http://jemboo.com");
  console.log("app=detection,module=app,function=get,q=%s", q);
  if (!q) {
    res.status(412).json({error: "Missing parameter: 'q'"});
  } 
  
  preProcess.do(q, function(preProcessingResponse){
    disambiguator.do(preProcessingResponse, vocabLoader, function(disambiguatorResponse){
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

});

app.use(function(err, req, res, next){
  if (err){
    var errJson = {error: err.message, stack: err.stack};
    console.error("app=detection,error=%s", JSON.stringify(errJson));
    res.send(500, 
      errJson
    );

    // create reusable transport method (opens pool of SMTP connections)
    var smtpTransport = nodemailer.createTransport("SMTP",{
        service: "Gmail",
        auth: {
            user: process.env.MAIL_USER || "admin@jemboo.com",
            pass: process.env.MAIL_PASSWORD || "none"
        }
    });

    // setup e-mail data with unicode symbols
    var mailOptions = {
        from: process.env.MAIL_FROM || "errors@jemboo.com", // sender address
        to: process.env.MAIL_TO || "robdefeo@gmail.com", // list of receivers
        subject: "Error: dection", // Subject line
        text: JSON.stringify({
          error: errJson,
          request: {
            headers: req.headers,
            url: req.url,
            methond: req.method
            }
          }, null, 2)
        // html: "<b>Hello world ✔</b>" // html body
    }

    // send mail with defined transport object
    smtpTransport.sendMail(mailOptions, function(error, response){
        if(error){
            console.error(error);
        }
        // if you don't want to use this transport object anymore, uncomment following line
        smtpTransport.close(); // shut down the connection pool, no more messages
    });
  }else{
    next();
  }
});

var port = process.env.PORT || 5001;
app.listen(port, function() {
  console.log("app=detection,port=%d,mode=%s,action=started", port, app.settings.env);
});
