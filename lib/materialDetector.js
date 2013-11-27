var 
  mongoClient = require('mongodb').MongoClient,
  _ = require('underscore');

var mongoUri = process.env.MONGOHQ_SCRAPE_URL || "mongodb://localhost:27017/getter";

materials = {}

var map = function() {
  for (var i = 0; i < this.shoe.attributes.length; i++) {
    if (this.shoe.attributes[i].key.toLowerCase().indexOf("material") != -1){
      var possibleItems = this.shoe.attributes[i].value
      .replace(" and ", "/")
      .replace(" n ", "/")
      .split(/[(\-)(\_)(\/)(,)(\&)(\+)]/);
      for (var materialIndex = 0; materialIndex < possibleItems.length; materialIndex++) {
        var possibleItem = possibleItems[materialIndex].trim().toLowerCase();
        if(possibleItem != "") {
          emit(possibleItem, 1);
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
        materials[results[i]._id] = { 
          value: results[i].value, 
          key: results[i]._id
        }
      }  
    }
  );    
});