var 
  mongoClient = require('mongodb').MongoClient,
  _ = require('underscore'),
  natural = require('natural');

var mongoUri = process.env.MONGOHQ_GETTER_URL || "mongodb://localhost:27017/getter";

// natural.PorterStemmer.attach();
// natural.Metaphone.attach();

var vocab = {};
// var stemPhoneticVocab = {};

var materialsDone = false;
var coloursDone = false;
var stylesDone = false;

var styleMap = function() {
 for (var i = 0; i < this.shoe.categories.length; i++) {
   var possibleItems = this.shoe.categories[i]
     .replace(" and ", "/")
     .replace(" n ", "/")
     .replace(" - ", "/")
     .split(/[(\_)(\/)(,)(\&)(\+)]/);
     for (var itemIndex = 0; itemIndex < possibleItems.length; itemIndex++) {
       var possibleItem = possibleItems[itemIndex].trim().toLowerCase();
       if(possibleItem != "") {
         emit(possibleItem, 1);
       }
     }
  }
};
var materialMap = function() {
  for (var i = 0; i < this.shoe.attributes.length; i++) {
    if (this.shoe.attributes[i].key.toLowerCase().indexOf("material") != -1){
      var possibleItems = this.shoe.attributes[i].value
        .replace(" and ", "/")
        .replace(" n ", "/")
        .replace(" - ", "/")
        .split(/[(\_)(\/)(,)(\&)(\+)]/);

      for (var materialIndex = 0; materialIndex < possibleItems.length; materialIndex++) {
        var possibleItem = possibleItems[materialIndex].trim().toLowerCase();
        if(possibleItem != "") {
          emit(possibleItem, 1);
        }
      } 
    };     
  }
};
var colourMap = function() {
  for (var i = 0; i < this.shoe.attributes.length; i++) {
    if (this.shoe.attributes[i].key.toLowerCase() == "colour"){
      var possibleItems = this.shoe.attributes[i].value
        .replace(" and ", "/")
        .replace(" n ", "/")
        .replace(" - ", "/")
        .split(/[(\_)(\/)(,)(\&)(\+)]/);
      
      for (var colourIndex = 0; colourIndex < possibleItems.length; colourIndex++) {
        var possibleColour = possibleItems[colourIndex].trim().toLowerCase();
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
var addVocabItem = function(item){
  if (vocab[item.key]){    
    console.log("vocab conflict: " + item.key + ":" + item.type + ":" + item.count + ":" + vocab[item.key].type + ":" + vocab[item.key].count  )
  } else {
    vocab[item.key] = item;
  }
};
// var addStemVocabTerm = function(item){
//   var itemKey = item.key.stem().phonetics()
//   console.log(itemKey);
//   if (stemPhoneticVocab[itemKey]){    
//     stemPhoneticVocab[itemKey].push(item);    
//   }else{
//     stemPhoneticVocab[itemKey] = [item];    
//   }
// };
var addTerm = function(item){
  addVocabItem(item);
  // addStemVocabTerm(item);
};
var exportData = function(){
  exports.vocab = vocab; 
  // exports.stemPhoneticVocab = stemPhoneticVocab; 
};
var populateColours = function(db) {
  db.collection('shoes').mapReduce(
    colourMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {    
      if (err){
          throw err;
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "colour"
        };
        addTerm(item);
      } 
      console.log("coloursVocab loaded:");      
      exportData();
    }
  );
};
var populateMaterials = function(db) {
  db.collection('shoes').mapReduce(
    materialMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
          throw err;
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "material"
          
        };
        addTerm(item);
      } 
      console.log("materialsVocab loaded:");
      exportData(); 
    }
  );
};
var populateStyles = function(db) {
  db.collection('shoes').mapReduce(
    styleMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
          throw err;
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "style"
          
        };
        addTerm(item);
      } 
      console.log(results);
      console.log("stylesVocab loaded:");
      exportData();
    }
  );
};

mongoClient.connect(mongoUri, function (err, db) {
  if (err){
      throw err;
  }  
  populateMaterials(db);
  populateColours(db);
  populateStyles(db);
});
