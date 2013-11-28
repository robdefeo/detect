var 
  natural = require('natural'),
  _ = require('underscore'),
  pos = require('pos');

// all domain stop words
natural.stopwords.push('shoe');
natural.stopwords.push('shoes');
natural.stopwords.push('I');

natural.PorterStemmer.attach();
natural.Metaphone.attach();
var tokenizer = new natural.WordTokenizer();

exports.do = function (q, callback) {
  var result = {};
  result.q = q;
  var rawTokens = new pos.Lexer().lex(q);
  var taggedWords = new pos.Tagger().tag(rawTokens);
  
  result.tokens = []
  for (i in rawTokens) {
    var word = rawTokens[i];
    var token = {
      value: word,
      pos: taggedWords[i][1],
      stem: word.stem(),
      phonetic: word.phonetics(),
      stemPhonetic: word.stem().phonetics(),
      stopWord: _.contains(natural.stopwords, word)
    }
    result.tokens.push(token);
  }  
  
  callback(result);
}