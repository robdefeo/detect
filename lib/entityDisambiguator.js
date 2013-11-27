var vocabLoader = require('./vocabLoader');

exports.do = function (request, callback) {
  var result = {};
  result.detections = [];
  for (i in request.tokens){
    var token = request.tokens[i];
    if (token && !token.stopWord && (token.pos[0] == "J" | token.pos[0] == "N")){
      var item = vocabLoader.vocab[token.value.toLowerCase()]
      if (item) {
        var detection = {
          type: item.type,
          value: item.key,
          score: 1
        };
        result.detections.push(detection);        
      }
    }
    
  }
  callback(result);
};
