import codecs
import os

from tests import test_words


# sanity check fixtures, to be sure tests are testing what they think they are
def test_word_file_fixture(word_file):
    assert os.access(word_file, os.R_OK)
    with codecs.open(word_file, "r", "utf-8") as f:
        result = f.read().strip()
    expected = "\n".join(test_words)
    assert result == expected


def test_words_fixture(words):
    assert test_words == tuple(words)
