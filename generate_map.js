function() {
 for (var i = 0; i < this.attributes.length; i++) {
   var item = this.attributes[i]
   value = ''
   if (item["_id"].hasOwnProperty("key")) {
     value = item["_id"]["key"]
   } else {
     value = item["_id"]["value"]
   }

   emit({
      "type": item["_id"]["type"],
      "value": value
     },
     item["confidence"]
   )
  }
};
