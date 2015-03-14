import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams

class Parse():
    def __init__(self):
        self.extra_stop_words = [
            "show"
        ]
        self.stopwords = stopwords.words('english')
        self.stopwords.extend(self.extra_stop_words)
        self.skip_words = [
            "all",
            "any",
            "anything",
            "display",
            "every",
            "everything",
            "find",
            "show",
            "some",
            "something",
            "want"
        ]
        self.stemmer = PorterStemmer()

    def preparation(self, q):
        result = {
            "q": q.lower()
        }
        raw_tokens = nltk.word_tokenize(q.lower())
        tagged_words = nltk.pos_tag(raw_tokens)

        result["tokens"] = []
        for idx, val in enumerate(raw_tokens):
            stop_word = val in self.stopwords
            skip_word = val in self.skip_words
            result["tokens"].append({
                "value": val,
                "pos": tagged_words[idx][1],
                "use": tagged_words[idx][1][0] in ["J", "N", "V"] and not stop_word and not skip_word,
                "stem": self.stemmer.stem(val),
                "stop_word": stop_word,
                "skip_word": skip_word
            })

        return result

    def create_found_doc(self, term, tokens, found_item):
        return {
            "term": term,
            "tokens": tokens,
            "found_item": found_item
        }

    def find_matches(self, found, ngram_size, tokens, vocab):
        n = min(len(tokens), ngram_size)
        for ngram in ngrams(tokens, n):
            ngram_term = " ".join(
                x["value"] for x in ngram if not x["stop_word"])
            if ngram_term in vocab["en"]:
                found[ngram_term] = self.create_found_doc(
                    ngram_term,
                    [x["value"] for x in ngram],
                    vocab["en"][ngram_term]
                )
            elif n > 0:
                found.update(self.find_matches(found, n-1, tokens, vocab))

        return found

    def disambiguate(self, vocab, preparation_result):
        found = self.find_matches({}, 3, preparation_result["tokens"], vocab)
        unique_values = list(found.values())
        # terms_found = [x["term"] for x in unique_values]
        terms_found = []
        for x in found.values():
            for y in x["tokens"]:
                terms_found.append(y)
        unique_terms_found = list(set(terms_found))

        not_women_shoes = [x["found_item"] for x in unique_values if not (x["found_item"]["type"] == "style" and (x["found_item"]["key"] == "shoe" or x["found_item"]["key"] == "women"))]
        return {
            "detections": not_women_shoes,
            "non_detections": [x["value"] for x in preparation_result["tokens"] if x["use"] and x["value"] not in unique_terms_found and x["pos"][0] in ["J", "N"]]
        }

