============
mkpassphrase
============

.. image:: https://travis-ci.org/eukaryote/mkpassphrase.svg?branch=master
    :target: https://travis-ci.org/eukaryote/mkpassphrase

`mkpassphrase` is a commandline script and an associated library for
generating passphrases by concatenating words chosen from a dictionary file
that contains one word per line.

As of version 2, released in July, 2018, it bundles the three `EFF wordlists`_,
and uses their standard 7,776-word list by default, but can use the
other EFF wordlists or a custom wordlist.

When run with no args, `mkpassphrase` generates a
passphrase like ``exemplify strobe pushover appealing Glimpse Snazzy``, which inserts
a space character between each word and randomly uppercases the first
character of each word with probability 1/2, using enough words to reach
the recommended 80-bit security level, but these choices and others are configurable.

.. _EFF wordlists: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases


Installation
------------

To install or upgrade to the latest stable version of `mkpassphrase` from PyPI,
you can install it as your normal user by running:

.. code-block:: shell-session

    $ pip install --user --upgrade mkpassphrase

On Linux, that installs `mkpasphrase` to `~/.local/bin`, which you may need to
add to your `$PATH`.

Or you can install it globally by running:

.. code-block:: shell-session

    $ sudo pip install --upgrade mkpassphrase


Usage
-----

Generate a passphrase using the default settings:

.. code-block:: shell-session

    $ mkpassphrase
    Octane Flatfoot timid revival Darkened dropkick

    83-bit security level

The security level reported is based only on the number of words in the
passphrase and the number of possible words (as well as whether
the ``--lowercase`` option is chosen), and does not include other factors
such as padding or a custom delimiter, which would increase the security
level. You can also add the ``-q`` option to only see the passphrases.

You can use the ``-t NUM`` option to generate multiple passphrases if you
want more options to choose from:

.. code-block:: shell-session

  $ mkpassphrase -t 10
  disposal Linoleum antibody petty Nucleus Unzip
  Banish Barterer doorway avenging Errand tasting
  poking disband Precook Ought pronounce procedure
  rambling Flanking trimness heaving Dock Corned
  overfull Evade Army fever sled Enjoyment
  fancied Maternal pawing Marmalade Synapse Ruse
  willow Hatless moving Dealmaker Mammogram share
  perm broker only company Privacy Animation
  composure Header polo prewar Unaware Creation
  Entomb unselfish Shrewdly rundown snuff Wing

  83-bit security level


Options
-------

Use the `--help` option to see the available options:

.. code-block:: shell-session

    $ mkpassphrase --help
    usage: mkpassphrase [-h] [-n NUM_WORDS] [-s ENTROPY] [-w WORD_LIST]
                        [-f WORD_FILE] [-l] [-p PAD] [-d DELIMITER] [-t TIMES]
                        [-V] [-q]

    Generate a passphrase.

    optional arguments:
    -h, --help            show this help message and exit
    -n NUM_WORDS, --num-words NUM_WORDS
                            Number of words in passphrase (the default is enough
                            words to reach a security level of 80 bits)
    -s ENTROPY, --entropy ENTROPY
                            Target entropy bits (the default is 80 bits)
    -w WORD_LIST, --word-list WORD_LIST
                            Use built-in wordlist (eff-large [default], eff1, or
                            eff2)
    -f WORD_FILE, --word-file WORD_FILE
                            Word file path (one word per line)
    -l, --lowercase       Lowercase words (the default is to capitalize the
                            first letterof each word with probability 0.5 and use
                            lowercase for all other letters)
    -p PAD, --pad PAD     Pad passphrase using PAD as prefix and suffix (the
                            default is no padding)
    -d DELIMITER, --delimiter DELIMITER
                            Use DELIMITER to separate words in passphrase (the
                            default is a space character)
    -t TIMES, --times TIMES
                            Generate TIMES different passphrases (the default is
                            to generate 1 passphrase)
    -V, --version         Show version
    -q, --quiet           Print just the passphrase (the default is to also show
                            the security-level of the generated passphrase(s))


Supported Python Versions and Operating Systems
-----------------------------------------------

mkpassphrase is supported on Python-2.7 (CPython or PyPy), Python-3.4+ for
CPython, and Python-3.5+ for PyPy. It is tested on Linux, but should work on
any OS with a supported Python version.
