# -- coding: utf-8 --
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from lxml import html
from pathlib import Path
from tqdm import tqdm
import multiprocessing as mp
from collections import defaultdict
import json
# from goroh_scraper.scrap import GOROH_URL
# from tools.utils import
import copy

from grab_pron import stress, consonant_modifier, vovel_modifier, vovel, consonant_pair, consonant

SPEECH_PARTS = ['сполучник', 'частка', 'прийменник', 'займенник', 'числівник', 'прислівник', 'прекметник', 'дієслово',
                'іменник']

BASE_LEXICON_PATH = '/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'

GOROH_URL = 'https://goroh.pp.ua/'

USER_AGENTS = [('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'),  # firefox
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36')  # chrome
]

headers = {'User-Agent': USER_AGENTS[0]}


def gen_lexicon_for_word_forms(word_forms_json, base_lexicons):

    # reading lexicons
    combined_lexicon = defaultdict(list)
    for lexicon_path in base_lexicons:
        [combined_lexicon[x.split()[0]].append(' '.join(x.split()[1:])) for x in
         open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if
         (x and ' '.join(x.split()[1:]) not in combined_lexicon[x.split()[0]])]

    # reading word forms
    with open(word_forms_json, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    gen_lexicon_for = []
    for base_word in tqdm(data):
        for word in data[base_word]:
            if word.replace('́', '') not in combined_lexicon:
                gen_lexicon_for.append(base_word.replace('́', ''))

    gen_lexicon_for = list(set(gen_lexicon_for))

    directory_path = Path('/Users/mac/Datasets/ukrainian/goroh/lexicon')

    pool = mp.Pool(8)

    # fire off workers
    jobs = []
    print('preparing...')
    for word in gen_lexicon_for:
        job = pool.apply_async(save_url, (word, f'/Транскрипція/{word}', directory_path))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    print('generating...')
    for job in tqdm(jobs):
        job.get()

    pool.close()
    pool.join()


def save_url(word, url, directory_path):

    save_path = directory_path / f'{word}.html'

    if not save_path.is_file():

        err_code = 0
        try:
            request = Request(url=(GOROH_URL + quote(url)), headers=headers)
            html_source = urlopen(request)

            webContent = html_source.read()

            f = open(save_path, 'wb')
            f.write(webContent)
            f.close

        except HTTPError as err:
            print(f'Error getting page {word} {url}')
            err_code = err.code
            pass
    else:
        print(f'Word {word} already present')


def parse_pron_find_result(pron_result):
    prons = []
    for r in pron_result:
        current_p_split = parse_pron_result(r.text)
        prons.append(current_p_split)

    prons = [' '.join(p) for p in prons]
    prons = list(set(prons))
    prons = [p.split() for p in prons]

    return prons


def parse_pron_result(raw_pron):
    current_p = raw_pron
    begin = current_p.index('[') + 1
    end = current_p.index(']')
    current_p = current_p[begin:end]
    current_p = current_p.replace('{', '')
    current_p = current_p.replace('}', '')
    current_p_split = []
    current_ph = [current_p[0]]
    for ph in current_p[1:]:
        if (ph in stress) or (ph in consonant_modifier):
            current_ph.append(ph)
        elif ph in vovel_modifier and current_ph[-1] in vovel:
            current_ph.append(ph)
        elif ph in consonant_pair and current_ph[-1] in consonant:
            current_ph.append(ph)
        else:
            current_p_split.append(''.join(current_ph))
            current_ph = [ph]
    current_p_split.append(''.join(current_ph))

    return current_p_split


def extract_words_forms(word_path, base_word, part_of_speech, base_lexicon=None):

    url = word_path
    page = open(url)
    soup = BeautifulSoup(page.read(), 'html.parser')
    articles = soup.find_all('div', class_='article-block')

    # check if lexicon page exists
    lexicon_url = Path('/Users/mac/Datasets/ukrainian/goroh/lexicon') / f'{base_word.replace("́", "")}.html'

    if lexicon_url.is_file():
        lexicon_page = open(lexicon_url)
        lexicon_soup = BeautifulSoup(lexicon_page.read(), 'html.parser')
        lexicon_articles = lexicon_soup.find_all('div', class_='article-block')
    else:
        lexicon_articles = None

    results = defaultdict(list)
    for art_idx, article in enumerate(articles):

        tag_list = [t.text.strip() for t in article.find_all('a', class_='tag')]

        # checking part of speech
        if part_of_speech not in tag_list:
            continue

        # find corresponding lexicon article
        lexicon_article = None
        if lexicon_articles:
            for l_a in lexicon_articles:
                lexicon_tag_list = [t.text.strip() for t in l_a.find_all('a', class_='tag')]
                if set(tag_list) == set(lexicon_tag_list):
                    lexicon_article = l_a

        if 'незмінювана словникова одиниця' in article.text:

            pron = []

            # adding lexicon if exists
            if lexicon_article:
                pron = parse_pron_find_result(lexicon_article.findAll('h2'))
                pron = [' '.join(p) for p in pron]
            elif base_lexicon and base_word.replace('́', '') in base_lexicon:
                pron = base_lexicon[base_word.replace('́', '')]

            results[base_word].append(('unchanged', pron))

            break

        # read pronunciation if available
        pron_table = []
        if lexicon_article:
            lexicon_table = lexicon_article.find('table', class_='table')
            if lexicon_table:
                for i, row in enumerate(lexicon_table.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['row'])):
                    pron_table.append([])
                    for j, cell in enumerate(row.find_all(lambda tag: tag.name == 'td' and tag.get('class') == ['cell'])):
                        prons = [' '.join(parse_pron_result(p)) for p in cell.text.split(',') if p != '—']
                        pron_table[i].append(prons)

        table = article.find('table', class_='table')

        if table:
            column_names = table.find('tr', class_='row column-header').text.split('\n')[2:-1]
            row_names = [name.text for name in table.find_all('td', class_='cell header')]

            for i, row in enumerate(table.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['row'])):
                for j, cell in enumerate(row.find_all(lambda tag: tag.name == 'td' and tag.get('class') == ['cell'])):
                    words = [w.strip() for w in cell.text.split(',') if w != '—']
                    for k, word in enumerate(words):
                        if pron_table:
                            if len(pron_table[i][j]) == len(words):
                                pron = [pron_table[i][j][k]]
                            elif len(pron_table[i][j]) == 2 * len(words):
                                pron = [pron_table[i][j][2 * k:2 * k + 1 + 1]]
                            else:
                                pron = []
                        elif base_lexicon and word.replace('́', '') in base_lexicon:
                            pron = base_lexicon[word.replace('́', '')]
                        else:
                            pron = []
                        results[word.strip()].append((row_names[i], column_names[j], pron))

    return base_word, results


def collect_words_forms(urls_list_path, directory_path, part_of_speech, base_lexicons=[BASE_LEXICON_PATH]):

    urls_list_path = Path(urls_list_path)
    directory_path = Path(directory_path)

    # read list of urls
    urls_list = {'_'.join(x.split()[:-1]): x.split()[-1] for x in open(urls_list_path, 'r', encoding='utf-8').read().split('\n') if x}

    # reading base lexicons
    combined_lexicon = defaultdict(list)
    for lexicon_path in base_lexicons:
        [combined_lexicon[x.split()[0]].append(' '.join(x.split()[1:])) for x in
         open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if
         (x and ' '.join(x.split()[1:]) not in combined_lexicon[x.split()[0]])]


######################################################

    results = {}
    for word in tqdm(list(urls_list.keys())):
        word_path = directory_path / f'{word}.html'
        base_word, forms = extract_words_forms(word_path, word, part_of_speech, combined_lexicon)
        results[base_word] = forms

######################################################

    # pool = mp.Pool(8)
    #
    # # fire off workers
    # jobs = []
    # print('preparing...')
    # for word in list(urls_list.keys()):
    #     word_path = directory_path / f'{word}.html'
    #     job = pool.apply_async(extract_words_forms, (word_path, word, part_of_speech, combined_lexicon))
    #     jobs.append(job)
    #
    # # collect results from the workers through the pool result queue
    # print('generating...')
    # results = {}
    # for job in tqdm(jobs):
    #     r = job.get()
    #     results[r[0]] = r[1]
    #
    # pool.close()
    # pool.join()

    with open(directory_path / part_of_speech, 'w', encoding='utf-8') as fp:
        json.dump(results, fp, sort_keys=True, indent=4, ensure_ascii=False)


def words_forms_to_vocab(word_forms_jsons, vocab_path='/Users/mac/Datasets/ukrainian/goroh/vocab'):

    vocab = []
    for words_json in word_forms_jsons:

        with open(words_json, 'r', encoding='utf-8') as fp:
            data = json.load(fp)

        for base_word in tqdm(data):
            for word in data[base_word]:
                vocab.append(word)

    vocab = list(set(vocab))
    with open(vocab_path, 'w', encoding='utf-8') as fp:
        json.dump(vocab, fp, sort_keys=True, indent=4, ensure_ascii=False)




if __name__ == '__main__':

    # extract_words_forms("/Users/mac/Datasets/ukrainian/goroh/zaim/аби́хто.html", "аби́хто", SPEECH_PARTS[3])

    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/spoluch/{SPEECH_PARTS[0]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/chastka/{SPEECH_PARTS[1]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/primenyk/{SPEECH_PARTS[2]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/zaim/{SPEECH_PARTS[3]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/chis/{SPEECH_PARTS[4]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/prisl/{SPEECH_PARTS[5]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/adj/{SPEECH_PARTS[6]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/verb/{SPEECH_PARTS[7]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])
    #
    # gen_lexicon_for_word_forms(f'/Users/mac/Datasets/ukrainian/goroh/noun/{SPEECH_PARTS[8]}',
    #                            ['/Users/mac/Datasets/ukrainian/lang.org.ua/lexicon_new.txt'])

    # extract_words_forms('/Users/mac/Datasets/ukrainian/goroh/zaim/которий.html', 'которий', SPEECH_PARTS[3])

    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/spoluch_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/spoluch', SPEECH_PARTS[0])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/chastka_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/chastka', SPEECH_PARTS[1])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/primenyk_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/primenyk', SPEECH_PARTS[2])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/zaim_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/zaim', SPEECH_PARTS[3])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/chis_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/chis', SPEECH_PARTS[4])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/prisl_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/prisl', SPEECH_PARTS[5])

    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/adj_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/adj', SPEECH_PARTS[6])

    collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/verb_lin_list',
                        '/Users/mac/Datasets/ukrainian/goroh/verb', SPEECH_PARTS[7])
    #
    # collect_words_forms('/Users/mac/Datasets/ukrainian/goroh/noun_lin_list',
    #                     '/Users/mac/Datasets/ukrainian/goroh/noun', SPEECH_PARTS[8])

    # words_forms_to_vocab(['/Users/mac/Datasets/ukrainian/goroh/spoluch/сполучник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/chastka/частка',
    #                       '/Users/mac/Datasets/ukrainian/goroh/primenyk/прийменник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/zaim/займенник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/chis/числівник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/prisl/прислівник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/adj/прекметник',
    #                       '/Users/mac/Datasets/ukrainian/goroh/verb/дієслово',
    #                       '/Users/mac/Datasets/ukrainian/goroh/noun/іменник'])
