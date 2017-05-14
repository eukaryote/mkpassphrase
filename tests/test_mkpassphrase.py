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


@pytest.fixture
def matchers():
    return [M.mk_word_matcher(ascii=b) for b in [True, False]]


# sanity check fixtures, to be sure tests are testing what they think they are
def test_word_file_fixture(word_file):
    assert os.access(word_file, os.R_OK)
    with codecs.open(word_file, 'r', 'utf-8') as f:
        result = f.read().strip()
    expected = u'\n'.join(test_words)
    assert result == expected


def test_words_fixture(words):
    assert test_words == tuple(words)


def verify_get_words(path, verifier, msg,
                     min=M.MIN, max=M.MAX, ascii=True):
    for word in M.get_words(path, min=min, max=max, ascii=ascii):
        assert verifier(word), msg % word


def test_is_unicode_letter_yes():
    assert M.is_unicode_letter('ú')
    assert M.is_unicode_letter('Ѥ')
    assert M.is_unicode_letter('u')
    assert M.is_unicode_letter('X')
    assert M.is_unicode_letter('Æ')
    assert M.is_unicode_letter('Ë')


def test_is_unicode_letter_no():
    assert not M.is_unicode_letter('2')
    assert not M.is_unicode_letter('®')


def test_is_unicode_letter_non_unicode():
    s = '3'.encode('ascii')
    with pytest.raises(TypeError):
        assert M.is_unicode_letter(s)


def test_mk_word_matcher_too_short(matchers):
    too_short = 'ab'
    assert len(too_short) < M.MIN
    for m in matchers:
        assert not m(too_short)


def test_mk_word_matcher_too_long(matchers):
    too_long = 'ababababab'
    assert len(too_long) > M.MAX
    for m in matchers:
        assert not m(too_long)


def test_mk_word_matcher_not_letters(matchers):
    for m in matchers:
        assert not m("abc-def")
        assert not m("abc_def")
        assert not m("wor rdd")
        assert not m("1234")
        assert not m("\n")
        assert not m("")


def test_mk_word_matcher_encoding():
    m = M.mk_word_matcher(ascii=False)
    s = 'abcd'.encode('ascii')
    with pytest.raises(M.EncodingError):
        m(s)
    assert m('abcd')  # relying on unicode_literals


def test_mk_word_matcher_custom_min():
    matchers = [M.mk_word_matcher(ascii=a, min=5) for a in [True, False]]
    for m in matchers:
        assert m('abcde')
        assert m('abcdef')
        assert not m('abcd')


def test_mk_word_matcher_custom_max():
    matchers = [M.mk_word_matcher(ascii=a, max=5) for a in [True, False]]
    for m in matchers:
        assert m('abcd')
        assert m('abcde')
        assert not m('abcdef')
        assert not m('abcdefg')


def test_mk_word_matcher_min_max():
    m = M.mk_word_matcher(min=5, max=5)
    assert m('abcde')
    assert not m('abcd')
    assert not m('abcdef')
    with pytest.raises(ValueError):
        M.mk_word_matcher(min=5, max=4)


def test_get_words_lowercased(word_file):
    """ All words should be just lowercase letters (ascii only) by default. """
    verify_get_words(word_file, (lambda w: re.match('^[a-z]+$', w)),
                     'non-lowercase word: %s')


def test_get_words_nonascii(word_file):
    words = M.get_words(word_file, ascii=False)
    assert 'quúux' in words


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


def test_mkpassword_lowercase_false(word_file):
    n = 100
    num_lower = num_title = 0
    for i in range(n):
        passphrase, _ = M.mkpassphrase(word_file, lowercase=False)
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


def test_mkpassphrase_count_default(word_file):
    result, _ = M.mkpassphrase(word_file)
    assert isinstance(result, M.u_type)
    result, _ = M.mkpassphrase(word_file, count=1)
    assert isinstance(result, M.u_type)


@pytest.mark.parametrize('count', list(range(2, 6)))
def test_mkpassphrase_count_multiple(word_file, count):
    passphrases, _ = M.mkpassphrase(word_file, count=count)
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
            import mkpassphrase as M
            assert M.RAND is _random, "should use non-CSPRNG impl"
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
