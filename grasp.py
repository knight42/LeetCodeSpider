#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import crawler
from urllib.parse import urljoin

def get_saved_problems(path):
    try:
        saved = [ i.split('-')[0] for i in os.listdir(path) ]
    except:
        saved = []
    return saved

def get_filtered_problems(plist, flist):
    for f in flist:
        plist = filter(f, plist)
    return list(plist)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', 
                        help="Specify the question number")
    parser.add_argument('-c', '--category', 
                        help="Specify the category: algorithms, database, shell, all")
    parser.add_argument('-d', '--difficulty',
                        help="Specify the difficulty: easy, medium, hard.\n"
                        "If not specified, all problems will be grasped")
    parser.add_argument('-t', '--tag',
                        help="Specify the tag")
    parser.add_argument('--show_tags',
                        action="store_true",
                        help="Display all the tags")
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="verbose output")
    args = parser.parse_args()

    filter_list = []

    if args.category and args.tag:
        print('You cannot specify <category> and <tag> at the same time.')
        sys.exit(1)

    if args.number:
        nlist = args.number.split(',')
        specified_numbers = set()
        for n in nlist:
            if n.isdigit():
                specified_numbers.add(n)
            elif '-' in n:
                b, e = n.split('-')
                specified_numbers.update({ str(i) for i in range(int(b), int(e)+1) })

        filter_list.append(lambda x: x['number'] in specified_numbers)

        if args.verbose:
            print('Specified numbers are: {}'.format(specified_numbers))

    if args.difficulty:
        specified_difficulty = args.difficulty.split(',')

        filter_list.append(lambda x: x['difficulty'] in specified_difficulty)

        if args.verbose:
            print('Specified difficulty is: {}'.format(specified_difficulty))

    specified_categories, specified_tags = None, None

    if args.category:
        if args.category == 'all': 
            specified_categories = ['algorithms', 'database', 'shell']
        else:
            specified_categories = args.category.split(',')
        if args.verbose:
            print('Specified categories are: {}'.format(specified_categories))

    if args.tag:
        if args.tag != 'all': 
            specified_tags = args.tag.split(',')
        c=crawler.Crawler()
        c.BASEDIR = os.path.join(c.BASEDIR, 'Tag')
        if not specified_tags:
            specified_tags = [ i for i in c.TAGS.keys() ]
        if args.verbose:
            print('Specified tags are: {}'.format(specified_tags))

    if specified_tags:
        L = specified_tags
        urllist = [ c.TAGS[i][1] for i in L ]
    elif specified_categories:
        L = specified_categories
        c=crawler.Crawler()
        urllist = [ urljoin(c.BASEURL, i) for i in L ]

    if args.show_tags:
        if not specified_tags:
            c=crawler.Crawler()
            print('Available tags are:')
            for t in c.TAGS.keys():
                print(t)
        else:
            for t, u in zip(specified_tags, urllist):
                print('The problems under <{}> are:'.format(t))
                plist = get_filtered_problems(c.get_problems_list(u), filter_list)
                for p in plist:
                    print('\t'.join((p['number'], p['title'],
                                    p['acceptance'], p['difficulty'])))
                print()
        sys.exit(0)

    if not specified_tags and not specified_categories:
        print('Please at least specify the category or tag.')
        sys.exit(1)

    for i, u in zip(L, urllist):
        filter_list.append(lambda x: x['number'] not in get_saved_problems(os.path.join(c.BASEDIR, i)))

        try:
            plist = get_filtered_problems(c.get_problems_list(u), filter_list)
        except Exception as e:
            print(e)
            continue

        if args.verbose:
            print('-----------8<---Problems List Begin---8<------------')
            print(plist)
            print('-----------8<---Problems List End---8<------------')

        c.save_problems(plist, i)

        filter_list.pop()
