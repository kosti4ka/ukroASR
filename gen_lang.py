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
            line = re.sub(r'\'{2,}', ' ', line)
            line_splited = line.split()[:1] if utt_id else line.split()
            for w in line_splited:
                w = process_ukr_word(w)
                if w:
                    words.add(w.lower() if lower_case else w)

    # make dir
    if not out_dir.exists():
        os.makedirs(str(out_dir))

    with open(words_path, 'w', encoding='utf-8') as words_f:
        for word in words:
            words_f.write(f'{word}\n')


def process_ukr_word(word):
    word = word.strip('[~!@#$%^&*()_+{}":;\']-+=$0123456789—•')
    if not set('[~!@#$%^&*()_+{}":;].+=$0123456789№qwertyuiopasdfghjklzxcvbnmñōê').intersection(word.lower()):
        return word
    else:
        return None

def lexicon2phonelist(lexicon_path, nonsilence_phones_path):

    # setting paths
    lexicon_path = Path(lexicon_path)
    nonsilence_phones_path = Path(nonsilence_phones_path)

    lexicon = defaultdict(list)
    [lexicon[x.split()[0]].append(x.split()[1:]) for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if x]

    phonemes = []
    for word in lexicon:
        for pron in lexicon[word]:
            phonemes.extend(pron)

    phonemes = sorted(list(set(phonemes)))

    with open(nonsilence_phones_path, 'w', encoding='utf-8') as f:
        for i, p in enumerate(phonemes):
            f.write(f'{i} {p}\n')


def lexicon2letterlist(lexicon_path, letters_path):

    # setting paths
    lexicon_path = Path(lexicon_path)
    letters_path = Path(letters_path)

    lexicon = {x.split()[0]: x.split()[1:] for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if x}

    letters = []
    for l in lexicon:
        letters.extend(list(l))

    letters = sorted(list(set(letters)))

    with open(letters_path, 'w', encoding='utf-8') as f:
        for i, p in enumerate(letters):
            f.write(f'{i} {p}\n')


def gen_lexicon(words_path, lexicon_path, additiona_lexicons=None):

    # setting paths
    words_path = Path(words_path)
    lexicon_path = Path(lexicon_path)
    # oov_words_path = Path(lexicon_dir_path) / 'oov.txt'

    # read optional lexicon
    skip = set()
    if additiona_lexicons:
        for lex_path in additiona_lexicons:
            lex_path = Path(lex_path)
            [skip.add(x.split()[0]) for x in open(lex_path, 'r',  encoding='utf-8').read().split('\n') if x]

    # read word list
    words = [x for x in open(words_path, 'r',  encoding='utf-8').read().split('\n') if x]
    words = sorted(words)

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(4)

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

def clean_lexicons(in_lexicon_path, out_lexicon_path):

    in_lexicon_paths_list = Path(in_lexicon_path)
    out_lexicon_path = Path(out_lexicon_path)

    # read and combining lexicons
    clean_lexicon = defaultdict(list)

    [clean_lexicon[x.split()[0]].append(' '.join(x.split()[1:])) for x in open(in_lexicon_path, 'r', encoding='utf-8').read().split('\n')
     if (x and (' '.join(x.split()[1:]) not in clean_lexicon[x.split()[0]]) and (x.split()[1] not in ['4', '5', '0']))]

    # make dir
    if not out_lexicon_path.parent.exists():
        os.makedirs(str(out_lexicon_path.parent))

    with open(out_lexicon_path, 'w', encoding='utf-8') as f:
        for word in sorted(clean_lexicon.keys()):
            for pron in clean_lexicon[word]:
                f.write(f'{word} {pron}\n')


if __name__ == '__main__':
    # lexicon2phonelist('/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang/nonsilence_phones_new.txt')
    lexicon2phonelist('/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon.txt',
                      '/Users/mac/Datasets/ukrainian/lang.org.ua/phones')
    # lexicon2letterlist('/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/letters')
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
    #             additiona_lexicons=['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_raw.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_1.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_2.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_3.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_4.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_5.txt'])
    # gen_lexicon('/home/ubuntu/kostya/words_small.txt',
    #             '/home/ubuntu/kostya/lexicon.txt',
    #             additiona_lexicons=['/home/ubuntu/kostya/lexicon-1.txt',
    #                                 '/home/ubuntu/kostya/lexicon-2.txt'])
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
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_1.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_2.txt',
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_3.txt'],
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_combined.txt')
    # combine_lexicons(['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_raw.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_1.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_2.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_3.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_4.txt',
    #                                 '/Users/mac/Datasets/ukrainian/lang.org.ua/wiki/dict/lexicon_5.txt'],
    #                   '/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_raw_new.txt')
    # clean_lexicons('/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_raw_new.txt', '/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt')
