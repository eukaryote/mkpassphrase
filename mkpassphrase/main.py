import sys
import os
import argparse

import mkpassphrase as M


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='Generate a passphrase.')
    parser.add_argument('--num-words', type=int, metavar='NUM_WORDS',
                        help='Number of words in passphrase', default=M.WORDS)
    parser.add_argument('--min', type=int, metavar='MIN',
                        help='Minimum word length', default=M.MIN)
    parser.add_argument('--max', type=int, metavar='MAX',
                        help='Maximum word length', default=M.MAX)
    parser.add_argument('--word-file', type=str, metavar='WORD_FILE',
                        help='Word file path (one word per line)',
                        default=M.WORD_FILE)
    parser.add_argument('--no-random-case', action='store_false',
                        dest='random_case', default=True,
                        help='Whether to randomly capitalize '
                             'the first letter of each word')
    parser.add_argument('--non-ascii', action='store_false',
                        dest='ascii', default=True,
                        help='Whether to allow words with non-ascii letters')
    parser.add_argument('-p', '--pad', metavar='PAD', default='',
                        help='Pad passphrase using PAD as prefix and suffix')

    args = parser.parse_args()
    if args.min > args.max:
        parser.exit("--max must be equal to or greater than --min")
    if args.min < 1 or args.max < 1:
        parser.exit('--min and --max must be positive')
    if args.num_words < 1:
        parser.exit('--num-words must be positive')
    if not os.access(args.word_file, os.R_OK):
        parser.exit("word file does not exist or is not readable: %s" %
                    args.word_file)

    passphrase, num_candidates = M.mk_passphrase(
        path=args.word_file, min=args.min, max=args.max,
        num_words=args.num_words, random_case=args.random_case, pad=args.pad)
    possibilities = M.num_possible(num_candidates, args.num_words)

    print(passphrase)
    print("{0:,g} unique candidate words".format(num_candidates))
    print("{0:,g} possible passphrases".format(possibilities))


if __name__ == '__main__':
    main()
