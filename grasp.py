#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
import os
import re
import sys
import argparse
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
        self.TABLE = dict()
        self.TAGS, self.TOP10 = [], []
        html = requests.get(self.BASEURL)
        soup = bs(html.content)
        content = soup.select('a[class=list-group-item]')
        for item in content[:10]:
            self.TOP10.append((''.join(item.stripped_strings),
                                urljoin(self.BASEURL, item['href'])))
        for item in content[10:]:
            # data: count tag url
            data = list(item.stripped_strings)
            data[1] = data[1].replace(' ','-')
            data[1] = data[1].lower()
            data.append(urljoin(self.BASEURL, item['href']))
            self.TAGS.append(tuple(data))

    def get_table(self, url, tableid):
        pat = re.compile('/(\w+)/?')
        key = pat.findall(url)[0]
        if key in self.TABLE.keys():
            return self.TABLE[key]
        html = requests.get(url)
        soup = bs(html.content)
        if soup.find(text=re.compile('available')):
            raise PageError('No Such Page', url) 
        table = soup.find(id=tableid).find_all('tr')[1:]
        return self.TABLE.setdefault(key, table)

    def get_problems_num(self, url, tableid='problemList'):
        try:
            content = self.get_table(url, tableid)
        except:
            raise

        return len(content)

    def get_problems_list(self, url, tableid='problemList'):
        try:
            content = self.get_table(url, tableid)
        except:
            raise

        for p in content:
            info = tuple(p.stripped_strings)
            d = {
                'number':info[0],
                'title':info[1].replace(' ','_'),
                'acceptance':info[2],
                'difficulty':info[3],
                'url':urljoin(self.BASEURL, p.find('a')['href'])
            }
            yield d

    def _write_file(self, info, pdir):
        html = requests.get(info['url'])
        soup = bs(html.content)
        content = soup.find(class_='question-content')
        pdir = os.path.join(pdir, '-'.join((info['number'], info['title'])))
        os.makedirs(pdir)
        with open(os.path.join(pdir, 'problem.txt'), 'w') as f:
            print(content.text, file=f)

    def save_problems(self, problemslist, problemsdir):
        with cf.ThreadPoolExecutor(max_workers=10) as e:
            e.map(lambda x: self._write_file(x, problemsdir), problemslist)
            e.shutdown(wait=True)


if __name__ == '__main__':
    BASEDIR = os.path.dirname(__file__)
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', 
                        help="Specify the question No.")
    parser.add_argument('-c', '--category', 
                        help="Specify the category")
    parser.add_argument('-d', '--difficulty',
                        help="Specify the difficulty. If not specified, all problems will be grasped")
    parser.add_argument('-t', '--tag',
                        help="Specify the tag")
    parser.add_argument('--show_tags',
                        action="store_true",
                        help="Display all the tags")
    args = parser.parse_args()
    #if args.category is None:
    #    print('Please specify the category of problems')
    #    sys.exit(1)
    if args.show_tags:
        c=Crawler()
        print(c.TAGS)
        sys.exit(0)
    if not args.category and not args.tag:
        print('Please at least specify the category or tag.')
        sys.exit(1)
    #print(c.TOP10)
    #print(c.TAGS)
