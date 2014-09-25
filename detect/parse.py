import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

stopwords = stopwords.words('english')
stemmer = PorterStemmer()


def preparation(q):
    result = {
        "q": q.lower()
    }
    raw_tokens = nltk.word_tokenize(q)
    tagged_words = nltk.pos_tag(raw_tokens)

    result["tokens"] = []
    for idx, val in enumerate(raw_tokens):
        stopWord = val in stopwords
        result["tokens"].append({
            "value": val,
            "pos": tagged_words[idx][1],
            "use": tagged_words[idx][1][0] in ["J", "N", "V"] and not stopWord,
            "stem": stemmer.stem(val),
            "stop_word": stopWord
        })

    return result


def get_item(vocab, tokens):
    string = " ".join([x["value"] for x in tokens])
    if string in vocab:
        return vocab[string]
    else:
        return None

def create_found_doc(term, found_item):
    return {
        "term": term,
        "found_item": found_item
    }

def disambiguate(vocab, preprocess_result):

    from nltk.util import bigrams, trigrams

    found_data = []
    # unmatched_tokens = dict.fromkeys(set(preprocess_result["tokens"]))
    # for trigram in trigrams([x["value"] for x in preprocess_result["tokens"]]):
    found = {}
    for trigram in trigrams(preprocess_result["tokens"]):
        # try to match tri gram
        trigram_term = " ".join(x["value"] for x in trigram if not x["stop_word"])
        if trigram_term in vocab["en"]:
            found[trigram_term] = create_found_doc(
                trigram_term,
                vocab["en"][trigram_term]
            )
        else:
            for bigram in bigrams(trigram):
                bigram_term = " ".join(
                    x["value"] for x in bigram if not x["stop_word"])
                if bigram_term in vocab["en"]:
                    found[bigram_term] = create_found_doc(
                        bigram_term,
                        vocab["en"][bigram_term]
                    )
                else:
                    for gram in bigram:
                        if not gram["stop_word"]:
                            term = gram["value"]
                            if term in vocab["en"]:
                                found[term] = create_found_doc(
                                    term,
                                    vocab["en"][term]
                                )
    unique_values = list(found.values())
    terms_found = [x["term"] for x in unique_values]
    return {
        "detections": [x["found_item"] for x in unique_values],
        "non_detections": [x["value"] for x in preprocess_result["tokens"] if not x["stop_word"] and x["value"] not in terms_found]
    }

