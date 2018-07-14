# coding=utf-8

"""Main executable module for mkpassphrase, installed as `mkpassphrase`."""

from __future__ import absolute_import, division, print_function

import argparse
import math
import os
import sys

import mkpassphrase as M


def main(argv=None):
    """Command-line entry point."""
    if argv is None:
        argv = sys.argv
    wordlists = sorted(M.WORD_LISTS)
    parser = argparse.ArgumentParser(description="Generate a passphrase.")
    parser.add_argument(
        "-n",
        "--num-words",
        type=int,
        metavar="NUM_WORDS",
        help="Number of words in passphrase",
    )
    parser.add_argument(
        "-s", "--entropy", type=int, metavar="ENTROPY", help="Target entropy bits"
    )
    parser.add_argument(
        "-w",
        "--word-list",
        type=str,
        metavar="WORD_LIST",
        choices=wordlists,
        help="Use built-in wordlist",
    )
    parser.add_argument(
        "-f",
        "--word-file",
        type=str,
        metavar="WORD_FILE",
        help="Word file path (one word per line)",
    )
    parser.add_argument(
        "-r",
        "--random-case",
        action="store_true",
        dest="random_case",
        help="Capitalize first character of each word " "with probability 0.5",
    )
    parser.add_argument(
        "-p",
        "--pad",
        metavar="PAD",
        default="",
        help="Pad passphrase using PAD as prefix and suffix",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        dest="delimiter",
        default=" ",
        metavar="DELIM",
        help="Use DELIM to separate words in passphrase",
    )
    parser.add_argument(
        "-t",
        "--items",
        dest="times",
        type=int,
        default=1,
        metavar="TIMES",
        help="Generate TIMES different " "passphrases",
    )
    parser.add_argument("-V", "--version", action="store_true", help="Show version")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Print just the passphrase"
    )

    args = parser.parse_args()
    if args.version:
        print("%s %s" % (M.__name__, M.__version__))
        sys.exit(0)
    if args.num_words is not None and args.num_words < 1:
        parser.exit("--num-words must be positive if provided")
    if args.times < 1:
        parser.exit("--times must be positive")
    if args.word_list and args.word_file:
        parser.exit("only one of --word-list and --word-file is allowed")
    if args.word_file and not os.access(args.word_file, os.R_OK):
        parser.exit("word file does not exist or is not readable: %s" % args.word_file)

    params = vars(args)
    quiet = params.pop("quiet", False)
    times = params.pop("times", 1)
    params.pop("version", None)
    if not args.word_file and not args.word_list:
        params["word_list"] = M.WORD_LIST_DEFAULT
    passphrases, entropy = M.mkpassphrase(count=times, **params)
    if times == 1:
        passphrases = [passphrases]
    for passphrase in passphrases:
        print(passphrase)

    if not quiet:
        print()
        print("{}-bit security level".format(int(math.floor(entropy))))


if __name__ == "__main__":
    main()
