var vocabLoader = require('./vocabLoader');
var _ = require('underscore');
var natural = require('natural');

var getItem = function(term){
  
  var item = vocabLoader.vocab[term.toLowerCase()]
  if (item){
    var detection = {
      type: item.type,
      value: item.key,
      score: 1
    };
    console.log("found "+ term);
    return detection;
  }else {
    // natural.LevenshteinDistance("ones","onez")
    var distanceItem = _.max(vocabLoader.vocab, function(item){ 
      return -natural.LevenshteinDistance(term,item.key); 
    });
    console.log(term + ":" + distanceItem.key + natural.LevenshteinDistance(term,distanceItem.key));
    if (natural.LevenshteinDistance(term,distanceItem.key) <= term.length / 5) {
      var detection = {
        type: distanceItem.type,
        value: distanceItem.key,
        score: 0.9
      };
      return detection;
    }
    
  }
}
exports.do = function (request, callback) {
  var result = {};
  result.detections = [];
  for (i = 0;i<request.tokens.length;i++){
    var token = request.tokens[i];
    var tokenTwo = request.tokens[parseInt(i)+1];
    if (tokenTwo
      && !token.stopWord && (token.pos[0] == "J" | token.pos[0] == "N")
      && !tokenTwo.stopWord && (tokenTwo.pos[0] == "J" | tokenTwo.pos[0] == "N")
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
          // // natural.LevenshteinDistance("ones","onez")
          // var distanceItems = _.sortBy(vocabLoader.vocab, function(item){ 
          //   return -natural.JaroWinklerDistance(token.value,item.key); 
          // });
          // console.log("not found: "+ token.value);
          // console.log(distanceItems[0].key  + natural.JaroWinklerDistance(token.value,distanceItems[0].key));
          // console.log(distanceItems[1].key + natural.JaroWinklerDistance(token.value,distanceItems[1].key));
          // console.log(distanceItems[2].key + natural.JaroWinklerDistance(token.value,distanceItems[2].key));
          // // var stemItem = vocabLoader.stemPhoneticVocab[token.stemPhonetic]
          // //          console.log("found: " + stemItem);
          // //          console.dir(stemItem);
        }      
      }
    }
    
  }
  callback(result);
};
