#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer
import concurrent.futures as cf

class PageError(Exception):
    def __init__(self, text, url):
        self.msg = text
        self.url = url
    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)

class Crawler:
    def __init__(self, debug=False):
        self.DEBUG = debug
        self.BASEURL = 'https://leetcode.com/problemset/'
        self.BASEDIR = os.path.dirname(__file__)
        self.SAVENAME = {'c':'solution.c',
                         'cpp':'solution.cpp',
                         'ruby':'solution.rb',
                         'javascript':'solution.js',
                         'csharp':'solution.cs',
                         'python':'solution.py',
                         'bash':'solution.sh',
                         'mysql':'solution.sql',
                         'java':'solution.java'}

    def _get_soup(self, url, strainer=None):
        html = requests.get(url, timeout=10)
        soup = bs(html.content, parse_only=strainer)
        return soup

    def get_tags(self):
        onlytags = SoupStrainer(class_='list-group-item')
        soup = self._get_soup(self.BASEURL, onlytags)
        content = soup.find_all('a', onclick=None)
        tagdict = {}
        for item in content:
            # data: count title url
            data = list(item.stripped_strings)
            data[1] = data[1].replace(' ','-')
            data[1] = data[1].lower()
            data.append(urljoin(self.BASEURL, item['href']))
            tagdict[data[1]] = (data[0], data[2])
        return tagdict

    def get_submitted_problems(self, username, passwd):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
            'Referer': 'https://leetcode.com/accounts/login/' })
        loginurl = 'https://leetcode.com/accounts/login/'
        session.get(loginurl)
        token = session.cookies['csrftoken']
        payload = {
            'csrfmiddlewaretoken': token,
            'login': username,
            'password': passwd }
        session.post(loginurl, data=payload)
        pass

    def get_table(self, url):
        soup = self._get_soup(url)
        if soup.find(text=re.compile('available')):
            raise PageError('No Such Page', url)

        if '/tag/' in url:
            pat = re.compile('"id".+?"(\d+)".+?"title".+?"(.+?)".+?"ac_rate".+?"(.+?)".+?"difficulty".+?"(.+?)"',
                            re.S | re.X | re.U)
            raw_script = soup.body.find_all('script')[3].text
            table = []
            for data in pat.findall(raw_script):
                num, title, ac_rate, diff = data
                title, diff = bs(title), bs(diff)
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

    def save_problems(self, plist, pdir, langlist, workers=15):
        if len(plist) == 0: return
        with cf.ThreadPoolExecutor(max_workers=workers) as e:
            e.map(lambda x: self._get_text(x, os.path.join(self.BASEDIR, pdir), langlist), plist)
            e.shutdown(wait=True)
        print('All done!')

    def _get_text(self, info, pdir, langlist):
        pdir = os.path.join(pdir, '-'.join([info['number'], info['title']]))
        os.makedirs(pdir, exist_ok=True)

        soup = self._get_soup(info['url'], strainer)

        descpath = os.path.join(pdir, 'description.txt')
        if not os.path.isfile(descpath):
            desc = soup.find(class_='question-content').text
            self._print_to_file(desc.replace('\r\n', os.linesep), descpath)
        elif self.DEBUG:
            print('{} already exists!'.format(descpath))

        if len(langlist) == 0: return

        tag = soup.find(lambda x: x.has_attr('ng-init'))
        rawjson = tag['ng-init']
        pat = re.compile('(\[.+\])')
        raw = pat.findall(rawjson)[0]
        raw = raw.replace("'", '"')       # ' -> "
        raw = ''.join(raw.rsplit(',', 1)) # remove the last ',' in json list
        codelist = json.loads(raw)
        codelist = filter(lambda x: x['value'] in langlist, codelist)

        d = { i['value']:i['defaultCode'] for i in codelist }

        for lang in d.keys():
            codepath = os.path.join(pdir, self.SAVENAME[lang])
            if not os.path.isfile(codepath):
                self._print_to_file(d[lang].replace('\r\n', os.linesep), codepath)
            elif self.DEBUG:
                print('{} already exists!'.format(descpath))

    def _print_to_file(text, path):
        with open(path, 'w') as f:
            print(text, file=f)
            if self.DEBUG:
                print('{} saved.'.format(path))
