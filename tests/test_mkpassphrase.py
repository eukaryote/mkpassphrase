# coding=utf-8

from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import sys
import tempfile
import re
import random as _random

import pytest

import mkpassphrase as M

from tests import test_words

try:
    reduce
except NameError:
    import functools
    reduce = functools.reduce


@pytest.fixture
def word_file(request):
    tmp = tempfile.mktemp()
    request.addfinalizer(lambda: os.remove(tmp))
    with codecs.open(tmp, 'w', 'utf-8') as f:
        for word in test_words:
            f.write(word)
            f.write('\n')
    return tmp


@pytest.fixture
def words(word_file):
    with codecs.open(word_file, 'r', 'utf-8') as f:
        return list(filter(None, f.read().split('\n')))


# sanity check fixtures, to be sure tests are testing what they think they are
def test_word_file_fixture(word_file):
    assert os.access(word_file, os.R_OK)
    with codecs.open(word_file, 'r', 'utf-8') as f:
        result = f.read().strip()
    expected = u'\n'.join(test_words)
    assert result == expected


def test_words_fixture(words):
    assert test_words == tuple(words)


def test_sample_words_len(words):
    k = 5
    assert len(words) > k
    ws = M.sample_words(words, k)
    assert len(ws.split(M.DELIM)) == k


def test_sample_words_random_case(words):

    def has_title_case(results, delim=M.DELIM):
        for ws in results:
            for w in ws.split(delim):
                if w.title() == w:
                    return True
        return False

    k = 5
    assert len(words) > k

    # verify default (True)
    results = [M.sample_words(words, k) for i in range(10)]
    assert has_title_case(results)

    # verify False
    words = [w.lower() for w in words]
    words = [w for w in words if re.match('^[a-z]+$', w)]
    results = [M.sample_words(words, k, random_case=False) for i in range(10)]
    assert not has_title_case(results)


def test_sample_words_unique(words):
    k = 4
    # normalize for testing purposes below
    words = list(set([w.lower() for w in words]))

    results = [M.sample_words(words, k) for i in range(20)]
    for result in results:
        ws = result.split(M.DELIM)
        assert sorted(set(ws)) == sorted(ws)


def test_sample_words_delim(words):
    k = 5
    delim = '_'
    res = M.sample_words(words, k, delim=delim)
    assert res.count(delim) == k - 1
    regex = '^[^{delim}]+({delim}[^{delim}]+){{{n}}}'
    regex = regex.format(delim=delim, n=k - 1)
    assert re.match(regex, res)


def test_mkpassword_defaults(word_file):
    assert M.load_words_from_file(word_file)
    passphrase, entropy = M.mkpassphrase(word_file=word_file)
    assert entropy > 0
    passphrase_words = passphrase.split(M.DELIM)
    assert len(passphrase_words) > 1
    for word in passphrase_words:
        assert passphrase.startswith(M.PAD)
        assert passphrase.endswith(M.PAD)


def test_mkpassword_delim(word_file):
    delim = '^'
    num_words = 10
    passphrase, _ = M.mkpassphrase(word_file=word_file, delim=delim,
                                   num_words=num_words)
    assert delim in passphrase
    assert len(passphrase.split(delim)) == num_words


def test_mkpassword_pad(word_file):
    pad = '//'
    passphrase, _ = M.mkpassphrase(word_file=word_file, pad=pad)
    assert passphrase.startswith(pad)
    assert passphrase.endswith(pad)


def test_mkpassphrase_count_default(word_file):
    result, _ = M.mkpassphrase(word_file=word_file)
    assert isinstance(result, M.u_type)
    result, _ = M.mkpassphrase(word_file=word_file, count=1)
    assert isinstance(result, M.u_type)


@pytest.mark.parametrize('count', list(range(2, 6)))
def test_mkpassphrase_count_multiple(word_file, count):
    passphrases, _ = M.mkpassphrase(word_file=word_file, count=count)
    assert isinstance(passphrases, list)
    assert isinstance(passphrases[0], M.u_type)
    assert len(set(passphrases)) == len(passphrases)


def test_num_possible():
    assert M.num_possible(10, 1) == 10
    assert M.num_possible(10, 2) == 10 * 9
    assert M.num_possible(10, 9) == reduce(lambda a, b: a * b, range(1, 11))

    with pytest.raises(ValueError):
        M.num_possible(0, 1)

    with pytest.raises(ValueError):
        M.num_possible(1, 0)


def test_csprng_unavailable():
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
            del sys.modules['mkpassphrase']
            with pytest.raises(NotImplementedError):
                import mkpassphrase as M
        finally:
            if _urandom:
                os.urandom = _urandom
    finally:
        # undo the patch
        try:
            del sys.modules['mkpassphrase']
        except KeyError:
            pass
        import mkpassphrase as M
        if _urandom:
            assert isinstance(M.RAND, _random.SystemRandom)
