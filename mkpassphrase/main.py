# coding=utf-8

"""Main executable module for mkpassphrase, installed as `mkpassphrase`."""

from __future__ import absolute_import, division, print_function

import argparse
import math
import os
import sys


def main():
    """Command-line entry point."""
    import mkpassphrase as MP
    from mkpassphrase import api, internal

    wordlists = sorted(internal.WORD_LISTS)
    parser = argparse.ArgumentParser(description="Generate a passphrase.")
    parser.add_argument(
        "-n",
        "--num-words",
        type=int,
        metavar="NUM_WORDS",
        help="Number of words in passphrase "
        "(the default is enough words to reach a security level of {} bits)".format(
            internal.ENTROPY_DEFAULT
        ),
    )
    parser.add_argument(
        "-s",
        "--entropy",
        type=int,
        metavar="ENTROPY",
        help="Target entropy bits "
        "(the default is {} bits)".format(internal.ENTROPY_DEFAULT),
    )
    parser.add_argument(
        "-w",
        "--word-list",
        type=str,
        metavar="WORD_LIST",
        choices=wordlists,
        help="Use built-in wordlist (eff-large [default], eff1, or eff2)",
    )
    parser.add_argument(
        "-f",
        "--word-file",
        type=str,
        metavar="WORD_FILE",
        help="Word file path (one word per line)",
    )
    parser.add_argument(
        "-l",
        "--lowercase",
        action="store_false",
        dest="random_case",
        default=True,
        help="Lowercase words (the default is to capitalize the first letter"
        "of each word with probability 0.5 and use lowercase "
        "for all other letters)",
    )
    parser.add_argument(
        "-p",
        "--pad",
        metavar="PAD",
        default="",
        help="Pad passphrase using PAD as prefix and suffix "
        "(the default is no padding)",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        dest="delimiter",
        default=" ",
        metavar="DELIMITER",
        help="Use DELIMITER to separate words in passphrase "
        "(the default is a space character)",
    )
    parser.add_argument(
        "-t",
        "--times",
        dest="times",
        type=int,
        default=1,
        metavar="TIMES",
        help="Generate TIMES different passphrases "
        "(the default is to generate 1 passphrase)",
    )
    parser.add_argument("-V", "--version", action="store_true", help="Show version")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Print just the passphrase (the default "
        "is to also show the security-level of the generated passphrase(s))",
    )

    args = parser.parse_args()
    if args.version:
        print("%s %s" % (MP.__name__, MP.__version__))
        sys.exit(0)
    if args.num_words is not None and args.num_words < 1:
        parser.exit("--num-words must be positive if provided")
    if args.times < 1:
        parser.exit("--times must be positive if provided")
    if args.word_list and args.word_file:
        parser.exit("only one of --word-list and --word-file is allowed")
    if args.word_file and not os.access(args.word_file, os.R_OK):
        parser.exit("word file does not exist or is not readable: %s" % args.word_file)

    params = vars(args)
    quiet = params.pop("quiet", False)
    times = params.pop("times", 1)
    params.pop("version", None)

    # use the default wordlist if no list or file was provided
    if not args.word_file and not args.word_list:
        params["word_list"] = internal.WORD_LIST_DEFAULT

    passphrases, entropy = api.mkpassphrase(count=times, **params)
    if times == 1:
        passphrases = [passphrases]
    for passphrase in passphrases:
        print(passphrase)

    if not quiet:
        print()
        print("{}-bit security level".format(int(math.floor(entropy))))


if __name__ == "__main__":
    main()
