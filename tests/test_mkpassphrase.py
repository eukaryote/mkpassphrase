# coding=utf-8

from __future__ import print_function

import os
import re

import pytest

import mkpassphrase as M

from tests import test_words

try:
    reduce
except NameError:
    import functools
    reduce = functools.reduce


def verify_get_words(path, verifier, msg,
                     min=M.MIN, max=M.MAX, ascii=True):
    for word in M.get_words(path, min=min, max=max, ascii=ascii):
        assert verifier(word), msg % word


def test_word_file(word_file):
    assert os.access(word_file, os.R_OK)
    assert '\n'.join(test_words) == open(word_file).read().strip()


def test_get_words_lowercased(word_file):
    """ All words should be just lowercase letters (ascii only) by default. """
    verify_get_words(word_file, (lambda w: re.match('^[a-z]+$', w)),
                     'non-lowercase word: %s')


def test_get_words_nonascii(word_file):
    words = M.get_words(word_file, ascii=False)
    assert u'quúux' in words


def test_get_words_min_default(word_file):
    """ All words should be at least MIN chars. """
    verify_get_words(word_file, (lambda w: len(w) >= M.MIN), "'%s' too short")


def test_get_words_max_default(word_file):
    """ All words should be no longer than MAX chars. """
    verify_get_words(word_file, (lambda w: len(w) <= M.MAX), "'%s' too long")


def test_get_words_min_custom(word_file):
    """ All words should be least MIN+1 chars. """
    verify_get_words(word_file, (lambda w: len(w) >= M.MIN + 1),
                     "'%s' too long", min=M.MIN + 1)


def test_get_words_max_custom(word_file):
    """ All words should be no longer than MAX-1 chars. """
    verify_get_words(word_file, (lambda w: len(w) <= M.MAX - 1),
                     "'%s' too long", max=M.MAX - 1)


def test_mk_word_pat_min_lte_max():
    with pytest.raises(ValueError):
        M.mk_word_matcher(min=5, max=4)


def test_mkpassword_defaults(word_file):
    all_words = M.get_words(word_file)
    assert len(all_words) == 8
    passphrase, num_candidates = M.mkpassphrase(word_file)
    assert num_candidates == len(all_words) * 2
    passphrase_words = passphrase.split(M.DELIM)
    assert len(passphrase_words) == M.WORDS
    for word in passphrase_words:
        assert len(word) >= M.MIN
        assert len(word) <= M.MAX
        assert re.match('^[a-zA-Z]+$', word)
        assert passphrase.startswith(M.PAD)
        assert passphrase.endswith(M.PAD)


def test_mkpassword_num_words(word_file):
    for i in range(1, 7):
        passphrase, n = M.mkpassphrase(word_file, num_words=i)
        assert len(passphrase.split(M.DELIM)) == i


def test_mkpassword_min_max(word_file):
    passphrase, n = M.mkpassphrase(word_file, min=9, max=10, num_words=2)
    words = passphrase.lower().split(M.DELIM)
    assert sorted(words) == sorted(test_words[-2:])


def test_mkpassword_random_case_true(word_file):
    n = 100
    num_lower = num_title = 0
    for i in range(n):
        passphrase, _ = M.mkpassphrase(word_file, random_case=True)
        for word in passphrase.split(M.DELIM):
            if re.match('^[a-z]+$', word):
                num_lower += 1
            elif word == word.title():
                num_title += 1
    total_words = n * M.WORDS
    assert total_words == num_lower + num_title
    assert num_lower > total_words / 4
    assert num_title > total_words / 4


def test_mkpassword_delim(word_file):
    delim = '^'
    passphrase, _ = M.mkpassphrase(word_file, delim=delim)
    assert delim in passphrase
    assert len(passphrase.split(delim)) == M.WORDS


def test_mkpassword_pad(word_file):
    pad = '//'
    passphrase, _ = M.mkpassphrase(word_file, pad=pad)
    assert passphrase.startswith(pad)
    assert passphrase.endswith(pad)


def test_num_possible():
    assert M.num_possible(10, 1) == 10
    assert M.num_possible(10, 2) == 10 * 9
    assert M.num_possible(10, 9) == reduce(lambda a, b: a * b, range(1, 11))

    with pytest.raises(ValueError):
        M.num_possible(0, 1)

    with pytest.raises(ValueError):
        M.num_possible(1, 0)
