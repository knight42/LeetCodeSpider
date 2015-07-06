#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

import os
import json
from bs4 import SoupStrainer, re
from concurrent.futures import ThreadPoolExecutor

class Writer:
    def __init__(self, debug=False):
        self.DEBUG = debug
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

    def print_to_file(self, text, path):
        with open(path, 'w') as f:
            print(text.replace('\r\n', os.linesep), file=f)
            if self.DEBUG:
                print('{} saved.'.format(path))

    def save_submissions(self, spider, info, workers=15):

        def set_save_path(title, lang):
            if lang == 'bash':
                pdir = os.path.join(self.BASEDIR, 'shell', title)
            elif lang == 'mysql':
                pdir = os.path.join(self.BASEDIR, 'database', title)
            else:
                pdir = os.path.join(self.BASEDIR, 'algorithms', title)
            os.makedirs(pdir, exist_ok=True)
            return os.path.join(pdir, self.SAVENAME[lang])

        def f(item):
            title, url, lang = item
            page = spider.session.get(url)
            pat = re.compile("scope.code.{} = '(.+)'".format(lang))
            code = pat.findall(page.text)[0]
            jsoncode = json.loads('{"code": "%s"}' %code)
            codepath = set_save_path(title, lang)
            self.print_to_file(jsoncode['code'], codepath)

        with ThreadPoolExecutor(max_workers=workers) as e:
            e.map(f, info)
            e.shutdown(wait=True)
            print('All done!')

    def save_problems(self, spider, plist, subdir, langlist, workers=15):

        def save_defaultcode(soup, pdir, langlist):
            tag = soup.find(lambda x: x.has_attr('ng-init'))
            rawjson = tag['ng-init']
            pat = re.compile('(\[.+\])')
            raw = pat.findall(rawjson)[0].replace("'", '"')  # ' -> "
            raw = ''.join(raw.rsplit(',', 1)) # remove the last ',' in json list
            codelist = json.loads(raw)
            codelist = filter(lambda x: x['value'] in langlist, codelist)

            d = { i['value']:i['defaultCode'] for i in codelist }

            for lang in d.keys():
                codepath = os.path.join(pdir, self.SAVENAME[lang])
                if not os.path.isfile(codepath):
                    self.print_to_file(d[lang], codepath)
                elif self.DEBUG:
                    print('{} already exists!'.format(codepath))

        def save_description(soup, pdir):
            descpath = os.path.join(pdir, 'description.txt')
            if not os.path.isfile(descpath):
                desc = soup.find(class_='question-content').text
                self.print_to_file(desc, descpath)
            elif self.DEBUG:
                print('{} already exists!'.format(descpath))

        def f(info):
            soup = spider.get_soup(info['url'], SoupStrainer(class_='col-md-12'))
            pdir = os.path.join(self.BASEDIR, subdir, info['title'])
            os.makedirs(pdir, exist_ok=True)
            save_description(soup, pdir)
            save_defaultcode(soup, pdir, langlist)

        with ThreadPoolExecutor(max_workers=workers) as e:
            e.map(f, plist)
            e.shutdown(wait=True)
        print('All done!')

if __name__ == '__main__':
    pass
