"""
Utility methods for generating passphrases from a dictionary file of words.
"""

__version__ = '0.1'

import string
import random
import re


# defaults
MIN = 3    # min word length
MAX = 7    # max word length
WORDS = 4  # num words
WORD_FILE = '/usr/share/dict/words'


def mk_word_pat(min=MIN, max=MAX, ascii=True):
    # string.letters will include non-ascii letters if locale includes them
    char_class = '[a-zA-Z]' if ascii else '[' + string.letters + ']'
    regex = '^{char_class}{{{min},{max}}}$'.format(**locals())
    return re.compile(regex)


def get_words(path, min=MIN, max=MAX, ascii=True, sorted=False):
    pat = mk_word_pat(min=min, max=max, ascii=ascii)
    with open(path) as f:
        words = (line.strip().lower() for line in f)
        words = list(set(filter(pat.match, words)))
    if sorted:
        words.sort()
    return words


def sample_words(all_words, num_words, random_case=True):
    all_words = list(all_words)
    words = random.sample(all_words, num_words)
    if random_case:
        for i, word in enumerate(words):
            if random.choice((True, False)):
                words[i] = word.title()
    return ' '.join(words)


def mk_passphrase(path=WORD_FILE, min=MIN, max=MAX, num_words=WORDS,
                  random_case=True, ascii=True):
    all_words = get_words(path, min=min, max=max)
    passphrase = sample_words(all_words, num_words, random_case=random_case)
    num_candidates = len(all_words)
    if random_case:
        num_candidates *= 2
    return passphrase, num_candidates


def num_possible(num_candidates, num_words):
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
