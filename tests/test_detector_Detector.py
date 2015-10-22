from mock import Mock

__author__ = 'robdefeo'
import unittest
from detect.detector import Detector as Target


class format_found_entities(unittest.TestCase):
    def test_remove_if_found_in_larger_string(self):
        all_found = [
            {'term': 'blue', 'start': 0, 'tokens': ['blue'], 'position': '0_4', 'end': 4, 'found_item': [
                {'type': 'color', 'match_type': 'alias', 'key': 'blue', 'display_name': 'blue', 'source': 'content'}]},
            {'term': 'heels', 'start': 10, 'tokens': ['heels'], 'position': '10_15', 'end': 15, 'found_item': [
                {'type': 'style', 'match_type': 'alias', 'key': 'heels', 'display_name': 'display_name',
                 'source': 'content'}]},
            {'term': 'high heels', 'start': 5, 'tokens': ['high', 'heels'], 'position': '5_15', 'end': 15,
             'found_item': [
                 {'type': 'style', 'match_type': 'alias', 'key': 'high heels', 'display_name': 'display_name',
                  'source': 'content'}]}
        ]
        target = Target({})
        actual = target.format_found_entities(all_found)

        self.assertListEqual(
            [
                {
                    'term': 'blue', 'start': 0, 'tokens': ['blue'], 'position': '0_4', 'end': 4, 'found_item': [
                    {'type': 'color', 'match_type': 'alias', 'key': 'blue', 'display_name': 'blue',
                     'source': 'content'}
                ]
                },
                {
                    'term': 'high heels', 'start': 5, 'tokens': ['high', 'heels'], 'position': '5_15', 'end': 15,
                    'found_item': [
                        {'type': 'style', 'match_type': 'alias', 'key': 'high heels', 'display_name': 'display_name',
                         'source': 'content'}
                    ]
                }
            ],
            actual
        )


class detect_entities(unittest.TestCase):
    def test_no_autocorrection(self):
        target = Target({})
        target.find_matches = Mock()
        target.find_matches.return_value = {
            "found": "find_matches_found",
            "can_not_match": "find_matches_can_not_match"
        }
        target.autocorrect_query = Mock()
        target.autocorrect_query.return_value = None
        target.key_matches = Mock(return_value="key_matches:return_value")
        target.unique_non_detections = Mock()
        target.unique_non_detections.return_value = "unique_non_detections:return_value"
        target.format_found_entities = Mock()
        target.format_found_entities.return_value = "formated_found_entities"

        actual = target.detect_entities(
            "vocab",
            {
                "tokens": "preperation_result:tokens",
                "used_query": "preperation_result:used_query"
            }
        )
        self.assertEqual(1, target.find_matches.call_count)
        self.assertEqual(3, target.find_matches.call_args_list[0][0][0])
        self.assertEqual("preperation_result:tokens", target.find_matches.call_args_list[0][0][1])
        self.assertEqual(
            target.find_matches.call_args_list[0][0][2],
            'vocab'
        )

        self.assertEqual(1, target.autocorrect_query.call_count)
        self.assertEqual('preperation_result:used_query', target.autocorrect_query.call_args_list[0][0][0])
        self.assertEqual('formated_found_entities', target.autocorrect_query.call_args_list[0][0][1])

        self.assertEqual(1, target.key_matches.call_count)

        self.assertEqual('formated_found_entities', target.key_matches.call_args_list[0][0][0])

        self.assertEqual(1, target.unique_non_detections.call_count)
        self.assertEqual('find_matches_can_not_match', target.unique_non_detections.call_args_list[0][0][0])

        self.assertDictEqual(
            {
                'detections': 'key_matches:return_value',
                'non_detections': 'unique_non_detections:return_value'
            },
            actual
        )

    def test_autocorrection(self):
        target = Target({})
        target.find_matches = Mock()
        target.find_matches.return_value = {
            "found": "find_matches_found",
            "can_not_match": "find_matches_can_not_match"
        }
        target.autocorrect_query = Mock()
        target.autocorrect_query.return_value = "autocorrected_query_new_value"
        target.key_matches = Mock(return_value="key_matches:return_value")
        target.unique_non_detections = Mock()
        target.unique_non_detections.return_value = "unique_non_detections:return_value"
        target.format_found_entities = Mock()
        target.format_found_entities.return_value = "formated_found_entities"

        actual = target.detect_entities(
            "vocab",
            {
                "tokens": "preperation_result:tokens",
                "used_query": "preperation_result:used_query"
            }
        )
        self.assertEqual(1, target.find_matches.call_count)
        self.assertEqual(3, target.find_matches.call_args_list[0][0][0])
        self.assertEqual("preperation_result:tokens", target.find_matches.call_args_list[0][0][1])
        self.assertEqual('vocab', target.find_matches.call_args_list[0][0][2])

        self.assertEqual(
            target.autocorrect_query.call_count,
            1
        )
        self.assertEqual(
            target.autocorrect_query.call_args_list[0][0][0],
            'preperation_result:used_query'
        )
        self.assertEqual(
            target.autocorrect_query.call_args_list[0][0][1],
            'formated_found_entities'
        )

        self.assertEqual(
            target.key_matches.call_count,
            1
        )

        self.assertEqual(
            target.key_matches.call_args_list[0][0][0],
            'formated_found_entities'
        )

        self.assertEqual(
            target.unique_non_detections.call_count,
            1
        )
        self.assertEqual(
            target.unique_non_detections.call_args_list[0][0][0],
            'find_matches_can_not_match'
        )

        self.assertDictEqual(
            actual,
            {
                'autocorrected_query': 'autocorrected_query_new_value',
                'detections': 'key_matches:return_value',
                'non_detections': 'unique_non_detections:return_value'
            }
        )


class unique_non_detections_Tests(unittest.TestCase):
    maxDiff = None

    def test_empty_can_not_match(self):
        target = Target({})
        actual = target.unique_non_detections([])

        self.assertListEqual(
            actual,
            []
        )

    def test_non_duplicates(self):
        target = Target({})
        actual = target.unique_non_detections(
            [
                {
                    'value': 'citrus',
                    'start': 0,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'citrus',
                    'end': 5,
                    'use': True,
                    'pos': 'NN'
                },
                {
                    'value': 'heel',
                    'start': 5,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'heel',
                    'end': 10,
                    'use': True,
                    'pos': 'NN'
                }
            ]
        )

        self.assertSetEqual(
            set(actual),
            set(['heel', 'citrus'])
        )

    def test_duplicates(self):
        target = Target({})
        actual = target.unique_non_detections(
            [
                {
                    'value': 'citrus',
                    'start': 0,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'citrus',
                    'end': 5,
                    'use': True,
                    'pos': 'NN'
                },
                {
                    'value': 'heel',
                    'start': 5,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'heel',
                    'end': 10,
                    'use': True,
                    'pos': 'NN'
                },
                {
                    'value': 'citrus',
                    'start': 15,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'citrus',
                    'end': 20,
                    'use': True,
                    'pos': 'NN'
                }
            ]
        )

        self.assertSetEqual(
            set(actual),
            set(['heel', 'citrus'])
        )


class unique_matches_Tests(unittest.TestCase):
    maxDiff = None

    def test_no_duplicates(self):
        target = Target({})
        actual = target.unique_matches(
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 0,
                    'end': 6,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'style'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'high heels',
                    'tokens': ['high heels']
                }
            ]
        )

        self.assertEqual(
            len(actual),
            2
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'color',
                'key': 'citrus'
            } in actual
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'style',
                'key': 'high heels'
            } in actual
        )

    def test_Single(self):
        target = Target({})
        actual = target.unique_matches(
            [
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'style'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'high heels',
                    'tokens': ['high heels']
                }
            ]
        )
        self.assertListEqual(
            actual,
            [
                {
                    'source': 'content',
                    'type': 'style',
                    'key': 'high heels'
                }
            ]
        )

    def test_multiple_alias(self):
        target = Target({})
        actual = target.unique_matches(
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        },
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'style'
                        }
                    ],
                    'start': 0,
                    'end': 6,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'style'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'high heels',
                    'tokens': ['high heels']
                }
            ]
        )

        self.assertEqual(
            len(actual),
            3
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'color',
                'key': 'citrus'
            } in actual
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'style',
                'key': 'citrus'
            } in actual
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'style',
                'key': 'high heels'
            } in actual
        )

    def test_mix_spelling_alias(self):
        target = Target({})
        actual = target.unique_matches(
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 0,
                    'end': 6,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'style'
                        }
                    ],
                    'start': 10,
                    'end': 16,
                    'term': 'high heels',
                    'tokens': ['high heels']
                }
            ]
        )

        self.assertEqual(
            len(actual),
            2
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'color',
                'key': 'citrus'
            } in actual
        )
        self.assertTrue(
            {
                'source': 'content',
                'type': 'style',
                'key': 'high heels'
            } in actual
        )


class autocorrect_query_Tests(unittest.TestCase):
    maxDiff = None

    def test_single_mistake(self):
        target = Target({})
        actual = target.autocorrect_query(
            # 0123456789
            "citru",
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 0,
                    'end': 5,
                    'term': 'citru',
                    'tokens': ['citru']
                }
            ]
        )

        self.assertEqual(
            actual,
            "citrus"
        )

    def test_single_mistake_with_other_words(self):
        target = Target({})
        actual = target.autocorrect_query(
            # 012345678901234567890123456789
            "I want citru high heels",
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 7,
                    'end': 12,
                    'term': 'citru',
                    'tokens': ['citru']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 13,
                    'end': 23,
                    'term': 'high heels',
                    'tokens': ['high', 'heels']
                }
            ]
        )

        self.assertEqual(
            actual,
            "I want citrus high heels"
        )

    def test_multiple_mistakes_with_other_words(self):
        target = Target({})
        actual = target.autocorrect_query(
            # 012345678901234567890123456789
            "I want citru high hells thanks",
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 7,
                    'end': 12,
                    'term': 'citru',
                    'tokens': ['citru']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 13,
                    'end': 23,
                    'term': 'high hells',
                    'tokens': ['high', 'hells']
                }
            ]
        )

        self.assertEqual(
            actual,
            "I want citrus high heels thanks"
        )

    def test_multiple_mistakes_with_same_entity_no_mistake(self):
        target = Target({})
        actual = target.autocorrect_query(
            # 012345678901234567890123456789
            "I want citru high hells citrus thanks",
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 7,
                    'end': 12,
                    'term': 'citru',
                    'tokens': ['citru']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'spelling',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 13,
                    'end': 23,
                    'term': 'high hells',
                    'tokens': ['high', 'hells']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 24,
                    'end': 30,
                    'term': 'citrus',
                    'tokens': ['citrus']
                }
            ]
        )

        self.assertEqual(
            actual,
            "I want citrus high heels citrus thanks"
        )

    def test_no_mistakes(self):
        target = Target({})
        actual = target.autocorrect_query(
            # 012345678901234567890123456789
            "I want citrus high heels",
            [
                {
                    'found_item': [
                        {
                            'display_name': 'citrus',
                            'key': 'citrus',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 7,
                    'end': 13,
                    'term': 'citrus',
                    'tokens': ['citrus']
                },
                {
                    'found_item': [
                        {
                            'display_name': 'high heels',
                            'key': 'high heels',
                            'match_type': 'alias',
                            'source': 'content',
                            'type': 'color'
                        }
                    ],
                    'start': 14,
                    'end': 24,
                    'term': 'high heels',
                    'tokens': ['high', 'heels']
                }
            ]
        )

        self.assertIsNone(actual)


class find_matches_Tests(unittest.TestCase):
    maxDiff = None

    def test_miss_spelling_ngram(self):
        target = Target({})
        actual = target.find_matches(
            3,
            [
                {'skip_word': False, 'stem': 'white', 'start': 0, 'pos': 'JJ', 'value': 'white', 'stop_word': False,
                 'use': True, 'end': 5},
                {'skip_word': False, 'stem': 'and', 'start': 7, 'pos': 'CC', 'value': 'and', 'stop_word': True,
                 'use': False, 'end': 10},
                {'skip_word': False, 'stem': 'blue', 'start': 11, 'pos': 'JJ', 'value': 'blue', 'stop_word': False,
                 'use': True, 'end': 15},
                {'skip_word': False, 'stem': 'high', 'start': 16, 'pos': 'NN', 'value': 'high', 'stop_word': False,
                 'use': True, 'end': 20},
                {'skip_word': False, 'stem': 'heal', 'start': 21, 'pos': 'NNS', 'value': 'heals', 'stop_word': False,
                 'use': True, 'end': 26}
            ],
            {
                'en': {
                    'high heals': [
                        {'type': 'color', 'key': 'high heels', 'source': 'content', 'display_name': 'high heels',
                         'match_type': 'spelling'}],
                    'white': [{'type': 'color', 'key': 'white', 'source': 'content', 'display_name': 'white',
                               'match_type': 'alias'}],
                    'blue': [{'type': 'color', 'key': 'blue', 'source': 'content', 'display_name': 'blue',
                              'match_type': 'alias'}]
                }
            }
        )

        self.assertDictEqual(
            {
                'found': [
                    {
                        'position': '0_5',
                        'start': 0,
                        'end': 5,
                        'found_item': [
                            {'source': 'content', 'type': 'color', 'match_type': 'alias', 'key': 'white',
                             'display_name': 'white'}
                        ],
                        'term': 'white',
                        'tokens': ['white']
                    },
                    {
                        'position': '11_15',
                        'start': 11, 'end': 15,
                        'found_item': [
                            {'source': 'content', 'type': 'color', 'match_type': 'alias', 'key': 'blue',
                             'display_name': 'blue'}
                        ],
                        'term': 'blue', 'tokens': ['blue']
                    },
                    {
                        'position': '16_26',
                        'start': 16, 'end': 26,
                        'found_item': [
                            {'source': 'content', 'type': 'color', 'match_type': 'spelling', 'key': 'high heels',
                             'display_name': 'high heels'}
                        ],
                        'term': 'high heals', 'tokens': ['high', 'heals']
                    }
                ],
                'can_not_match': []
            },
            actual

        )

    def test_miss_spelling(self):
        target = Target({})
        actual = target.find_matches(
            3,
            [
                {
                    'value': 'citru',
                    'start': 0,
                    'skip_word': False,
                    'stop_word': False,
                    'stem': 'citru',
                    'end': 5,
                    'use': True,
                    'pos': 'NN'
                }
            ],
            {
                'en': {
                    'citru': [{'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                               'match_type': 'spelling'}],
                    'citrus': [{'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                                'match_type': 'alias'}],
                    'red': [{'type': 'color', 'key': 'red', 'source': 'content', 'display_name': 'red',
                             'match_type': 'alias'}],
                    'heel': [{'type': 'style', 'key': 'heel', 'source': 'content', 'display_name': 'heel',
                              'match_type': 'alias'}]
                }
            }
        )

        self.assertDictEqual(
            actual,
            {
                'can_not_match': [],
                "found": [
                    {
                        'found_item': [
                            {
                                'display_name': 'citrus',
                                'key': 'citrus',
                                'match_type': 'spelling',
                                'source': 'content',
                                'type': 'color'
                            }
                        ],
                        'position': '0_5',
                        'start': 0,
                        'end': 5,
                        'term': 'citru',
                        'tokens': ['citru']
                    }
                ]
            }
        )

    def test_single_term(self):
        target = Target({})

        actual = target.find_matches(
            3,
            [
                {'stem': 'red', 'value': 'red', 'start': 0, 'pos': 'NNP', 'end': 3, 'skip_word': False,
                 'stop_word': False, 'use': True},
                {'stem': 'heel', 'value': 'heel', 'start': 4, 'pos': 'NN', 'end': 8, 'skip_word': False,
                 'stop_word': False, 'use': True}
            ],
            {
                'en': {
                    'citru': [
                        {
                            'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                            'match_type': 'spelling'
                        }
                    ],
                    'citrus': [
                        {
                            'type': 'color', 'key': 'citrus', 'source': 'content', 'display_name': 'citrus',
                            'match_type': 'alias'
                        }
                    ],
                    'red': [
                        {
                            'type': 'color', 'key': 'red', 'source': 'content', 'display_name': 'red',
                            'match_type': 'alias'
                        }
                    ],
                    'heel': [
                        {
                            'type': 'style', 'key': 'heel', 'source': 'content', 'display_name': 'heel',
                            'match_type': 'alias'
                        }
                    ]
                }
            }
        )

        self.assertDictEqual(
            actual,
            {
                "can_not_match": [],
                "found": [
                    {
                        'found_item': [
                            {
                                'display_name': 'red',
                                'key': 'red',
                                'match_type': 'alias',
                                'source': 'content',
                                'type': 'color'
                            }
                        ],
                        'position': '0_3',
                        'start': 0,
                        'end': 3,
                        'term': 'red',
                        'tokens': ['red']
                    },
                    {
                        'found_item': [
                            {
                                'display_name': 'heel',
                                'key': 'heel',
                                'match_type': 'alias',
                                'source': 'content',
                                'type': 'style'
                            }
                        ],
                        'position': '4_8',
                        'start': 4,
                        'end': 8,
                        'term': 'heel',
                        'tokens': ['heel']
                    }
                ]
            }
        )

    def test_multiple_term(self):
        target = Target({})
        actual = target.find_matches(
            3,
            [
                {
                    'value': 'red',
                    'pos': 'VBD',
                    'stem': 'red',
                    'stop_word': False,
                    'use': True,
                    'start': 0,
                    'skip_word': False,
                    'end': 3
                },
                {
                    'value': 'valentino',
                    'pos': 'VBN',
                    'stem': 'valentino',
                    'stop_word': False,
                    'use': True,
                    'start': 4,
                    'skip_word': False,
                    'end': 13
                }
            ],
            {
                "en": {
                    "red": [
                        {"key": "red", "type": "color", "source": "content", 'match_type': 'alias'}
                    ],
                    "red valentino": [
                        {"key": "red valentino", "type": "brand", "source": "content", 'match_type': 'alias'}
                    ]
                }
            }
        )

        self.assertDictEqual(
            actual,
            {
                "can_not_match": [],
                "found": [
                    {
                        'found_item': [
                            {
                                'key': 'red valentino',
                                'match_type': 'alias',
                                'source': 'content',
                                'type': 'brand'
                            }
                        ],
                        'term': 'red valentino',
                        'end': 13,
                        'start': 0,
                        'position': '0_13',
                        'tokens': ['red', 'valentino']
                    }
                ]
            }

        )

    def test_has_non_matches(self):
        target = Target({})
        actual = target.find_matches(
            3,
            [
                {
                    'value': 'red',
                    'pos': 'VBD',
                    'stem': 'red',
                    'stop_word': False,
                    'use': True,
                    'start': 0,
                    'skip_word': False,
                    'end': 3
                },
                {
                    'value': 'valentino',
                    'pos': 'VBN',
                    'stem': 'valentino',
                    'stop_word': False,
                    'use': True,
                    'start': 4,
                    'skip_word': False,
                    'end': 13
                }
            ],
            {
                "en": {
                    "red": [
                        {"key": "red", "type": "color", "source": "content", 'match_type': 'alias'}
                    ]
                }
            }
        )

        self.assertDictEqual(
            {
                "found": [
                    {
                        'end': 3,
                        'position': '0_3',
                        'tokens': ['red'],
                        'found_item': [
                            {
                                'key': 'red',
                                'match_type': 'alias',
                                'source': 'content',
                                'type': 'color'
                            }
                        ],
                        'term': 'red',
                        'start': 0
                    }
                ],
                'can_not_match': [
                    {
                        'value': 'valentino',
                        'pos': 'VBN',
                        'stem': 'valentino',
                        'stop_word': False,
                        'use': True,
                        'start': 4,
                        'skip_word': False,
                        'end': 13
                    }
                ]
            },
            actual
        )


class create_found_doc_Tests(unittest.TestCase):
    maxDiff = None

    def test_regular(self):
        target = Target({})
        actual = target.create_found_doc(
            "terms_value",
            "tokens_value",
            "found_item_value",
            "start_value",
            "end_value"
        )

        self.assertDictEqual(
            actual,
            {
                "term": "terms_value",
                "tokens": "tokens_value",
                "found_item": "found_item_value",
                "start": "start_value",
                'position': 'start_value_end_value',
                "end": "end_value"
            }
        )


class preperation_Tests(unittest.TestCase):
    maxDiff = None

    def test_empty_string(self):
        target = Target({})
        actual = target.preparation("")
        self.assertDictEqual(
            actual,
            {
                'used_query': '',
                'tokens': [],
                'original_query': ''
            }
        )

    def test_has_uppercase_elements(self):
        target = Target({})
        actual = target.preparation("Red HEEL")
        self.assertDictEqual(
            actual,
            {
                'used_query': 'Red HEEL',
                'original_query': 'Red HEEL',
                'tokens': [
                    {
                        'start': 0,
                        'end': 3,
                        'pos': 'NNP',
                        'stem': u'red',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'red'
                    },
                    {
                        'start': 4,
                        'end': 8,
                        'pos': 'NNP',
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
        target = Target({})
        actual = target.preparation("Shoes with red and white")
        self.assertDictEqual(
            actual,
            {
                'original_query': 'Shoes with red and white',
                'used_query': 'Shoes with red and white',
                'tokens': [
                    {
                        'start': 0,
                        'end': 5,
                        'pos': 'VBZ',
                        'stem': u'shoe',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'shoes'},
                    {
                        'start': 6,
                        'end': 10,
                        'pos': 'IN',
                        'stem': u'with',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'with'},
                    {
                        'start': 11,
                        'end': 14,
                        'pos': 'JJ',
                        'stem': u'red',
                        'stop_word': False,
                        'skip_word': False,
                        'use': True,
                        'value': 'red'},
                    {
                        'start': 15,
                        'end': 18,
                        'pos': 'CC',
                        'stem': u'and',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'and'},
                    {
                        'start': 19,
                        'end': 24,
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
        target = Target({})
        actual = target.preparation("Show me anything")
        self.assertDictEqual(
            actual,
            {
                'original_query': 'Show me anything',
                'used_query': 'Show me anything',
                'tokens': [
                    {
                        'start': 0,
                        'end': 4,
                        'pos': 'NNP',
                        'stem': u'show',
                        'stop_word': True,
                        'skip_word': True,
                        'use': False,
                        'value': 'show'},
                    {
                        'start': 5,
                        'end': 7,
                        'pos': 'PRP',
                        'stem': u'me',
                        'stop_word': True,
                        'skip_word': False,
                        'use': False,
                        'value': 'me'},
                    {
                        'start': 8,
                        'end': 16,
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
