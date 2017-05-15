"""Utilities for generating passphrases from a dictionary file of words."""

from __future__ import absolute_import, division, print_function

from contextlib import closing
import functools
import math
import os
import random as _random
import sys
import types
import unicodedata

import pkg_resources

# require CSPRNG
try:
    os.urandom(1)
except NotImplementedError:
    print("cryptographically secure pseudo-random "
          "number generator not available")
    raise
else:
    RAND = _random.SystemRandom()

# python 2/3 compatibility workarounds
if sys.version_info[0] >= 3:
    u = u_type = str
else:
    # default encoding is always supposed to be ascii under python2, so we
    # just try as utf-8 and don't support other encodings for now
    u = functools.partial(types.UnicodeType, encoding='utf8')
    u_type = types.UnicodeType
    # alias imap as map under python2 for consistency with python3
    from itertools import imap as map


__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))


# defaults
PAD = ''        # prefix/suffix of passphrase
DELIM = u(' ')  # delimiter

# Default entropy bits to use for determining number of words to use
ENTROPY_DEFAULT = 80

WORD_LIST_DEFAULT = 'eff-large'

WORD_LISTS = {
    WORD_LIST_DEFAULT: 'eff_large_wordlist.txt',
    'eff1': 'eff_short_wordlist_1.txt',
    'eff2': 'eff_short_wordlist_2_0.txt',
}


class EncodingError(Exception):
    """Encoding error procesing word file."""


def is_unicode_letter(char):
    """Answer whether given unicode character is a letter."""
    return unicodedata.category(char) in ('Ll', 'Lu')


def calculate_entropy(dict_size, num_words, random_case=False):
    """Calculate entropy bits for ``num_words`` chosen from ``dict_size``."""
    if random_case:
        dict_size *= 2
    return math.log(num_possible(dict_size, num_words), 2)


def calculate_num_words(dict_size, entropy=None, random_case=False):
    """
    Calculate number of words needed for given entropy drawn from dict size.
    """
    if entropy is None:
        entropy = ENTROPY_DEFAULT

    n = 1
    result_entropy = calculate_entropy(dict_size, n, random_case)
    while result_entropy < entropy:
        n += 1
        result_entropy = calculate_entropy(dict_size, n, random_case)
    return n, result_entropy


def load_from_stream(stream, test=None):
    words = list(filter(test, (line.decode('utf8').strip().lower()
                               for line in stream)))
    if not words:
        raise Exception("no words loaded")
    words.sort()
    return words


def load_words_from_list(name):
    filename = WORD_LISTS.get(name)
    if not filename:
        raise ValueError("Invalid wordlist: %s" % (name,))
    path = 'wordlists/' + filename
    with closing(pkg_resources.resource_stream('mkpassphrase', path)) as f:
        return load_from_stream(f)


def load_words_from_file(path):
    """
    Get sorted unique words from word file.
    """
    with open(path) as f:
        return load_from_stream(f)


def sample_words(all_words, k, delim=DELIM, random_case=True):
    """
    Sample ``k`` words from the ``all_words`` word sequence and join them.

    The words are returned as a string joined using the ``delim`` str.

    If ``random_case`` is true (the default), then each word will
    with probability 0.5 be converted to title case, otherwise
    the word is used unchanged as sampled from ``all_words``.
    """
    all_words = list(all_words)
    if k >= len(all_words):
        raise ValueError("can't sample %d of %d words" % (k, len(all_words)))
    words = RAND.sample(all_words, k)
    if random_case:
        for i, word in enumerate(words):
            if RAND.choice((True, False)):
                words[i] = word.title()
    return delim.join(words)


def mkpassphrase(word_list=None, word_file=None, entropy=None, num_words=None,
                 random_case=True, delim=DELIM, pad=PAD, count=1):
    """
    Make one or more passphrases using given params.

    :params:
    - word_list: name of a builtin wordlist ('eff-large', 'eff1', or 'eff2')
    - word_file: path to a word file, one word per line, encoded with a
            character encoding that is compatible with the python default
            encoding if ``ascii`` is true.
    - entropy: optional bits of entropy minimum that will be used to
           calculate the number of words to use if ``num_words`` not provided,
           or used to verify ``num_words`` is sufficient if both provided.
    - num_words: number of words to include in passphrase (at least 1, if
            provided). If not provided, the number will be calculated
            based on the ``entropy`` (or default entropy if ``entropy``
            not provide).
    - random_case: whether to capitalize first letter of each word with
             probability 0.5
    - delim: the delimiter to use for joining the words in the passphrase.
    - pad: a string to use as a prefix and suffix of the generated passphrase.
    - count: positive integer representing the number of passwords to generate,
             defaulting to 1. If greater than one, the ``passphrase`` returned
             will be a list of passphrases. If equal to one, the ``passphrase``
             will be just a string passphrase and not a one-element list.

    :return:
    - passphrase: the generated passphrase (string) or list of passphrases
    - entropy bits: entropy in bits of the generated passphrase(s)
    """
    if not bool(word_file) ^ bool(word_list):
        raise ValueError("exactly one of 'word_list' and "
                         "'word_file' is required")
    if num_words is not None and num_words < 1:
        raise ValueError("'num_words' must be at least 1 if provided")
    if not isinstance(count, int) or count < 1:
        raise ValueError("'count' must be a positive int")

    words = (load_words_from_file(word_file) if word_file
             else load_words_from_list(word_list))

    # if num words not provided, we calculate how many to
    # use based on entropy target provided (or default if not provided)
    if num_words is None:
        num_words, actual_entropy = calculate_num_words(
            len(words),
            entropy=entropy,
            random_case=random_case,
        )
    else:
        actual_entropy = calculate_entropy(
            len(words),
            num_words,
            random_case,
        )
        if entropy is not None and actual_entropy < entropy:
            msg = "entropy bits (%s) for %d words is less than %d"
            msg %= (int(actual_entropy), num_words, entropy)
            raise ValueError(msg)

    passphrases = []
    for _ in range(count):
        passphrase = sample_words(words, num_words, delim=delim,
                                  random_case=random_case)
        passphrase = pad + passphrase + pad
        passphrases.append(passphrase)

    return (passphrases[0] if count == 1 else passphrases), actual_entropy


def num_possible(num_candidates, num_words):
    """
    Calculate number of possible word tuples.

    Answers the int number representing how many possible word tuples are
    possible by choosing ``num_words`` elems from ``num_candidates``
    (with replacement). Both args must be at least 1.
    """
    if num_candidates < 1:
        raise ValueError('num_candidates must be positive')
    if num_words < 1:
        raise ValueError('num_words must be positive')

    n, k = num_candidates, num_words
    possible = 1
    while k > 0:
        possible *= n
        n -= 1
        k -= 1
    return possible
