from pathlib import Path
import os
from collections import defaultdict
from grab_pron import goroh_g2p
from tqdm import tqdm
import multiprocessing as mp
import re


def words(text_path, out_dir, utt_id=True, lower_case=True):

    text_path = Path(text_path)
    out_dir = Path(out_dir)
    words_path = out_dir / 'words.txt'

    words = set()
    with open(text_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f):
            line_splited = line.split()[:1] if utt_id else line.split()
            for w in line_splited:
                w = process_ukr_word(w)
                if w:
                    words.add(w)

    # make dir
    if not out_dir.exists():
        os.makedirs(str(out_dir))

    with open(words_path, 'w', encoding='utf-8') as words_f:
        for word in words:
            words_f.write(f'{word.lower() if lower_case else word}\n')


def process_ukr_word(word):
    word = word.strip('[~!@#$%^&*()_+{}":;\']-+$0123456789')
    if not set('[~!@#$%^&*()_+{}":;]+$0123456789№qwertyuiopasdfghjklzxcvbnmñōê').intersection(word.lower()):
        return word
    else:
        return None

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


def gen_lexicon(words_path, lexicon_path, skip_words=None):

    # setting paths
    words_path = Path(words_path)
    lexicon_path = Path(lexicon_path)
    # oov_words_path = Path(lexicon_dir_path) / 'oov.txt'

    # read optional lexicon
    skip = set()
    if skip_words:
        for skip_path in skip_words:
            skip_words_path = Path(skip_path)
            [skip.add(x) for x in open(skip_words_path, 'r',  encoding='utf-8').read().split('\n') if x]

    # read word list
    words = [x for x in open(words_path, 'r',  encoding='utf-8').read().split('\n') if x]
    words = sorted(words)

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(18)

    # put listener to work first
    watcher = pool.apply_async(listener, (q, lexicon_path))

    # fire off workers
    jobs = []
    print('preparing...')
    for word in tqdm(words):
        if word not in skip:
            job = pool.apply_async(worker, (word, q))
            jobs.append(job)

    # collect results from the workers through the pool result queue
    print('generating...')
    for job in tqdm(jobs):
        job.get()

    # now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()


def worker(word, q):

    prons = goroh_g2p(word)

    if prons:
        for pron in prons:
            q.put(f'{word} {" ".join(pron)}\n')


def listener(q, file_path):
    '''listens for messages on the q, writes to file. '''

    with open(file_path, 'w') as f:
        while 1:
            m = q.get()
            if m == 'kill':
                break
            f.write(f'{m}')
            f.flush()

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
    # lexicon2phonelist('/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang/nonsilence_phones_new.txt')
    # lexicon2phonelist('/Users/mac/Datasets/ukrainian/panas_yasla/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/panas_yasla/lang/nonsilence_phones.txt')
    # words('/Users/mac/Datasets/ukrainian/texts/text_plane',
    #       '/Users/mac/Datasets/ukrainian/texts/lang')
    # words('/Users/mac/Datasets/ukrainian/lang.org.ua/fiction/fiction.tokenized.shuffled.txt',
    #       '/Users/mac/Datasets/ukrainian/lang.org.ua/fiction/dict', utt_id=False)
    # words('/Users/mac/Datasets/ukrainian/lang.org.ua/ubercorpus/ubercorpus.tokenized.shuffled.txt',
    #       '/Users/mac/Datasets/ukrainian/lang.org.ua/ubercorpus/dict', utt_id=False)
    # words('/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/wiki_dump.tokenized.txt',
    #       '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict', utt_id=False)
    # gen_lexicon('/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/words.txt',
    #             '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon.txt',
    #             skip_words=['/Users/mac/Datasets/ukrainian/lang.org.ua/fiction/dict/words.txt',
    #                         '/Users/mac/Datasets/ukrainian/lang.org.ua/news/dict/words.txt'])
    # gen_lexicon('~/kostya/words.txt',
    #             '~/kostya')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/zapovit/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/kateryna/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lysmykyta/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/prychynna/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/contra/lang/lexicon.txt'],
    #                  '/Users/mac/Datasets/ukrainian/lang/lexicon.txt')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/panas_yasla/lang/lexicon.txt'],
    #                  '/Users/mac/Datasets/ukrainian/lang/lexicon_new.txt')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/texts/lang/laxicon_back',
    #                   '/Users/mac/Datasets/ukrainian/texts/lang/lexicon.txt'],
    #                   '/Users/mac/Datasets/ukrainian/lang/lexicon_full.txt')
    process_ukr_word("**лесько")