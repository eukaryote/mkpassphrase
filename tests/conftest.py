# coding=utf-8

import codecs

import six

import pytest

from tests import test_words


@pytest.fixture
def word_file(tmpdir):
    tmpfile = tmpdir.join("words")
    filepath = str(tmpfile)
    with codecs.open(filepath, "w", "utf-8") as f:
        for word in test_words:
            six.print_(word, file=f)
    yield filepath


@pytest.fixture
def words(word_file):
    with codecs.open(word_file, "r", "utf-8") as f:
        words = list(filter(None, f.read().split("\n")))
    yield words
