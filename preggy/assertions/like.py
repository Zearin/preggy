# -*- coding: utf-8 -*-
'''preggy 'like' assertions.  For use with `expect()` (see `preggy.core`).
'''


# preggy assertions
# https://github.com/heynemann/preggy

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

import re
from datetime import datetime

try:
    from six import string_types, binary_type
except ImportError:  # pragma: no cover
    import warnings
    warnings.warn("Ignoring six. Probably setup.py installing package.")

import numbers

from preggy import create_assertions

DATE_THRESHOLD = 5.0


#-------------------------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------------------------
REMOVE_COLORS_REGEX = re.compile(
    r'(\033|\x1b|\x03)'  # prefixes
    r'\['                # non-regex bracket
    r'[0-9]*m',          # suffix
    re.UNICODE
)


def _match_alike(expected, topic):
    '''Asserts the "like"-ness of `topic` and `expected` according to their types.'''
    if topic is None:
        return expected is None
    if isinstance(topic, string_types + (binary_type, )):
        return _compare_strings(expected, topic)
    if isinstance(topic, numbers.Number):
        return _compare_numbers(expected, topic)
    if isinstance(topic, (list, tuple)):
        return _compare_lists(expected, topic)
    if isinstance(topic, dict):
        return _compare_dicts(expected, topic)
    if isinstance(topic, datetime):
        return _compare_datetime(expected, topic)
    raise RuntimeError('Could not compare {expected} and {topic}'.format(expected=expected, topic=topic))


def _compare_strings(expected, topic):
    '''Asserts the "like"-ness of `topic` and `expected` as strings.
    Allows some leeway.  (Strings don't have to exactly match.)

    '''
    if isinstance(topic, (binary_type, )):
        topic = topic.decode('utf-8')
    if isinstance(expected, (binary_type, )):
        expected = expected.decode('utf-8')

    _filter_str = lambda s: s.strip().lower().replace(' ', '').replace('\n', '')
    expected = REMOVE_COLORS_REGEX.sub('', expected)
    topic = REMOVE_COLORS_REGEX.sub('', topic)

    expected = _filter_str(expected)
    topic = _filter_str(topic)

    if isinstance(topic, (binary_type, )):
        topic = topic.decode('utf-8')
    if isinstance(expected, (binary_type, )):
        expected = expected.decode('utf-8')

    return expected == _filter_str(topic)


def __timedelta_to_seconds(timedelta):
    ms = 10 ** 6
    days = 24 * 3600
    return abs((float(timedelta.microseconds) + (float(timedelta.seconds) + float(timedelta.days) * days) * ms) / ms)


def _compare_datetime(expected, topic):
    return __timedelta_to_seconds(topic - expected) <= DATE_THRESHOLD


def _compare_numbers(expected, topic):
    '''Asserts the "like"-ness of `topic` and `expected` as Numbers.'''
    FALSE_CONDITIONS = (not isinstance(topic, numbers.Number),
                        not isinstance(expected, numbers.Number), )
    if any(FALSE_CONDITIONS):
        return False
    return float(expected) == float(topic)


def _compare_dicts(expected, topic):
    '''Asserts the "like"-ness of `topic` and `expected` as dicts.'''
    return _match_dicts(expected, topic) and _match_dicts(topic, expected)


def _match_dicts(expected, topic):
    '''Asserts the "like"-ness of all keys and values in `topic` and `expected`.'''
    for k, v in expected.items():
        if not k in topic or not _match_alike(topic[k], v):
            return False
    return True


def _compare_lists(expected, topic):
    '''Asserts the "like"-ness of `topic` and `expected` as lists.'''
    return _match_lists(expected, topic) and _match_lists(topic, expected)


def _match_lists(expected, topic):
    '''Asserts the "like"-ness each item in of `topic` and `expected` (as lists or tuples).'''
    for item in expected:
        if isinstance(item, (list, tuple)):
            found = False
            for inner_item in topic:
                if isinstance(inner_item, (list, tuple)) and _compare_lists(item, inner_item):
                    found = True
                    break
            if not found:
                return False
        elif not item in topic:
            return False
    return True


#-------------------------------------------------------------------------------------------------
# Assertions
#-------------------------------------------------------------------------------------------------
@create_assertions
def to_be_like(topic, expected):
    '''Asserts that `topic` is like (similar to) `expected`. Allows some leeway.'''
    return _match_alike(expected, topic)
