var 
  mongoClient = require('mongodb').MongoClient,
  _ = require('underscore'),
  natural = require('natural');

var mongoUri = process.env.MONGOHQ_GETTER_URL || "mongodb://localhost:27017/getter";



var vocab = {};

var materialsDone = false;
var coloursDone = false;
var stylesDone = false;
var brandMap = function() {
  emit(this.shoe.brand, 1);
};

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
    console.warn("app=detection,module=vocabLoader,function=addVocabItem,message=vocab conflict,newItemKey=%s,newItemType=%s,newItemCount=%d,existingItemKey=%s,existingItemType=%s,existingItemCount=%d", item.key, item.type, item.count, vocab[item.key].key, vocab[item.key].type, vocab[item.key].count  )
  } else {
    vocab[item.key] = item;
  }
};

var addTerm = function(item){
  addVocabItem(item);
};
var exportData = function(){
  exports.vocab = vocab; 
};
var populateColours = function(db) {
  console.time('app=detection,module=vocabLoader,function=populateColours');
  db.collection('shoes').mapReduce(
    colourMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {    
      if (err){
        console.error("app=detection,module=vocabLoader,resource=mongo,error=%s", err);
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "colour"
        };
        addTerm(item);
      } 
      console.info("app=detection,module=vocabLoader,coloursVocab=loaded");      
      console.timeEnd('app=detection,module=vocabLoader,function=populateColours');
      exportData();
    }
  );
};
var populateMaterials = function(db) {
  console.time('app=detection,module=vocabLoader,function=populateMaterials');
  db.collection('shoes').mapReduce(
    materialMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        console.error("app=detection,module=vocabLoader,resource=mongo,error=%s", err);
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "material"
          
        };
        addTerm(item);
      } 
      console.info("app=detection,module=vocabLoader,materialsVocab=loaded");
      console.timeEnd('app=detection,module=vocabLoader,function=populateMaterials');      
      exportData(); 
    }
  );
};
var populateStyles = function(db) {
  console.time('app=detection,module=vocabLoader,function=populateStyles');
  db.collection('shoes').mapReduce(
    styleMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        console.error("app=detection,resource=mongo,error=%s", err);
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "style"
          
        };
        addTerm(item);
      } 
      console.info("app=detection,module=vocabLoader,stylesVocab=loaded");
      console.timeEnd('app=detection,module=vocabLoader,function=populateStyles');
      exportData();
    }
  );
};
var populateBrands = function(db) {
  console.time('app=detection,module=vocabLoader,function=populateBrands');
  db.collection('shoes').mapReduce(
    brandMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        console.err("app=detection,module=vocabLoader,resource=mongo,error=%s", err);
      }
      for (i in results) {
        var item = { 
          count: results[i].value, 
          key: results[i]._id,
          type: "style"
          
        };
        addTerm(item);
      } 
      console.info("app=detection,module=vocabLoader,brandsVocab=loaded");
      console.timeEnd('app=detection,module=vocabLoader,function=populateBrands');
      exportData();
    }
  );
};

mongoClient.connect(mongoUri, function (err, db) {
  if (err){
    console.error("app=detection,module=vocabLoader,resource=mongo,error=%s", err);
  }  
  populateMaterials(db);
  populateColours(db);
  populateStyles(db);
  populateBrands(db);
});
