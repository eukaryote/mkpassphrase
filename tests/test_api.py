# coding=utf-8

import six

import pytest

from mkpassphrase import api, internal


def test_mkpassword_defaults(word_file):
    assert internal.load_words_from_file(word_file)
    passphrase, entropy = api.mkpassphrase(word_file=word_file)
    assert entropy > 0
    passphrase_words = passphrase.split(internal.DELIMITER)
    assert len(passphrase_words) > 1
    for word in passphrase_words:
        assert passphrase.startswith(internal.PAD)
        assert passphrase.endswith(internal.PAD)


def test_mkpassword_not_file_and_list(word_file):
    with pytest.raises(ValueError) as err:
        api.mkpassphrase(word_file=word_file, word_list=internal.WORD_LIST_DEFAULT)
    assert "exactly one of" in str(err.value)


@pytest.mark.parametrize("num_words", [0, "1"])
def test_mkpassword_must_be_positive_int(word_file, num_words):
    with pytest.raises(ValueError) as err:
        api.mkpassphrase(num_words=num_words, word_file=word_file)
    assert "must be a positive integer" in str(err.value)
    assert "'num_words'" in str(err.value)


@pytest.mark.parametrize("count", [0, 1.0, "2"])
def test_mkpassphrase_count_must_be_positive_int(word_file, count):
    with pytest.raises(ValueError) as err:
        api.mkpassphrase(num_words=3, word_file=word_file, count=count)
    assert "must be a positive integer" in str(err.value)
    assert "'count'" in str(err.value)


def test_mkpassphrase_entropy_provided_insufficient_words(tmpdir):
    words = ["true", "false"]
    tmpfile = tmpdir.join("words.txt")
    with tmpfile.open("w") as f:
        for word in words:
            six.print_(word, file=f)
    path = str(tmpfile)
    with pytest.raises(ValueError) as err:
        api.mkpassphrase(num_words=1, word_file=path, random_case=False, entropy=2)
    assert "entropy bits (1) for 1 words is less than 2" == str(err.value)


def test_mkpassphrase_entropy_provided_exactly_enough(tmpdir):
    words = [str(i) for i in range(4)]
    assert len(words) == 4
    tmpfile = tmpdir.join("words.txt")
    entropy = 2
    with tmpfile.open("w") as f:
        for word in words:
            six.print_(word, file=f)
    path = str(tmpfile)
    result, security_level = api.mkpassphrase(
        num_words=1, word_file=path, random_case=False, entropy=entropy
    )
    assert result in words
    assert security_level == entropy


def test_mkpassphrase_delim(word_file):
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
