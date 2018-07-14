# coding=utf-8

from __future__ import absolute_import, division, print_function

import codecs
import os
import sys
import tempfile
import re
import random as _random

import six
from six.moves import reduce

import pytest

from mkpassphrase import api, internal

from tests import test_words


@pytest.fixture
def word_file(request):
    tmp = tempfile.mktemp()
    request.addfinalizer(lambda: os.remove(tmp))
    with codecs.open(tmp, "w", "utf-8") as f:
        for word in test_words:
            f.write(word)
            f.write("\n")
    return tmp


@pytest.fixture
def words(word_file):
    with codecs.open(word_file, "r", "utf-8") as f:
        return list(filter(None, f.read().split("\n")))


# sanity check fixtures, to be sure tests are testing what they think they are
def test_word_file_fixture(word_file):
    assert os.access(word_file, os.R_OK)
    with codecs.open(word_file, "r", "utf-8") as f:
        result = f.read().strip()
    expected = "\n".join(test_words)
    assert result == expected


def test_words_fixture(words):
    assert test_words == tuple(words)


def test_sample_words_len(words):
    k = 5
    assert len(words) > k
    ws = internal.sample_words(words, k)
    assert len(ws.split(internal.DELIMITER)) == k


def test_sample_words_random_case(words):
    def has_title_case(results, delim=internal.DELIMITER):
        for ws in results:
            for w in ws.split(delim):
                if w.title() == w:
                    return True
        return False

    k = 5
    assert len(words) > k

    # verify default (True)
    results = [internal.sample_words(words, k) for i in range(10)]
    assert has_title_case(results)

    # verify False
    words = [w.lower() for w in words]
    words = [w for w in words if re.match("^[a-z]+$", w)]
    results = [internal.sample_words(words, k, random_case=False) for i in range(10)]
    assert not has_title_case(results)


def test_sample_words_unique(words):
    k = 4
    # normalize for testing purposes below
    words = list(set([w.lower() for w in words]))

    results = [internal.sample_words(words, k) for i in range(20)]
    for result in results:
        ws = result.split(internal.DELIMITER)
        assert sorted(set(ws)) == sorted(ws)


def test_sample_words_delim(words):
    k = 5
    delim = "_"
    res = internal.sample_words(words, k, delimiter=delim)
    assert res.count(delim) == k - 1
    regex = "^[^{delim}]+({delim}[^{delim}]+){{{n}}}"
    regex = regex.format(delim=delim, n=k - 1)
    assert re.match(regex, res)


def test_mkpassword_defaults(word_file):
    assert internal.load_words_from_file(word_file)
    passphrase, entropy = api.mkpassphrase(word_file=word_file)
    assert entropy > 0
    passphrase_words = passphrase.split(internal.DELIMITER)
    assert len(passphrase_words) > 1
    for word in passphrase_words:
        assert passphrase.startswith(internal.PAD)
        assert passphrase.endswith(internal.PAD)


def test_mkpassword_delim(word_file):
    delim = "^"
    num_words = 10
    passphrase, _ = api.mkpassphrase(
        word_file=word_file, delimiter=delim, num_words=num_words
    )
    assert delim in passphrase
    assert len(passphrase.split(delim)) == num_words


def test_mkpassword_pad(word_file):
    pad = "//"
    passphrase, _ = api.mkpassphrase(word_file=word_file, pad=pad)
    assert passphrase.startswith(pad)
    assert passphrase.endswith(pad)


def test_mkpassphrase_count_default(word_file):
    result, _ = api.mkpassphrase(word_file=word_file)
    assert isinstance(result, six.text_type)
    result, _ = api.mkpassphrase(word_file=word_file, count=1)
    assert isinstance(result, six.text_type)


@pytest.mark.parametrize("count", list(range(2, 6)))
def test_mkpassphrase_count_multiple(word_file, count):
    passphrases, _ = api.mkpassphrase(word_file=word_file, count=count)
    assert isinstance(passphrases, list)
    assert isinstance(passphrases[0], six.text_type)
    assert len(set(passphrases)) == len(passphrases)


def test_num_possible():
    assert internal.num_possible(10, 1) == 10
    assert internal.num_possible(10, 2) == 10 * 9
    assert internal.num_possible(10, 9) == reduce(lambda a, b: a * b, range(1, 11))

    with pytest.raises(ValueError):
        internal.num_possible(0, 1)

    with pytest.raises(ValueError):
        internal.num_possible(1, 0)


def test_csprng_unavailable(capsys):
    # patch os.urandom so it behaves as if not implemented, if needed
    _urandom = None
    try:
        os.urandom(1)
    except NotImplementedError:
        pass  # no need to patch
    else:
        _urandom = os.urandom

        def fail(n):
            raise NotImplementedError()

        os.urandom = fail

    # reimport to test module initialization logic when urandom not implemented
    try:
        try:
            sys.modules.pop("mkpassphrase", None)
            sys.modules.pop("mkpassphrase.internal", None)
            with pytest.raises(NotImplementedError):
                import mkpassphrase.internal  # noqa
            out, err = capsys.readouterr()
            assert "not available" in err
        finally:
            if _urandom:
                os.urandom = _urandom
    finally:
        # undo the patch
        try:
            sys.modules.pop("mkpassphrase", None)
            sys.modules.pop("mkpassphrase.internal", None)
        except KeyError:
            pass
        import mkpassphrase.internal as I2

        if _urandom:
            assert isinstance(I2.RAND, _random.SystemRandom)
