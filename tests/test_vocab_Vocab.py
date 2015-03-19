__author__ = 'robdefeo'
import unittest

from mock import Mock

from detect.vocab import Vocab as Target


class add_value_Tests(unittest.TestCase):
    def test_already_exsits(self):
        target = Target()
        acutal = {
            "en": {
                "black": ["black"]
            }
        }

        target.add_value(
            acutal,
            "en",
            "black",
            "new_black"
        )

        self.assertDictEqual(
            acutal,
            {'en': {'black': ['black', 'new_black']}}
        )

    def test_no_value(self):
        target = Target()
        acutal = {
            "en": {
                "black": ["black"]
            }
        }

        target.add_value(
            acutal,
            "en",
            "blue",
            "blue"
        )

        self.assertDictEqual(
            acutal,
            {
                'en': {
                    'black': ['black'],
                    'blue': ['blue']
                }
            }
        )


class generate_empty_structure_Tests(unittest.TestCase):
    def test_regular(self):
        target = Target()
        actual = target.generate_empty_structure(["en"])
        self.assertDictEqual(
            {
                "en": {}
            },
            actual
        )


class load_Tests(unittest.TestCase):
    maxDiff = None

    def test_spelling_mistakes(self):
        target = Target()
        target.add_hearts = Mock()
        target.get_from_database = Mock()
        target.get_from_database.return_value = [
            {
                "_id": {
                    "type": "color",
                    "key": "citrus"
                },
                "aliases": [
                    {
                        "value": "citrus",
                        "language": "en"
                    },
                    {
                        "value": "agrume",
                        "language": "it"
                    },
                    {
                        "value": "citrin",
                        "language": "fr"
                    },
                    {
                        "value": "citru",
                        "language": "en",
                        "type": "spelling"
                    }
                ]
            }
        ]

        actual = target.load(["en"])

        self.assertDictEqual(
            actual,
            {
                'en': {
                    'citru': [{'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                               'match_type': 'spelling'}],
                    'citrus': [{'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                                'match_type': 'alias'}],
                }
            }
        )

        self.assertEqual(
            target.add_hearts.call_count,
            1
        )

    def test_display_name_set(self):
        target = Target()
        target.add_hearts = Mock()
        target.get_from_database = Mock()
        target.get_from_database.return_value = [
            {
                "_id": {
                    "type": "brand",
                    "key": "ash"
                },
                "display_name": "Ash",
                "aliases": [
                    {
                        "value": "ash",
                        "language": "en"
                    }
                ]
            }
        ]

        actual = target.load(["en"])

        self.assertDictEqual(
            actual,
            {
                'en': {
                    'ash': [{'type': 'brand', 'key': 'ash', 'source': 'content', 'display_name': 'Ash',
                             'match_type': 'alias'}]
                }
            }
        )

        self.assertEqual(
            target.add_hearts.call_count,
            1
        )

    def test_display_name_not_set(self):
        target = Target()
        target.add_hearts = Mock()
        target.get_from_database = Mock()
        target.get_from_database.return_value = [
            {
                "_id": {
                    "type": "brand",
                    "key": "ash"
                },
                "display_name": None,
                "aliases": [
                    {
                        "value": "ash",
                        "language": "en"
                    }
                ]
            }
        ]

        actual = target.load(["en"])

        self.assertDictEqual(
            actual,
            {
                'en': {
                    'ash': [{'type': 'brand', 'key': 'ash', 'source': 'content', 'display_name': 'ash',
                             'match_type': 'alias'}]
                }
            }
        )

        self.assertEqual(
            target.add_hearts.call_count,
            1
        )

    def test_display_name_not_exists(self):
        target = Target()
        target.add_hearts = Mock()
        target.get_from_database = Mock()
        target.get_from_database.return_value = [
            {
                "_id": {
                    "type": "brand",
                    "key": "ash"
                },
                "aliases": [
                    {
                        "value": "ash",
                        "language": "en"
                    }
                ]
            }
        ]

        actual = target.load(["en"])

        self.assertDictEqual(
            actual,
            {
                'en': {
                    'ash': [{'type': 'brand', 'key': 'ash', 'source': 'content', 'display_name': 'ash',
                             'match_type': 'alias'}]
                }
            }
        )
        self.assertEqual(
            target.add_hearts.call_count,
            1
        )

    def test_multiple_alias_different_type(self):
        target = Target()
        target.get_from_database = Mock()
        target.get_from_database.return_value = [
            {
                "_id": {
                    "type": "brand",
                    "key": "ash"
                },
                "display_name": "Ash",
                "aliases": [
                    {
                        "value": "ash",
                        "language": "en"
                    }
                ]
            },
            {
                "_id": {
                    "type": "color",
                    "key": "ash"
                },
                "display_name": None,
                "aliases": [
                    {
                        "value": "ash",
                        "language": "en"
                    }
                ]
            }
        ]

        actual = target.load(["en"])

        self.assertDictEqual(
            actual,
            {
                'en': {
                    'hearts': [{'type': 'interest', 'key': 'heart', 'source': 'context', 'display_name': 'heart',
                                'match_type': 'alias'}],
                    'ash': [{'type': 'brand', 'key': 'ash', 'source': 'content', 'display_name': 'Ash',
                             'match_type': 'alias'},
                            {'type': 'color', 'key': 'ash', 'source': 'content', 'display_name': 'ash',
                             'match_type': 'alias'}]
                }
            }
        )