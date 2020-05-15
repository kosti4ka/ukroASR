#!/usr/bin/env python3.6

import argparse
from tools.utils import get_list
from pathlib import Path


def gen_lexicon(in_vocab_path, out_lex_path):
    """
    Generates lexicon for given vocabulary
    :param in_vocab_path: in vocabulary path
    :param out_lex_path: out lexicon path
    :return:
    """

    # setting paths
    in_vocab_path = Path(in_vocab_path)
    out_lex_path = Path(out_lex_path)

    # read vocabulary file
    vocab = get_list(in_vocab_path)

    # deduplicate vocab
    vocab = list(set(vocab))


    pass
def gen_g2p(word_list, variants=1):
    """
    Generates pronunciations for words from the given list
    :param word_list: input list of words
    :param out_lex_path: out lexicon path
    :return:
    """


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vocab', help='path to a vocabulary file', required=True)
    parser.add_argument('-o', '--out_lex', help='path to the generated lexicon.', required=True)

    args = parser.parse_args()

    gen_lexicon(args.vocab, args.out_lex)