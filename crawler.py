#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
import os
import json
import requests
import itertools
import configparser
from urllib.parse import urljoin
from collections import defaultdict
from bs4 import BeautifulSoup, SoupStrainer, re
from concurrent.futures import ThreadPoolExecutor


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
        return 'Fail to login! Please check your username or password in `config.ini` .'


class Crawler:
    def __init__(self, debug=False):
        self.BASEURL = 'https://leetcode.com/problemset/'
        self.DEBUG = debug
        self.BASEDIR = os.path.dirname(__file__)
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    def daemon(self):
        pass

    def get_soup(self, url, strainer=None):
        html = self.session.get(url, timeout=10)
        soup = BeautifulSoup(html.content, parse_only=strainer)
        return soup

    def get_tags(self):
        soup = self.get_soup(self.BASEURL, SoupStrainer(class_='list-group-item'))
        content = soup.find_all('a', onclick=None)
        tagdict = {}
        for item in content:
            if '/tag/' not in item['href']:
                continue
            count, title = list(item.stripped_strings)
            title = title.replace(' ', '-').lower()
            tagdict[title] = (count, urljoin(self.BASEURL, item['href']))
        return tagdict

    def login(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(self.BASEDIR, 'config.ini'))
        username = config['USER']['username']
        password = config['USER']['password']
        loginurl = 'https://leetcode.com/accounts/login/'
        self.session.headers['Referer'] = loginurl
        self.session.get(loginurl)
        token = self.session.cookies['csrftoken']
        payload = {
                   'csrfmiddlewaretoken': token,
                   'login': username,
                   'password': password
                  }
        self.session.post(loginurl, data=payload)
        if not self.session.cookies.get('PHPSESSID'):
            raise LoginError()

    def get_submissions(self, specified_langs):
        submurl = 'https://leetcode.com/submissions/'
        strainer = SoupStrainer('tbody')
        memory = defaultdict(dict)
        for i in itertools.count(1):
            url = urljoin(submurl, str(i))
            soup = self.get_soup(url, strainer)
            rowlist = soup.find_all('tr')
            if rowlist == []:
                break
            eachpage = defaultdict(dict)
            for row in rowlist:
                _, title, status, _, lang = list(row.stripped_strings)
                if status == 'Accepted':
                    title = title.replace(' ', '_')
                    if not memory[title].get(lang):
                        memory[title][lang] = urljoin(self.BASEURL, row.find_all('a')[1]['href'])
                        eachpage[title][lang] = memory[title][lang]
            info = []
            for title in eachpage.keys():
                for lang in eachpage[title].keys():
                    if lang in specified_langs:
                        info.append((title, eachpage[title][lang], lang))
            yield info

    def get_table(self, url):
        soup = self.get_soup(url)
        if soup.find(text=re.compile('available')):
            raise PageError('No Such Page', url)

        if '/tag/' in url:
            pat = re.compile('data: (\[.*\])', re.S | re.U)
            raw_script = soup.body.find_all('script')[3].text
            rawjson = pat.findall(raw_script)[0]
            rawjson = re.sub(',\s*}', '}', rawjson)
            rawjson = re.sub('"\s*\+\s*"', '', rawjson)
            rawjson = ''.join(rawjson.rsplit(',', 1))
            allproblems = json.loads(rawjson)
            table = list()
            for p in allproblems:
                title, diff, ac_or_not = p['title'], p['difficulty'], p['ac_or_not']
                title, diff, ac_or_not = (BeautifulSoup(title).body.a,
                                          BeautifulSoup(diff).text,
                                          BeautifulSoup(ac_or_not).span['class'][0])
                ac_rate, idnum = p['ac_rate'], p['id']
                table.append((idnum, title.text, ac_rate, diff, title['href'], ac_or_not))
        else:
            tmp = soup.find(id='problemList').find_all('tr')[1:]
            table = [tuple(i.stripped_strings) + (i.a['href'], i.td.span['class'][0]) for i in tmp]

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
            yield {'id': info[0],
                   'title': info[1].replace(' ', '_'),
                   'acceptance': info[2],
                   'difficulty': info[3].lower(),
                   'url': urljoin(self.BASEURL, info[4]),
                   'ac_or_not': info[5]
                  }


class Writer:
    def __init__(self, debug=False):
        self.DEBUG = debug
        self.BASEDIR = os.path.dirname(__file__)
        self.SAVENAME = {'c': 'solution.c',
                         'cpp': 'solution.cpp',
                         'ruby': 'solution.rb',
                         'javascript': 'solution.js',
                         'csharp': 'solution.cs',
                         'python': 'solution.py',
                         'bash': 'solution.sh',
                         'mysql': 'solution.sql',
                         'java': 'solution.java'}

    def print_to_file(self, text, path):
        with open(path, 'w') as fout:
            print(text.replace('\r\n', os.linesep), file=fout)
            if self.DEBUG:
                print('{} saved.'.format(path))

    def save_submissions(self, spider, info):

        def set_save_path(title, lang):
            if lang == 'bash':
                pdir = os.path.join(self.BASEDIR, 'shell', title)
            elif lang == 'mysql':
                pdir = os.path.join(self.BASEDIR, 'database', title)
            else:
                pdir = os.path.join(self.BASEDIR, 'algorithms', title)
            os.makedirs(pdir, exist_ok=True)
            return os.path.join(pdir, self.SAVENAME[lang])

        def executor(item):
            title, url, lang = item
            page = spider.session.get(url)
            pat = re.compile("vm.code.{} = '(.+)'".format(lang))
            code = pat.findall(page.text)[0]
            jsoncode = json.loads('{"code": "%s"}' % code)
            codepath = set_save_path(title, lang)
            self.print_to_file(jsoncode['code'], codepath)

        with ThreadPoolExecutor(max_workers=15) as pool:
            pool.map(executor, info)
            pool.shutdown(wait=True)

    def save_problems(self, spider, plist, subdir, langlist):

        def save_defaultcode(soup, pdir, langlist):
            tag = soup.find(lambda x: x.has_attr('ng-init'))
            rawjson = tag['ng-init']
            pat = re.compile(r'(\[.+\])')
            raw = pat.findall(rawjson)[0].replace("'", '"')  # ' -> "
            raw = ''.join(raw.rsplit(',', 1))  # remove the last ',' in json list
            codelist = json.loads(raw)
            codelist = filter(lambda x: x['value'] in langlist, codelist)

            codedict = {i['value']: i['defaultCode'] for i in codelist}

            for lang in codedict.keys():
                codepath = os.path.join(pdir, self.SAVENAME[lang])
                if not os.path.isfile(codepath):
                    self.print_to_file(codedict[lang], codepath)
                elif self.DEBUG:
                    print('{} already exists!'.format(codepath))

        def save_description(soup, pdir):
            descpath = os.path.join(pdir, 'description.txt')
            if not os.path.isfile(descpath):
                desc = soup.find(class_='question-content').text
                self.print_to_file(desc, descpath)
            elif self.DEBUG:
                print('{} already exists!'.format(descpath))

        def executor(info):
            soup = spider.get_soup(info['url'], SoupStrainer(class_='col-md-12'))
            pdir = os.path.join(self.BASEDIR, subdir, info['title'])
            os.makedirs(pdir, exist_ok=True)
            save_description(soup, pdir)
            save_defaultcode(soup, pdir, langlist)

        with ThreadPoolExecutor(max_workers=15) as pool:
            pool.map(executor, plist)
            pool.shutdown(wait=True)
        print('All done!')
