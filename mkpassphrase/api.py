# coding-utf-8

from __future__ import absolute_import, division, print_function

from . import internal


def mkpassphrase(
    word_list=None,
    word_file=None,
    entropy=None,
    num_words=None,
    random_case=True,
    delimiter=internal.DELIMITER,
    pad=internal.PAD,
    count=1,
):
    """
    Make one or more passphrases using the given params.

    :params:
    - word_list: name of a builtin wordlist ('eff-large', 'eff1', or 'eff2')
    - word_file: path to a word file, one word per line, encoded with a
            character encoding that is compatible with the python default
            encoding if ``ascii`` is true.
    - entropy: optional bits of entropy minimum that will be used to
           calculate the number of words to use if ``num_words`` not provided,
           or used to verify ``num_words`` is sufficient if both provided.
    - num_words: number of words to include in passphrase (at least 1, if
            provided). If not provided, the number will be calculated
            based on the ``entropy`` (or default entropy if ``entropy``
            not provide).
    - random_case: whether to capitalize first letter of each word with
             probability 0.5
    - delimiter: the delimiter to use for joining the words in the passphrase.
    - pad: a string to use as a prefix and suffix of the generated passphrase.
    - count: positive integer representing the number of passwords to generate,
             defaulting to 1. If greater than one, the ``passphrase`` returned
             will be a list of passphrases. If equal to one, the ``passphrase``
             will be just a string passphrase and not a one-element list.

    :return:
    - passphrase: the generated passphrase (string) or list of passphrases
    - entropy bits: entropy in bits of the generated passphrase(s)
    """
    if not bool(word_file) ^ bool(word_list):
        raise ValueError("exactly one of 'word_list' or " "'word_file' is required")
    if num_words is not None and (not isinstance(num_words, int) or num_words < 1):
        raise ValueError("'num_words' must be a positive integer if provided")
    if not isinstance(count, int) or count < 1:
        raise ValueError("'count' must be a positive integer")

    load, src = (
        (internal.load_words_from_file, word_file)
        if word_file
        else (internal.load_words_from_list, word_list)
    )
    words = load(src)

    # if num words not provided, we calculate how many to
    # use based on entropy target provided (or default if not provided)
    if num_words is None:
        num_words, actual_entropy = internal.calculate_num_words(
            len(words), entropy=entropy, random_case=random_case
        )
    else:
        actual_entropy = internal.calculate_entropy(len(words), num_words, random_case)
        if entropy is not None and actual_entropy < entropy:
            msg = "entropy bits (%s) for %d words is less than %d"
            msg %= (int(actual_entropy), num_words, entropy)
            raise ValueError(msg)

    passphrases = []
    for _ in range(count):
        passphrase = internal.sample_words(
            words, num_words, delimiter=delimiter, random_case=random_case
        )
        passphrase = pad + passphrase + pad
        passphrases.append(passphrase)

    return (passphrases[0] if count == 1 else passphrases), actual_entropy
