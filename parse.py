import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

stopwords = stopwords.words('english')
stemmer = PorterStemmer()

def preperation(q):
  result = {}
  result['q'] = q.lower()
  rawTokens = nltk.word_tokenize(q)
  taggedWords = nltk.pos_tag(rawTokens)

  result["tokens"] = []
  for idx, val in enumerate(rawTokens):
    stopWord = val in stopwords
    result["tokens"].append({
      "value": val,
      "pos": taggedWords[idx][1],
      "use": taggedWords[idx][1][0] in ["J", "N", "V"] and not stopWord,
      "stem": stemmer.stem(val),
      "stopWord": stopWord
    })

  return result

def getItem(vocab, tokens):
  string = " ".join([x["value"] for x in tokens])
  if string in vocab:
    return vocab[string]
  else:
    return None

def disambiguate(vocab, preprocessResult):
  res = {
    "detections": [],
    "nonDetections": []
  }
  skip = 0
  for idx, val in enumerate(preprocessResult["tokens"]):
    token = preprocessResult["tokens"][idx]
    tokenTwo = preprocessResult["tokens"][idx + 1] if idx < len(preprocessResult["tokens"]) - 1 else None

    if skip == 0:
      itemToken = getItem(vocab, [token])
      itemTokenTwo = getItem(vocab, [token, tokenTwo]) if tokenTwo else None

      if tokenTwo and itemTokenTwo:
        skip = 1
        res["detections"].append(itemTokenTwo)
      elif itemToken:
        res["detections"].append(itemToken)
      else:
        res["nonDetections"].append(token)

    else:
      skip -= 1
      print "skipping=%s" % token

  return res
