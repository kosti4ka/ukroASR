# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from lxml import html
from pathlib import Path
from tqdm import tqdm
import multiprocessing as mp


GOROH_URL = 'https://goroh.pp.ua/'
USER_AGENTS = [('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'),  # firefox
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'),  # chrome
               ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36')  # chrome
]

headers = {'User-Agent': USER_AGENTS[3]}


def scrap_for_urls(part_path, out_link_list):
    """
    scraps https://goroh.pp.ua/ acording to pattern and saves urls

    """

    out_link_list = Path(out_link_list)

    # part of path converted to utf-8
    part_path = [quote(part) for part in part_path]

    with open(out_link_list, 'w', encoding='utf-8') as out_file:
        err_code = 0
        i = 0
        while err_code == 0:
            request = Request(url=(GOROH_URL + '/'.join(part_path) + '/' + str(i)), headers=headers)

            err_code = 0
            # try:
            html_source = urlopen(request)
            # except HTTPError as err:
            #     err_code = err.code


            if err_code == 0:
                soup = BeautifulSoup(html_source, 'html.parser')

                results = soup.findAll('li', attrs={'class': 'content-list__item'})
                for r in results:
                    out_file.write(f"{r.find('a').string} {r.find('a').get('href')}\n")

            i += 1


def scrap_for_pages(urls_list_path, directory_path):

    urls_list_path = Path(urls_list_path)
    directory_path = Path(directory_path)

    if not directory_path.exists():
        directory_path.mkdir()

    # read list of urls
    urls_list = {'_'.join(x.split()[:-1]): x.split()[-1] for x in open(urls_list_path, 'r', encoding='utf-8').read().split('\n') if x}

    pool = mp.Pool(1)

    # fire off workers
    jobs = []
    print('preparing...')
    for word in tqdm(list(urls_list.keys())[44430+13000+36500+6000:]):
        job = pool.apply_async(save_url, (word, urls_list[word], directory_path))
        jobs.append(job)

    # collect results from the workers through the pool result queue
    print('generating...')
    for job in tqdm(jobs):
        job.get()

    pool.close()
    pool.join()


def save_url(word, url, directory_path):

    request = Request(url=(GOROH_URL + quote(url)), headers=headers)

    err_code = 0
    try:
        html_source = urlopen(request)
    except HTTPError as err:
        print((word, url))
        err_code = err.code
        pass

    webContent = html_source.read()

    save_path = directory_path / f'{word}.html'

    f = open(save_path, 'wb')
    f.write(webContent)
    f.close


# def parse_page(page_path):
#     page_path = Path(page_path)



if __name__ == '__main__':
    # scrap_for_urls(['Словозміна', '[сполучник]'], '/Users/mac/Datasets/ukrainian/goroh/spoluch_lin_list')
    # scrap_for_urls(['Словозміна', '[дієслово]'], '/Users/mac/Datasets/ukrainian/goroh/verb_lin_list')
    # scrap_for_urls(['Словозміна', '[іменник]'], '/Users/mac/Datasets/ukrainian/goroh/noun_lin_list')
    # scrap_for_urls(['Словозміна', '[прикметник]'], '/Users/mac/Datasets/ukrainian/goroh/adj_lin_list')
    # scrap_for_urls(['Словозміна', '[займенник]'], '/Users/mac/Datasets/ukrainian/goroh/zaim_lin_list')
    # scrap_for_urls(['Словозміна', '[числівник]'], '/Users/mac/Datasets/ukrainian/goroh/chis_lin_list')
    # scrap_for_urls(['Словозміна', '[прислівник]'], '/Users/mac/Datasets/ukrainian/goroh/prisl_lin_list')
    # scrap_for_urls(['Словозміна', '[прийменник]'], '/Users/mac/Datasets/ukrainian/goroh/primenyk_lin_list')
    # scrap_for_urls(['Словозміна', '[частка]'], '/Users/mac/Datasets/ukrainian/goroh/chastka_lin_list')

    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/spoluch_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/spoluch')
    scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/verb_lin_list',
                    '/Users/mac/Datasets/ukrainian/goroh/verb')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/noun_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/noun')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/adj_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/adj')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/zaim_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/zaim')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/chis_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/chis')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/prisl_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/prisl')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/primenyk_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/primenyk')
    # scrap_for_pages('/Users/mac/Datasets/ukrainian/goroh/chastka_lin_list',
    #                 '/Users/mac/Datasets/ukrainian/goroh/chastka')