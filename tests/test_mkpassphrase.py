# coding=utf-8

from __future__ import print_function

import os
import re

import pytest

import mkpassphrase as M

from tests import test_words


def verify_get_words(path, verifier, msg,
                     min=M.MIN, max=M.MAX, ascii=True, sorted=False):
    for word in M.get_words(path, min=min, max=max, ascii=ascii,
                            sorted=sorted):
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
