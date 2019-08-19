from pathlib import Path
import os
from collections import defaultdict
from grab_pron import goroh_g2p
from tqdm import tqdm


def words(text_path, out_dir, utt_id=True):

    text_path = Path(text_path)
    out_dir = Path(out_dir)
    words_path = out_dir / 'words.txt'

    text = [x.split() for x in open(text_path, 'r', encoding='utf-8').read().split('\n') if x]

    words = []
    for t in text:
        if utt_id:
            words.extend(t[1:])
        else:
            words.extend(t)

    words = sorted(list(set(words)))

    # make dir
    if not out_dir.exists():
        os.makedirs(str(out_dir))

    with open(words_path, 'w', encoding='utf-8') as words_f:
        for word in words:
            words_f.write(f'{word}\n')


def lexicon2phonelist(lexicon_path, nonsilence_phones_path):

    # setting paths
    lexicon_path = Path(lexicon_path)
    nonsilence_phones_path = Path(nonsilence_phones_path)

    lexicon = {x.split()[0]: x.split()[1:] for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if x}

    phones = []
    for l in lexicon:
        phones.extend(lexicon[l])

    phones = sorted(list(set(phones)))

    with open(nonsilence_phones_path, 'w', encoding='utf-8') as f:
        for p in phones:
            f.write(f'{p}\n')


def gen_lexicon(words_path, lexicon_dir_path, optional_lexicon_path=None):

    # setting paths
    words_path = Path(words_path)
    lexicon_path = Path(lexicon_dir_path) / 'lexicon.txt'
    oov_words_path = Path(lexicon_dir_path) / 'oov.txt'

    # read optional lexicon
    if optional_lexicon_path:
        optional_lexicon_path = Path(optional_lexicon_path)
        optional_lexicon = defaultdict(list)
        [optional_lexicon[x.split()[0]].append(x.split()[1:]) for x in open(optional_lexicon_path, 'r').read().split('\n') if x]
    else:
        optional_lexicon = {}

    # read word list
    words = [x for x in open(words_path, 'r').read().split('\n') if x]
    words = sorted(words)

    # generating lexicon and oov word list
    lexicon = {}
    oov = []
    for word in tqdm(words):
        if word in optional_lexicon:
            lexicon[word] = optional_lexicon[word]
        else:
            prons = goroh_g2p(word)
            if prons:
                lexicon[word] = prons
            else:
                oov.append(word)

    with open(lexicon_path, 'w', encoding='utf-8') as f:
        for word in lexicon:
            for pron in lexicon[word]:
                f.write(f'{word} {" ".join(pron)}\n')

    with open(oov_words_path, 'w', encoding='utf-8') as f:
        for word in oov:
            f.write(f'{word}\n')


def combine_lexicons(lexicon_paths_list, out_lexicon_path):

    lexicon_paths_list = [Path(lexicon_path) for lexicon_path in lexicon_paths_list]
    out_lexicon_path = Path(out_lexicon_path)

    # read and combining lexicons
    combined_lexicon = defaultdict(list)
    for lexicon_path in lexicon_paths_list:
        [combined_lexicon[x.split()[0]].append(' '.join(x.split()[1:])) for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if (x and ' '.join(x.split()[1:]) not in combined_lexicon[x.split()[0]])]

    # make dir
    if not out_lexicon_path.parent.exists():
        os.makedirs(str(out_lexicon_path.parent))

    with open(out_lexicon_path, 'w', encoding='utf-8') as f:
        for word in sorted(combined_lexicon.keys()):
            for pron in combined_lexicon[word]:
                f.write(f'{word} {pron}\n')


if __name__ == '__main__':
    lexicon2phonelist('/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
                      '/Users/mac/Datasets/ukrainian/lang/nonsilence_phones_new.txt')
    # words('/Users/mac/Datasets/ukrainian/glibov/data/text',
    #       '/Users/mac/Datasets/ukrainian/glibov/lang')
    # gen_lexicon('/Users/mac/Datasets/ukrainian/glibov/lang/words.txt',
    #             '/Users/mac/Datasets/ukrainian/glibov/lang',
    #             optional_lexicon_path='/Users/mac/Datasets/ukrainian/lang/lexicon.txt')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/zapovit/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/kateryna/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lysmykyta/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/prychynna/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/contra/lang/lexicon.txt'],
    #                  '/Users/mac/Datasets/ukrainian/lang/lexicon.txt')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/glibov/lang/lexicon.txt'],
    #                  '/Users/mac/Datasets/ukrainian/lang/lexicon_new.txt')