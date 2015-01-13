import unittest

from detect.parse import preparation


class preperation_Tests(unittest.TestCase):
    maxDiff = None

    def test_empty_string(self):
        target = preparation
        actual = target("")
        self.assertDictEqual(
            actual,
            {
                'q': '',
                'tokens': []
            }
        )

    def test_has_uppercase_elements(self):
        target = preparation
        actual = target("Red HEEL")
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
        target = preparation
        actual = target("Shoes with red and white")
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
        target = preparation
        actual = target("Show me anything")
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