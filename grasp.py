#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
import os
import sys
import json
import argparse
import crawler
from urllib.parse import urljoin

# This piece of code mainly comes from @vamin in StackOverFlow
# See http://stackoverflow.com/a/25334100/4725840
class CustomFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                return ', '.join(action.option_strings)
            # if the Optional takes a value, format is:
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                option_string = ', '.join(action.option_strings)
            return '{} {}'.format(option_string, args_string)

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

def print_problems(items, urllist):
    # memo:
    # $c(crawler instance) and $filter_list are global

    for t, u in zip(items, urllist):
        print('The problems under <{}> are:'.format(t))
        plist = get_filtered_problems(c.get_problems_list(u), filter_list)
        for p in plist:
            print('\t'.join((p['number'], p['title'],
                            p['acceptance'], p['difficulty'])))
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-n', '--number', 
                        nargs='*',
                        help="Specify the question number")
    parent_parser.add_argument('-d', '--difficulty',
                        nargs='*',
                        choices=['easy', 'medium', 'hard'],
                        help="Specify the difficulty.")
    parent_parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="Verbose output"
                        "If not specified, all problems will be grasped")

    subparsers = parser.add_subparsers(help='commands')

    sav_parser = subparsers.add_parser('save',
                            parents=[parent_parser],
                            formatter_class=CustomFormatter,
                            help='Save filtered problems in cur dir.')
    tag_parser = subparsers.add_parser('show_tags', 
                            parents=[parent_parser],
                            formatter_class=CustomFormatter,
                            help='Display available tags or problems with specified tags')
    cat_parser = subparsers.add_parser('show_categories',
                            parents=[parent_parser],
                            formatter_class=CustomFormatter,
                            help='Display available categories or problems in specified categories')

    cat_parser.add_argument('-c', '--category', 
                        nargs='*',
                        choices=['algorithms', 'database', 'shell', 'all'],
                        help="Specify the category")
    tag_parser.add_argument('-t', '--tag',
                        nargs='*',
                        help="Specify the tag")
    sav_parser.add_argument('-l','--language',
                        nargs='+',
                        required=True,
                        choices=['all','cpp','java','python','c','c#','js','ruby'],
                        help="Specify the language")

    sav_group = sav_parser.add_mutually_exclusive_group(required=True)
    sav_group.add_argument('-c', '--category', 
                        nargs='*',
                        choices=['algorithms', 'database', 'shell', 'all'],
                        help="Specify the category")
    sav_group.add_argument('-t', '--tag',
                        nargs='*',
                        help="Specify the tag")

    args = parser.parse_args()

    if args.category and args.tag:
        print('You cannot specify <category> and <tag> at the same time.')
        sys.exit(1)

    filter_list = []

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
    
    ALL_CATEGORIES = ['algorithms', 'database', 'shell']

    if args.category:
        if args.category == 'all': 
            specified_categories = ALL_CATEGORIES
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
            specified_tags = list(c.TAGS.keys())
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
            print('\n'.join(c.TAGS.keys()))
        else:
            print_problems(specified_tags, urllist)
        sys.exit(0)
    elif args.show_categories:
        if not specified_categories:
            print('Available categories are:')
            print('\n'.join(ALL_CATEGORIES))
        else:
            print_problems(specified_categories, urllist)
        sys.exit(0)

    if not specified_tags and not specified_categories:
        print('Please at least specify a category or tag.')
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
