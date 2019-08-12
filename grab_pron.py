# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from lxml import html




headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
reg_url = 'https://goroh.pp.ua/'
tr = quote('Транскрипція/бистрім')

req = Request(url=(reg_url + tr), headers=headers)
html = urlopen(req)
soup = BeautifulSoup(html, 'html.parser')
print(html)
