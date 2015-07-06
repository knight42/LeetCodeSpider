#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

import os
import requests
import itertools
from urllib.parse import urljoin
from collections import defaultdict
from bs4 import BeautifulSoup, SoupStrainer, re

class PageError(Exception):
    def __init__(self, text, url):
        self.msg = text
        self.url = url
    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)

class LoginError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'Fail to login! Please check your username or password.'

class Crawler:
    def __init__(self, debug=False):
        self.BASEURL = 'https://leetcode.com/problemset/'
        self.DEBUG = debug
        self.BASEDIR = os.path.dirname(__file__)
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    def get_soup(self, url, strainer=None):
        html = self.session.get(url, timeout=10)
        soup = BeautifulSoup(html.content, parse_only=strainer)
        return soup

    def get_tags(self):
        soup = self.get_soup(self.BASEURL, SoupStrainer(class_='list-group-item'))
        content = soup.find_all('a', onclick=None)
        tagdict = {}
        for item in content:
            # data: count title url
            count, title, url = list(item.stripped_strings)
            title = title.replace(' ','-').lower()
            tagdict[title] = ( count, urljoin(self.BASEURL, item['href']) )
        return tagdict

    def login(self, username, passwd):
        loginurl = 'https://leetcode.com/accounts/login/'
        self.session.headers['Referer'] = loginurl
        self.session.get(loginurl)
        token = self.session.cookies['csrftoken']
        payload = {
            'csrfmiddlewaretoken': token,
            'login': username,
            'password': passwd }
        self.session.post(loginurl, data=payload)
        if not self.session.cookies.get('PHPSESSID'):
            raise LoginError()

    def get_submissions(self):
        submurl = 'https://leetcode.com/submissions/'
        strainer = SoupStrainer('tbody')
        tosaveDict = defaultdict(dict)
        for i in itertools.count(1):
            url = urljoin(submurl, str(i))
            soup = self.get_soup(url, strainer)
            rowlist = soup.find_all('tr')
            if rowlist == []: break
            for row in rowlist:
                _1, title, status, _2, lang = list(row.stripped_strings)
                if status == 'Accepted':
                    title = title.replace(' ','_')
                    if not tosaveDict[title].get(lang):
                        tosaveDict[title][lang] = urljoin(self.BASEURL, row.find_all('a')[1]['href'])
        return tosaveDict

    def get_table(self, url):
        soup = self.get_soup(url)
        if soup.find(text=re.compile('available')):
            raise PageError('No Such Page', url)

        if '/tag/' in url:
            pat = re.compile('"id".+?"(\d+)".+?"title".+?"(.+?)".+?"ac_rate".+?"(.+?)".+?"difficulty".+?"(.+?)"',
                            re.S | re.X | re.U)
            raw_script = soup.body.find_all('script')[3].text
            table = []
            for data in pat.findall(raw_script):
                num, title, ac_rate, diff = data
                title, diff = BeautifulSoup(title), BeautifulSoup(diff)
                table.append((num, title.text, ac_rate, diff.text, title.a['href']))
        else:
            t = soup.find(id='problemList').find_all('tr')[1:]
            table = [ tuple(i.stripped_strings) + (i.a['href'],) for i in t ]

        return table

    def get_problems_list(self, url):
        try:
            content = self.get_table(url)
        except:
            raise

        if self.DEBUG:
            print("Grasped content:")
            print(content)

        for info in content:
            yield {
                    'number':info[0],
                    'title':info[1].replace(' ','_'),
                    'acceptance':info[2],
                    'difficulty':info[3].lower(),
                    'url':urljoin(self.BASEURL, info[4])
                  }

