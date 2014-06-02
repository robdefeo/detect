import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

stopwords = stopwords.words('english')
stemmer = PorterStemmer()

def tag(q):
  result = {}
  result['q'] = q.lower()
  rawTokens = nltk.word_tokenize(q)
  taggedWords = nltk.pos_tag(rawTokens)

  result["tokens"] = []
  for idx, val in enumerate(rawTokens):
    result["tokens"].append({
      "value": val,
      "pos": taggedWords[idx][1],
      "stem": stemmer.stem(val),
      "stopWord": val in stopwords
    })

  return result
