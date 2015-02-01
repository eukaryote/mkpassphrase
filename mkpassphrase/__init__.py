"""
Utility methods for generating passphrases from a dictionary file of words.
"""

__version__ = '0.1'

import random
import re
import unicodedata

try:
    unicode
except NameError:
    u = lambda s: s
else:
    u = lambda s: unicode(s)


try:
    from itertools import imap
except ImportError:
    imap = map


# defaults
MIN = 3    # min word length
MAX = 7    # max word length
WORDS = 4  # num words
PAD = ''   # prefix/suffix of passphrase
WORD_FILE = '/usr/share/dict/words'


def is_unicode_letter(char):
    """ Answer whether given unicode character is a letter."""
    return unicodedata.category(char) in ('Ll', 'Lu')


def mk_word_matcher(min=MIN, max=MAX, ascii=True):
    if max < min:
        msg = "min '%s' should be less than or equal to max '%s'"
        raise ValueError(msg % (min, max))
    if ascii:
        pat = re.compile('^[a-zA-Z]{%s,%s}$' % (min, max))

        def matcher(word):
            return bool(pat.match(word))
    else:

        def matcher(word):
            length = len(word)
            return (length >= min and length <= max and
                    all(imap(is_unicode_letter, word)))
    return matcher


def get_words(path, min=MIN, max=MAX, ascii=True, sorted=False):
    matcher = mk_word_matcher(min=min, max=max, ascii=ascii)
    with open(path) as f:
        words = (line.strip().lower() for line in f)
        if not ascii:
            words = (u(w) for w in words)
        words = list(filter(matcher, set(words)))
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
                  random_case=True, ascii=True, pad=PAD):
    all_words = get_words(path, min=min, max=max)
    passphrase = sample_words(all_words, num_words, random_case=random_case)
    passphrase = pad + passphrase + pad
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
