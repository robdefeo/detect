var _ = require('underscore');
var natural = require('natural');
var vocabLoader;
var getItem = function(term){  
  var item = vocabLoader.vocab[term.toLowerCase()]  
  if (item){
    var detection = {
      type: item.type,
      value: item.key,
      method: "exact"
    };
    
    return detection;
  }else {
    var distanceItem = _.max(vocabLoader.vocab, function(item){ 
      return -natural.LevenshteinDistance(term,item.key); 
    });

    if (typeof(distanceItem) !== 'undefined' && typeof(distanceItem.key) !== 'undefined' && natural.LevenshteinDistance(term,distanceItem.key) <= term.length / 5) {
      var detection = {
        type: distanceItem.type,
        value: distanceItem.key,
        method: "levenshtein"
      };
      return detection;
    }
    
  }
}
exports.do = function (request, p_vocabLoader, callback) {
  vocabLoader = p_vocabLoader;
  var result = {};
  result.detections = [];
  result.nonDetections = [];
  for (i = 0;i<request.tokens.length;i++){
    var token = request.tokens[i];
    //TODO here is the problem
    var tokenTwo = request.tokens[parseInt(i)+1];
    if (tokenTwo
      && !token.stopWord && (token.pos[0] == "J" | token.pos[0] == "N" | token.pos[0] == "V")
      && !tokenTwo.stopWord && (tokenTwo.pos[0] == "J" | tokenTwo.pos[0] == "N" | tokenTwo.pos[0] == "V")
      && getItem(token.value + " " + tokenTwo.value)
      ){
        var biItem = getItem(token.value + " " + tokenTwo.value);
        if (biItem) {
          // skip next token
          i++;
          result.detections.push(biItem);        
        }  
    } else {
      
      if (token && !token.stopWord && (token.pos[0] == "J" | token.pos[0] == "N")){
        var item = getItem(token.value);
        if (item) {
          result.detections.push(item);        
        } else {
          // not detected
          result.nonDetections.push(token)
        }      
      } else{
        // not a relevant word as of now.
        
      }
    }
    
  }
  callback(result);
};
