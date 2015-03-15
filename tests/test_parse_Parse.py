__author__ = 'robdefeo'
import unittest
from detect.parse import Parse as Target


class find_matches_Tests(unittest.TestCase):
    def test_single_term(self):
        target = Target()
        actual = target.find_matches(
            {},
            3,
            [
                {
                    'pos': 'VBD',
                    'stem': u'red',
                    'stop_word': False,
                    'skip_word': False,
                    'use': True,
                    'value': 'red'
                },
                {
                    'pos': 'NN',
                    'stem': u'heel',
                    'stop_word': False,
                    'skip_word': False,
                    'use': True,
                    'value': 'heel'
                }
            ],
            {
                "en": {
                    "red": {"key": "red", "type": "color", "source": "content"},
                    "heel": {"key": "heel", "type": "style", "source": "content"}
                }
            }
        )

        self.assertDictEqual(
            actual,
            {
                'red': {
                    'found_item': {
                        'key': 'red',
                        'source': 'content',
                        'type': 'color'
                    },
                    'term': 'red',
                    'tokens': ['red']
                },
                'heel': {
                    'found_item': {
                        'key': 'heel',
                        'source': 'content',
                        'type': 'style'
                    },
                    'term': 'heel',
                    'tokens': ['heel']
                }
            }
        )

    def test_multiple_term(self):
        target = Target()
        actual = target.find_matches(
            {},
            3,
            [
                {
                    'pos': 'VBD',
                    'stem': u'red',
                    'stop_word': False,
                    'skip_word': False,
                    'use': True,
                    'value': 'red'
                },
                {
                    'pos': 'NN',
                    'stem': u'valentino',
                    'stop_word': False,
                    'skip_word': False,
                    'use': True,
                    'value': 'valentino'
                }
            ],
            {
                "en": {
                    "red": {"key": "red", "type": "color", "source": "content"},
                    "red valentino": {"key": "red valentino", "type": "brand", "source": "content"}
                }
            }
        )

        self.assertDictEqual(
            actual,
            {
                'red valentino': {
                    'found_item': {
                        'key': 'red valentino',
                        'source': 'content',
                        'type': 'brand'
                    },
                    'term': 'red valentino',
                    'tokens': ['red', 'valentino']
                }
            }
        )


class create_found_doc_Tests(unittest.TestCase):
    maxDiff = None

    def test_regular(self):
        target = Target()
        actual = target.create_found_doc(
            "terms_value",
            "tokens_value",
            "found_item_value"
        )

        self.assertDictEqual(
            actual,
            {
                "term": "terms_value",
                "tokens": "tokens_value",
                "found_item": "found_item_value"
            }
        )


class preperation_Tests(unittest.TestCase):
    maxDiff = None

    def test_empty_string(self):
        target = Target()
        actual = target.preparation("")
        self.assertDictEqual(
            actual,
            {
                'q': '',
                'tokens': []
            }
        )

    def test_has_uppercase_elements(self):
        target = Target()
        actual = target.preparation("Red HEEL")
        self.assertDictEqual(
            actual,
            {
                'q': 'red heel',
                'tokens': [
                    {
                        'pos': 'VBD',
                        'stem': u'red',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'red'
                    },
                    {
                        'pos': 'NN',
                        'stem': u'heel',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'heel'
                    }
                ]
            }
        )

    def test_has_stopwords(self):
        target = Target()
        actual = target.preparation("Shoes with red and white")
        self.assertDictEqual(
            actual,
            {
                'q': 'shoes with red and white',
                'tokens': [
                    {
                        'pos': 'NNS',
                        'stem': u'shoe',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'shoes'},
                    {
                        'pos': 'IN',
                        'stem': u'with',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'with'},
                    {
                        'pos': 'JJ',
                        'stem': u'red',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'red'},
                    {
                        'pos': 'CC',
                        'stem': u'and',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'and'},
                    {
                        'pos': 'JJ',
                        'stem': u'white',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'white'
                    }
                ]
            }
        )

    def test_has_skipwords(self):
        target = Target()
        actual = target.preparation("Show me anything")
        self.assertDictEqual(
            actual,
            {
                'q': 'show me anything',
                'tokens': [
                    {
                        'pos': 'NN',
                        'stem': u'show',
                        'stop_word': True,
                        'skip_word': True,
                        'use': False,
                        'value': 'show'},
                    {
                        'pos': 'PRP',
                        'stem': u'me',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'me'},
                    {
                        'pos': 'NN',
                        'stem': u'anyth',
                        'stop_word': False,
                        'skip_word': True,
                        'use': False,
                        'value': 'anything'
                    }
                ]
            }
        )