# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from lxml import html


stress = ['́']

consonant_modifier = ['`', '‛', ':']

vovel_modifier = ['е', 'и', 'у']
vovel = ['е', 'и', 'о', 'і']

consonant = ['д']
consonant_pair = ['з', 'ж']



def goroh_g2p(word):
    """
    Generates pronunciation for the word using https://goroh.pp.ua/
    :param word: word in ukrainian language
    :return: list of pronunciations
    """

    # define initial parameters for the url request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    gorh_url = 'https://goroh.pp.ua/'

    # task and word converted to utf-8
    dictionary = quote('Транскрипція')
    word_utf = quote(word)

    request = Request(url=(gorh_url + '/' + dictionary + '/' + word_utf), headers=headers)

    results = []
    try:
        html_source = urlopen(request)
        soup = BeautifulSoup(html_source, 'html.parser')

        # checking that we get word what we asked for
        ppage_header = soup.find('h1', attrs={'class': 'page__header-title'})
        header_word = ppage_header.text.translate('\rnt').strip().split()[0]

        if header_word.lower() == word.lower():
            # in results we are lookin for transcription in bold on the site
            results = soup.findAll('span', attrs={'class': 'word searched-word'})
            if not results:
                results = soup.findAll('h2')
        else:
            print(f'{word} not found')
    except:
        pass

    prons = []
    for r in results:
        current_p = r.text
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
        prons.append(current_p_split)

    prons = [' '.join(p) for p in prons]
    prons = list(set(prons))
    prons = [p.split() for p in prons]

    return prons


if __name__ == '__main__':
    words = ['знемігся', 'одчинила', 'одчинить', 'он', 'опівночі', 'орда', 'орел', 'орлинії', 'осоки', 'осоці', 'ось', 'отаку-то', 'ото', 'отоді', 'очереті', 'очі', 'пари', 'перекликались', 'переполоху', 'перстень', 'питать', 'плугатир', 'по', 'повиринали', 'пограємось', 'погуляймо', 'подивилась', 'подивляться', 'подруженьки', 'поділиться', 'поки', 'покину', 'покинув', 'покрились', 'поле', 'полине', 'полину', 'положила', 'полюбила', 'полі', 'пом\'янути', 'поможе', 'понад', 'понесе', 'попи', 'поробила', 'породила', 'пору', 'посадили', 'посвіти', 'поспішай', 'потопав', 'поховайте', 'поховали', 'пошли', 'правди', 'при', 'привітає', 'прийшли', 'прилітає', 'причинна', 'причину', 'провожала', 'прости', 'пташка', 'півні', 'під', 'підкралися', 'підійма', 'пісеньку', 'пішла', 'пішов', 'раз', 'реве', 'реве', 'ревучий', 'робить', 'розбивши', 'розкаже', 'розлучили', 'розплете', 'розігнався', 'русалонька', 'русалоньки', 'руці', 'ріже', 'сама', 'самий', 'самого', 'світи', 'світом', 'сердешную', 'сердитий', 'серед', 'серце', 'серця', 'сидячи', 'сизокрила', 'сина', 'синім', 'сиротина', 'сиротою', 'сироту', 'сичі', 'скажені', 'скрипів', 'скрізь', 'скучала', 'словом', 'слід', 'слізоньки', 'сміючись', 'сокіл', 'соловейко', 'солом\'яний', 'сонна', 'сонце', 'спала', 'спить', 'спотикнеться', 'спочинем', 'співали', 'співають', 'співає', 'срібний', 'стала', 'степу', 'стовбуру', 'стогне', 'стоїть', 'ступає', 'сумує', 'схаменулись', 'сьогодні', 'сяє', 'сім\'ї', 'та', 'так', 'така', 'таке', 'такеє', 'таку', 'там', 'татарин', 'тая', 'твоя', 'те', 'темному', 'теє', 'ти', 'тим', 'тихим', 'то', 'тобою', 'товаришу', 'товариші', 'того', 'той', 'торік', 'треті', 'ту', 'тута', 'тіло', 'тії', 'у', 'убив', 'убито', 'угору', 'уже', 'україни', 'умру', 'уночі', 'уроду', 'уст', 'усі', 'утомився', 'ух', 'хата', 'хвилю', 'хмари', 'ходи', 'ходили', 'ходить', 'ходя', 'ходім', 'ходімо', 'хоче', 'хто', 'хустку', 'цікаві', 'цілує', 'часом', 'червону', 'червоніє', 'чи', 'чистім', 'човен', 'чорнобривий', 'чорнобриву', 'чорнобровий', 'чорні', 'чорніє', 'чужому', 'чужії', 'чути', 'чує', 'швидче', 'шелеснули', 'шелест', 'шепчуть', 'широкий', 'широкого', 'широкополі', 'шукати', 'шукає', 'щаслива', 'щастя', 'ще', 'щебетати', 'щебече', 'щиро', 'що', 'щоб', 'щоніч', 'щось', 'я', 'явір', 'як', 'якби-то', 'ялину', 'ями', 'яму', 'ясен', 'і', 'іде', 'ідуть', 'ідучи', 'із', 'ізлякать', 'ізнемігся', 'їй', 'їх', 'її']
    for w in words:
        prons = goroh_g2p(w)
        prons = [' '.join(p) for p in prons]
        prons = list(set(prons))
        for p in prons:
            print(f'{w} {p}')