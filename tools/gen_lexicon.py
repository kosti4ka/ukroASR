#!/usr/bin/env python3.6
import subprocess

import argparse
from tools.utils import get_list, get_lexicon
from pathlib import Path
from ukro_g2p.predict import G2P
# import unicode
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import torch


BASE_LEXICON_PATH = '/data/exp/kostya/ukroASR/artifacts/lexicon.txt'
G2P_MODEL_NAME = 'ukro-base-uncased'


def create_chunks(iterable, num_chunks):
    for i in range(0, num_chunks):
        yield iterable[i::num_chunks]


def gen_lexicon(in_vocab_path, out_lex_path, base_lexicons=[BASE_LEXICON_PATH], num_workers=1):
    """
    Generates lexicon for given vocabulary
    :param in_vocab_path: in vocabulary path
    :param out_lex_path: out lexicon path
    :param base_lexicons: list of base lexicons
    :param num_workers: number of workers
    :return:
    """

    # init paths
    out_lex_path = Path(out_lex_path)
    out_lex_path.parent.mkdir(parents=True, exist_ok=True)

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

    executor = ProcessPoolExecutor(max_workers=num_workers)
    futures = []
    for vocab_chunk in create_chunks(oov_vocab, num_workers):
        futures.append(executor.submit(partial(gen_g2p, vocab_chunk)))

    for future in futures:
        # extend base lexicon with OOVs
        base_lexicon.update(future.result())

    out_lexicon = {word: base_lexicon[word] for word in vocab if word in base_lexicon}

    # writing out lexicon
    with open(out_lex_path, 'w', encoding='utf-8') as f:
        for word in out_lexicon:
            for pron in out_lexicon[word]:
                f.write(f'{word} {" ".join(pron)}\n')


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
    # TODO move pbar outside process
    for word in tqdm(word_list):
        try:
            pron = g2p(word)
            if pron:
                lexicon[word] = [pron]
            else:
                pass
                # subprocess.call(f'echo Failed on: {word.encode("utf-8")}', shell=True)
        except:
            # TODO move it to logger
            # subprocess.call(f'echo Failed on: {word.encode("utf-8")}', shell=True)
            pass

    return lexicon


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vocab', help='path to a vocabulary file', required=True)
    parser.add_argument('-o', '--out_lex', help='path to the generated lexicon', required=True)
    parser.add_argument('-n', '--num_workers', help='number of workers', required=False, type=int)

    args = parser.parse_args()

    gen_lexicon(args.vocab, args.out_lex, num_workers=args.num_workers)
