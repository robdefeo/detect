var 
  mongoClient = require('mongodb').MongoClient,
  _ = require('underscore');

var mongoUri = process.env.MONGOHQ_SCRAPE_URL || "mongodb://localhost:27017/getter";

var colours = {};

var map = function() {
  for (var i = 0; i < this.shoe.attributes.length; i++) {
    if (this.shoe.attributes[i].key.toLowerCase() == "colour"){
      var possibleColours = this.shoe.attributes[i].value
      .replace(" and ", "/")
      .replace(" n ", "/")
      .split(/[(\-)(\_)(\/)(,)(\&)]/);
      for (var colourIndex = 0; colourIndex < possibleColours.length; colourIndex++) {
        var possibleColour = possibleColours[colourIndex].trim().toLowerCase();
        if(possibleColour != "") {
          emit(possibleColour, 1);
        }
      } 
    };     
  }
};

var reduce = function (key, values) {
  return Array.sum(values);
};


mongoClient.connect(mongoUri, function (err, db) {
  if (err){
      throw err;
  }
  
  db.collection('shoes').mapReduce(
    map,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {    
      for (i in results) {
        colours[results[i]._id] = { 
          value: results[i].value, 
          key: results[i]._id
        }
      } 
      exports.colours = colours; 
    }
  );    
});

exports.do = function (request, callback) {
  var result = {};
  result.detections = [];
  for (i in request.tokens){
    var token = request.tokens[i];
    if (token && !token.stopWord && (token.pos[0] == "J" | token.pos[0] == "N")){
      var item = colours[token.value.toLowerCase()]
      if (item) {
        var detection = {
          type: "colour",
          value: item.key,
          score: 1
        };
        result.detections.push(detection);        
      }
    }
    
  }
  callback(result);
};
