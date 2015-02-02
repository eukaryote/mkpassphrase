# mkpassphrase

[![Build Status](https://travis-ci.org/eukaryote/mkpassphrase.svg?branch=master)](https://travis-ci.org/eukaryote/mkpassphrase)

`mkpassphrase` is a commandline script (and associated package) for generating
passphrases by concatenating words chosen from a dictionary file that
contains one word per line.

# Installation (stable version from pypi)

```console
# user install to ~/.local/bin on *nix
pip install --user --upgrade mkpassphrase
```

# Usage

```console
~ » mkpassphrase
brusque Autumn advise Oratory
60,298 unique candidate words
1.32181e+19 possible passphrases
```

# Options

```console
~ » mkpassphrase --help
usage: main.py [-h] [-n NUM_WORDS] [--min MIN] [--max MAX] [-f WORD_FILE]
               [--lowercase] [--non-ascii] [-p PAD] [-d DELIM] [-V]

Generate a passphrase.

optional arguments:
  -h, --help            show this help message and exit
  -n NUM_WORDS, --num-words NUM_WORDS
                        Number of words in passphrase
  --min MIN             Minimum word length
  --max MAX             Maximum word length
  -f WORD_FILE, --word-file WORD_FILE
                        Word file path (one word per line)
  --lowercase           Make each word entirely lowercase, rather than the
                        default behavior of choosing Titlecase or lowercase
                        for each word (with probability 0.5)
  --non-ascii           Whether to allow words with non-ascii letters
  -p PAD, --pad PAD     Pad passphrase using PAD as prefix and suffix
  -d DELIM, --delimiter DELIM
                        Use DELIM to separate words in passphrase
  -V, --version         Show version
~ »
```

# Supported Python Versions and Operating Systems

mkpassphrase is tested under py27, py32, py33, py34, and pypy on Linux, but
should work on any OS that supports those Python versions.
