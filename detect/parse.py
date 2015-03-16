import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams
from operator import itemgetter

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
        self.tokenizer = nltk.PunktWordTokenizer()

    def preparation(self, q):
        # used_query = q.lower().strip()
        used_query = q
        result = {
            "used_query": used_query,
            "original_query": q
        }
        raw_tokens = self.tokenizer.tokenize(used_query)
        token_spans = self.tokenizer.span_tokenize(used_query)
        tagged_words = nltk.pos_tag(raw_tokens)

        result["tokens"] = []
        for index, value in enumerate(raw_tokens):
            lower_value = value.lower()
            stop_word = lower_value in self.stopwords
            skip_word = lower_value in self.skip_words
            result["tokens"].append({
                "value": lower_value,
                "start": token_spans[index][0],
                "end": token_spans[index][1],
                "pos": tagged_words[index][1],
                "use": tagged_words[index][1][0] in ["J", "N", "V"] and not stop_word and not skip_word,
                "stem": self.stemmer.stem(lower_value),
                "stop_word": stop_word,
                "skip_word": skip_word
            })

        return result

    def create_found_doc(self, term, tokens, found_item, start, end):
        return {
            "term": term,
            "tokens": tokens,
            "found_item": found_item,
            "start": start,
            "end": end
        }

    def find_matches(self, ngram_size, tokens, vocab):
        found = []
        n = min(len(tokens), ngram_size)
        for ngram in ngrams(tokens, n):
            ngram_term = " ".join(
                x["value"] for x in ngram if not x["stop_word"]
            )
            start = ngram[0]["start"]
            end = ngram[-1:][0]["end"]

            if ngram_term in vocab["en"]:
                found.append(
                    self.create_found_doc(
                        ngram_term,
                        [x["value"] for x in ngram],
                        vocab["en"][ngram_term],
                        start,
                        end
                    )
                )
            elif n > 0:
                found.extend(self.find_matches(n-1, tokens, vocab))

        return found

    def autocorrect_query(self, used_query, found_entities):
        corrected_query = used_query
        corrected = False
        # need to work from end of string backwards otherwise it gets messed up with adding/removing chars
        for entity in sorted(found_entities, key=itemgetter("start"), reverse=True):
            for x in [x for x in entity["found_item"] if x["match_type"] == "spelling"]:
                corrected = True
                corrected_query = corrected_query[0:entity["start"]] + x["display_name"] + corrected_query[entity["end"]:]

        if corrected:
            return corrected_query
        else:
            return None

    def unique_matches(self):
        raise Exception()

    def disambiguate(self, vocab, preparation_result):
        found_entities = self.find_matches(
            [],
            3,
            preparation_result["tokens"],
            vocab
        )

        unique_values = list(found_entities.values())
        # terms_found = [x["term"] for x in unique_values]
        terms_found = []
        for x in found_entities.values():
            for y in x["tokens"]:
                terms_found.append(y)
        unique_terms_found = list(set(terms_found))

        not_women_shoes = [x["found_item"] for x in unique_values if not (x["found_item"]["type"] == "style" and (x["found_item"]["key"] == "shoe" or x["found_item"]["key"] == "women"))]
        return {
            "detections": not_women_shoes,
            "non_detections": [x["value"] for x in preparation_result["tokens"] if x["use"] and x["value"] not in unique_terms_found and x["pos"][0] in ["J", "N"]]
        }

