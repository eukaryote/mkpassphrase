# coding=utf-8

from __future__ import absolute_import, division, print_function

import codecs
import math
import os
import random as _random
import sys

import pkg_resources

import six

# require CSPRNG
try:
    os.urandom(1)
except NotImplementedError:
    six.print_(
        "cryptographically secure pseudo-random number generator not available",
        file=sys.stderr,
    )
    raise
else:
    RAND = _random.SystemRandom()

# defaults
PAD = six.u("")  # prefix/suffix of passphrase
DELIMITER = six.u(" ")

# Default entropy bits to use for determining number of words to use
ENTROPY_DEFAULT = 80

WORD_LIST_DEFAULT = "eff-large"

# Map from wordlist name to filename. The three EFF files are as follows:

# WORD_LIST_DEFAULT: 7,776 words, average 7.0 chars in length;
# eff1: 1,296 (6**4) most memorable and distinct words;
# eff2: 1,296 (6**4) words that all have a unique three-character prefix
#   and an edit distance of at least three from any other word in the list.
WORD_LISTS = {
    WORD_LIST_DEFAULT: "eff_large_wordlist.txt",
    "eff1": "eff_short_wordlist_1.txt",
    "eff2": "eff_short_wordlist_2_0.txt",
}


class EncodingError(Exception):
    """Encoding error procesing word file."""


def num_possible(num_candidates, num_words):
    """
    Calculate number of possible word tuples.

    Answers the int number representing how many possible word tuples are
    possible by choosing ``num_words`` elems from ``num_candidates``
    (with replacement). Both args must be at least 1.
    """
    if num_candidates < 1:
        raise ValueError("num_candidates must be positive")
    if num_words < 1:
        raise ValueError("num_words must be positive")

    n, k = num_candidates, num_words
    possible = 1
    while k > 0:
        possible *= n
        n -= 1
        k -= 1
    return possible


def calculate_entropy(dict_size, num_words, random_case=True):
    """Calculate entropy bits for ``num_words`` chosen from ``dict_size``."""
    if random_case:
        dict_size *= 2
    return math.log(num_possible(dict_size, num_words), 2)


def calculate_num_words(dict_size, entropy=None, random_case=True):
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
    words = list(set(filter(test, (line.strip().lower() for line in stream))))
    if not words:
        raise RuntimeError("no words loaded")
    words.sort()
    return words


def load_words_from_list(name):
    filename = WORD_LISTS.get(name)
    if not filename:
        raise ValueError("Invalid wordlist: %s" % (name,))
    path = "wordlists/" + filename
    fullfilepath = pkg_resources.resource_filename("mkpassphrase", path)
    with codecs.open(fullfilepath, "r", "utf-8") as f:
        return load_from_stream(f)


def load_words_from_file(path):
    """
    Get sorted unique words from word file.
    """
    with codecs.open(path, "r", "utf-8") as f:
        return load_from_stream(f)


def sample_words(all_words, k, delimiter=DELIMITER, random_case=True):
    """
    Sample ``k`` words from the ``all_words`` word sequence and join them.

    The words are returned as a string joined using the ``delimiter`` str.

    If ``random_case`` is true (the default), then each word will
    with probability 0.5 be converted to title case, otherwise
    the word is used unchanged as sampled from ``all_words``.
    """
    all_words = list(all_words)
    if k > len(all_words):
        raise ValueError("can't sample %d of %d words" % (k, len(all_words)))
    words = RAND.sample(all_words, k)
    if random_case:
        for i, word in enumerate(words):
            if RAND.choice((True, False)):
                words[i] = word.title()
    return delimiter.join(words)
