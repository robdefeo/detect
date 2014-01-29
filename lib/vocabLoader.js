var 
  mongoClient = require('mongodb').MongoClient,
  _ = require('underscore'),
  natural = require('natural'),
  async = require('async')

// var mongoUri = process.env.MONGOHQ_GETTER_URL || "mongodb://getter:getter@paulo.mongohq.com:10030/getter";
var mongoUri = process.env.MONGOHQ_GETTER_URL || "mongodb://localhost:27017/getter";

var vocab = {};

vocabStatus = {
  materials: "notStarted",
  brands: "notStarted",
  colours: "notStarted",
  styles: "notStarted"
};


exports.status = function(){
  vocabStatus.self ="down";
  if (
    vocabStatus.materials == "completed" &
    vocabStatus.brands == "completed" &
    vocabStatus.colours == "completed" &
    vocabStatus.styles == "completed"   
  ){
    vocabStatus.self ="up";
  }
  return vocabStatus;
}

var brandMap = function() {
  emit(this.shoe.brand.toLowerCase(), 1);
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

var populateColours = function(db, callback) {
  console.time('app=detection,function=populateColours,module=vocabLoader,function=populateColours');
  vocabStatus.colours = "started";
  db.collection('shoes').mapReduce(
    colourMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {    
      if (err){
        vocabStatus.colours = "errored";        
        console.error("app=detection,function=populateColours,module=vocabLoader,resource=mongo,error=%s", JSON.stringify(err));
      } else{
        vocabStatus.colours = "inProgress";

        for (i in results) {
          var item = { 
            count: results[i].value, 
            key: results[i]._id,
            type: "colour"
          };
          addTerm(item);
        } 
        console.info("app=detection,function=populateColours,module=vocabLoader,coloursVocab=loaded");      
        console.timeEnd('app=detection,function=populateColours,module=vocabLoader,function=populateColours');
        vocabStatus.colours = "completed";
     }
     callback();
    }
  );
};
var populateMaterials = function(db, callback) {
  console.time('app=detection,function=populateMaterials,module=vocabLoader,function=populateMaterials');
  vocabStatus.materials = "started";
  db.collection('shoes').mapReduce(
    materialMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        vocabStatus.materials = "errored";        
        console.error("app=detection,function=populateMaterials,module=vocabLoader,resource=mongo,error=%s", JSON.stringify(err));
      } else{
        vocabStatus.materials = "inProgress";
        for (i in results) {
          var item = { 
            count: results[i].value, 
            key: results[i]._id,
            type: "material"
          
          };
          addTerm(item);
        } 
        console.info("app=detection,function=populateMaterials,module=vocabLoader,materialsVocab=loaded");
        console.timeEnd('app=detection,function=populateMaterials,module=vocabLoader,function=populateMaterials');      
        vocabStatus.materials = "completed";
      }
      callback(); 
    }
  );
};
var populateStyles = function(db, callback) {
  console.time('app=detection,function=populateStyles,module=vocabLoader,function=populateStyles');
  vocabStatus.styles = "started";
  db.collection('shoes').mapReduce(
    styleMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        vocabStatus.styles = "errored";    
        console.error("app=detection,function=populateStyles,resource=mongo,error=%s", JSON.stringify(err));
      } else{
        vocabStatus.styles = "inProgress";
        for (i in results) {
          var item = { 
            count: results[i].value, 
            key: results[i]._id,
            type: "style"
          
          };
          addTerm(item);
        } 
        console.info("app=detection,function=populateStyles,module=vocabLoader,stylesVocab=loaded");
        console.timeEnd('app=detection,function=populateStyles,module=vocabLoader,function=populateStyles');
        vocabStatus.styles = "completed";
      }
      callback();
    }
  );
};
var populateBrands = function(db, callback) {
  console.time('app=detection,function=populateBrands,module=vocabLoader,function=populateBrands');
  vocabStatus.brands = "started";
  db.collection('shoes').mapReduce(
    brandMap,
    reduce,
    {
      out: {inline: 1}
    },
    function (err, results) {   
      if (err){
        vocabStatus.brands = "errored";
        console.error("app=detection,function=populateBrands,module=vocabLoader,resource=mongo,error=%s", JSON.stringify(err));
      } else{
        vocabStatus.brands = "inProgress";
      
        for (i in results) {
          var item = { 
            count: results[i].value, 
            key: results[i]._id,
            type: "brand"
          
          };
          addTerm(item);
        } 
        console.info("app=detection,function=populateBrands,module=vocabLoader,brandsVocab=loaded");
        console.timeEnd('app=detection,function=populateBrands,module=vocabLoader,function=populateBrands');
      
        vocabStatus.brands = "completed";
      }
      callback();        
    }
  );
};

exports.loadData = function(callback){
  mongoClient.connect(mongoUri, function (err, db) {
    if (err){
      console.error("app=detection,function=loadData,module=vocabLoader,resource=mongo,error=%s", JSON.stringify(err));
      throw err;
    }else{    
      async.series([
        function(callback){
          populateBrands(db, callback)
        },
        function(callback){
          populateMaterials(db, callback)
        },      
        function(callback){
          populateColours(db, callback)
        },
        function(callback){
          populateStyles(db, callback)
        }
      ],
      // optional callback
      function(err, results){
        if(err){
          vocab = undefined;
          throw err;
        }else{
          exports.vocab = vocab; 
          db.close();
          console.info("app=detection,function=loadData,module=vocabLoader,action=completed");
          callback();          
        }
          // the results array will equal ['one','two'] even though
          // the second function had a shorter timeout.
      });

    }  
  });
}


