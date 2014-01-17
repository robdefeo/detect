var 
  assert = require("assert"),
  target = require("../lib/preProcess"),
  _ = require('underscore')

describe('preProcess', function(){
  it('single word', function(){
    var actual = target.do("red")
    assert.equal(actual.q, "red");
    assert.equal(actual.tokens.length, 1);    
  });
  it('multi word', function(){
    var actual = target.do("red and blue")
    assert.equal(actual.q, "red and blue");
    assert.equal(actual.tokens.length, 3);    
  });
  it('mixed cases', function(){
    var actual = target.do("Red")
    assert.equal(actual.q, "red");
    assert.equal(actual.tokens.length, 1);    
  });
  
});
