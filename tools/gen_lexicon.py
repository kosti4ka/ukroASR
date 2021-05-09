#!/usr/bin/env python3.6
import subprocess

import argparse
from tools.utils import get_list, get_lexicon
from pathlib import Path
from ukro_g2p.predict import G2P
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import torch


BASE_LEXICON_PATH = '/data/exp/kostya/ukroASR/artifacts/lexicon.txt'
G2P_MODEL_NAME = 'ukro-base-uncased'


def create_chunks(iterable, num_chunks):
    for i in range(0, num_chunks):
        yield iterable[i::num_chunks]


def gen_lexicon(in_vocab_path, out_lex_path, base_lexicons=[BASE_LEXICON_PATH], num_workers=1, write_lexicon_oov=True):
    """
    Generates lexicon for given vocabulary
    :param in_vocab_path: in vocabulary path
    :param out_lex_path: out lexicon path
    :param base_lexicons: list of base lexicons
    :param num_workers: number of workers
    :param write_lexicon_oov: if True, saves words with no pronunciation to the file 'lexicon_oov.txt'
    :return:
    """

    # init paths
    out_lex_path = Path(out_lex_path)
    out_lex_path.parent.mkdir(parents=True, exist_ok=True)

    oov_out_path = out_lex_path.parent / 'lexicon_oov.txt' if write_lexicon_oov else None

    # read vocabulary file
    vocab = get_list(in_vocab_path)

    # deduplicate vocab
    vocab = list(set(vocab))

    # read base lexicon
    base_lexicon = {}
    if base_lexicons:
        for lex_path in base_lexicons:
            base_lexicon.update(get_lexicon(lex_path))

    oov_vocab = [word for word in vocab if word not in base_lexicon]
    print(f'Num words to generate pronunciations: {len(oov_vocab)}')

    executor = ProcessPoolExecutor(max_workers=num_workers)
    futures = []
    lexicon_oov = []
    for vocab_chunk in create_chunks(oov_vocab, num_workers):
        futures.append(executor.submit(partial(gen_g2p, vocab_chunk)))

    for future in futures:
        # extend base lexicon with OOVs
        base_lexicon.update(future.result()[0])
        lexicon_oov.extend(future.result()[1])

    out_lexicon = {word: base_lexicon[word] for word in vocab if word in base_lexicon}

    # writing out lexicon
    with open(out_lex_path, 'w', encoding='utf-8') as f:
        for word in out_lexicon:
            for pron in out_lexicon[word]:
                f.write(f'{word} {" ".join(pron)}\n')

    # writing out oov words
    if oov_out_path:
        with open(oov_out_path, 'w', encoding='utf-8') as f:
            for word in lexicon_oov:
                f.write(f'{word}\n')


def gen_g2p(word_list, variants=1):
    """
    Generates pronunciations for words from the given list using g2p model
    :param word_list: input list of words
    :param variants: max number of pronunciations for each word
    :return lexicon: generated lexicon
    """

    # init g2p model
    g2p = G2P(G2P_MODEL_NAME)

    # set number of processors available for pytorch
    torch.set_num_threads(1)

    # generating lexicon
    lexicon = {}
    lexicon_oov = []
    # TODO move pbar outside process
    for word in tqdm(word_list):
        try:
            pron = g2p(word)
            if pron:
                lexicon[word] = [pron]
            else:
                lexicon_oov.append(word)
        except:
            # TODO move it to logger
            lexicon_oov.append(word)

    return lexicon, lexicon_oov


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vocab', help='path to a vocabulary file', required=True)
    parser.add_argument('-o', '--out_lex', help='path to the generated lexicon', required=True)
    parser.add_argument('-nj', '--num_jobs', help='number of jobs', required=False, type=int, default=1)

    args = parser.parse_args()

    gen_lexicon(args.vocab, args.out_lex, num_workers=args.num_jobs)
