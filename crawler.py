#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup as bs
import concurrent.futures as cf

class PageError(Exception):
    def __init__(self, text, url):
        self.msg = text
        self.url = url
    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)

class Crawler:
    def __init__(self):
        self.BASEURL = 'https://leetcode.com/problemset/'
        self.BASEDIR = os.path.dirname(__file__)
        self.TABLE = dict()
        self.TAGS = dict()
        html = requests.get(self.BASEURL, timeout=10)
        soup = bs(html.content)
        content = soup.select('a[class=list-group-item]')
        #self.TOP10 = []
        #for item in content[:10]:
        #    self.TOP10.append((''.join(item.stripped_strings),
        #                        urljoin(self.BASEURL, item['href'])))
        for item in content[10:]:
            # data: count title url
            data = list(item.stripped_strings)
            data[1] = data[1].replace(' ','-')
            data[1] = data[1].lower()
            data.append(urljoin(self.BASEURL, item['href']))
            self.TAGS[data[1]] = (data[0], data[2])

    def get_table(self, url):
        pat = re.compile('/([\w-]+)/?$')
        key = pat.findall(url)[0]
        if key in self.TABLE.keys():
            return self.TABLE[key]

        html = requests.get(url, timeout=10)
        soup = bs(html.content)
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

        return self.TABLE.setdefault(key, table)

    def get_problems_list(self, url):
        try:
            content = self.get_table(url)
        except:
            raise

        for info in content:
            d = {
                'number':info[0],
                'title':info[1].replace(' ','_'),
                'acceptance':info[2],
                'difficulty':info[3].lower(),
                'url':urljoin(self.BASEURL, info[4])
            }
            yield d

    def _write_file(self, info, pdir, lang='c'):
        html = requests.get(info['url'])
        soup = bs(html.content)
        desc = soup.find(class_='question-content')
        tag = soup.find(lambda x: x.has_attr('ng-init'))
        rawjson = tag['ng-init']
        pat = re.compile('(\[.+\])')
        raw = pat.search(rawjson).group()
        raw = raw.replace("'", '"') # ' -> "
        raw = ''.join(raw.rsplit(',', 1)) # remove the last ',' in json list
        codelist = json.loads(raw)

        if lang == 'c':
            f = lambda x: x['value'] == 'c'
        elif lang == 'cpp':
            f = lambda x: x['value'] == 'cpp'
        elif lang == 'c#':
            f = lambda x: x['value'] == 'csharp'
        elif lang == 'java':
            f = lambda x: x['value'] == 'java'
        elif lang == 'python':
            f = lambda x: x['value'] == 'python'
        elif lang == 'js':
            f = lambda x: x['value'] == 'javascript'
        elif lang == 'ruby':
            f = lambda x: x['value'] == 'ruby'
        code = list(filter(f, codelist))[0]['defaultCode']

        pdir = os.path.join(pdir, '-'.join([info['number'], info['title']]))
        os.makedirs(pdir)
        with open(os.path.join(pdir, 'description.txt'), 'w') as f:
            print(desc.text, file=f)

    def save_problems(self, plist, pdir, workers=10):
        if len(plist) == 0: return
        with cf.ThreadPoolExecutor(max_workers=workers) as e:
            e.map(lambda x: self._write_file(x, os.path.join(self.BASEDIR, pdir)), plist)
            e.shutdown(wait=True)

