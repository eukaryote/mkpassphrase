# coding=utf-8

from __future__ import absolute_import, division, print_function

import codecs
import os
import sys
import re
import random as _random

import six

import pytest

from mkpassphrase import internal

import tests


def test_num_possible_invalid_num_candidates():
    with pytest.raises(ValueError) as err:
        internal.num_possible(0, 2)
    assert str(err.value) == "num_candidates must be positive"


def test_num_possible_invalid_num_words():
    with pytest.raises(ValueError) as err:
        internal.num_possible(2, 0)
    assert str(err.value) == "num_words must be positive"


@pytest.mark.parametrize(
    "n,k,expected",
    [
        (1, 1, 1),
        (2, 1, 2),
        (2, 2, 2),
        (3, 1, 3),
        (3, 2, 6),
        (4, 1, 4),
        (4, 2, 12),
        (4, 3, 24),
        (4, 4, 24),
        (10, 1, 10),
        (10, 2, 90),
        (10, 3, 720),
        (10, 4, 5040),
        (10, 5, 30240),
        (10, 6, 151200),
        (10, 7, 604800),
        (10, 8, 1814400),
        (10, 9, 3628800),
        (10, 10, 3628800),
    ],
)
def test_num_possible_success(n, k, expected):
    assert internal.num_possible(n, k) == expected


@pytest.mark.parametrize(
    "dict_size,entropy,expected",
    [(2, 1, (1, 1.0)), (10, 4, (2, (6, 7))), (16, 8, (3, (11, 12)))],
)
def test_calculate_num_words_nondefault_entropy(dict_size, entropy, expected):
    result = internal.calculate_num_words(dict_size, entropy=entropy, random_case=False)
    words_needed, actual_entropy = expected
    assert result[0] == words_needed
    if isinstance(actual_entropy, tuple):
        assert actual_entropy[0] <= result[1] <= actual_entropy[1]
    else:
        assert result[1] == actual_entropy


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


def test_sample_words_custom_delimiter(words):
    k = 5
    delim = "_"
    res = internal.sample_words(words, k, delimiter=delim)
    assert res.count(delim) == k - 1
    regex = "^[^{delim}]+({delim}[^{delim}]+){{{n}}}"
    regex = regex.format(delim=delim, n=k - 1)
    assert re.match(regex, res)


def test_sample_words_k_too_large():
    with pytest.raises(ValueError) as err:
        internal.sample_words(["a", "b"], 3, delimiter=" ", random_case=False)
    assert "can't sample 3 of 2 words" == str(err.value)


def test_sample_words_k_max():
    result = internal.sample_words(["a", "b"], 2, delimiter=" ", random_case=False)
    assert result in ["a b", "b a"]


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


def test_load_from_stream_success_default_test(word_file, words):
    expected = sorted(set(w.strip().lower() for w in words))
    with codecs.open(word_file, "r", "utf-8") as f:
        result = internal.load_from_stream(f)
    assert sorted(result) == expected


def test_load_from_stream_yields_sorted_words(tmpdir):
    filepath = str(tmpdir.join("file.txt"))
    with codecs.open(filepath, "w", "utf-8") as f:
        six.print_("1", file=f)
        six.print_("0", file=f)
    expected = ["0", "1"]
    with codecs.open(filepath, "r", "utf-8") as f:
        result = internal.load_from_stream(f)
    assert result == expected


def test_load_from_stream_no_words(tmpdir):
    filepath = str(tmpdir.join("file.txt"))
    with codecs.open(filepath, "w", "utf-8") as f:
        f.write("")
    with codecs.open(filepath, "r", "utf-8") as f:
        with pytest.raises(RuntimeError) as err:
            internal.load_from_stream(f)
    assert "no words loaded" == str(err.value)


@pytest.mark.parametrize("name", ["eff-large", "eff1", "eff2"])
def test_load_words_from_list_success(name):
    assert name in internal.WORD_LISTS
    filename = internal.WORD_LISTS[name]
    dirpath = os.path.join(tests.tests_dir, "..", "mkpassphrase", "wordlists")
    all_filenames = os.listdir(dirpath)
    assert filename in all_filenames
    filepath = os.path.join(dirpath, filename)
    with codecs.open(filepath, "r", "utf-8") as f:
        actual_words = [s.strip().lower() for s in f.readlines()]
        actual_words = list(set(actual_words))
        actual_words.sort()
        actual_words = [w for w in actual_words if w]

    result = internal.load_words_from_list(name)
    assert result == actual_words


def test_load_words_from_list_invalid_wordlist():
    with pytest.raises(ValueError) as err:
        internal.load_words_from_list("nonexistent")
    assert "Invalid wordlist: nonexistent" == str(err.value)
