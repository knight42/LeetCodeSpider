#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import crawler
from urllib.parse import urljoin

####################
# This piece of code mainly comes from @vamin in StackOverFlow
# See http://stackoverflow.com/a/25334100/4725840
# Thank him very much! :D
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
####################

def get_filtered_problems(plist, flist):
    for filt in flist:
        plist = filter(filt, plist)
    return list(plist)

def print_problems(spider, items, urllist, filter_list):
    for item, url in zip(items, urllist):
        print('The problems under <{}> are:'.format(item))
        plist = get_filtered_problems(spider.get_problems_list(url), filter_list)
        maxlen = max(len(pro['title']) for pro in plist)
        head = '{0:<10} {1:<5} {2:<{tlen}} {3:<12} {4:<12}'
        print(head.format('ac_or_not', 'id', 'title', 'acceptance', 'difficulty', tlen=maxlen))
        for pro in plist:
            print(head.format(pro['ac_or_not'], pro['id'], pro['title'],
                              pro['acceptance'], pro['difficulty'], tlen=maxlen))
        print()


if __name__ == '__main__':

    ALL_CATEGORIES = ['algorithms', 'database', 'shell']
    ALL_LANGUAGES = ['cpp', 'java', 'python', 'c', 'csharp', 'javascript', 'ruby', 'bash', 'mysql']

    parser = argparse.ArgumentParser()

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('-n', '--number',
                             nargs='+',
                             help="Specify the question number")
    base_parser.add_argument('-d', '--difficulty',
                             nargs='+',
                             choices=['easy', 'medium', 'hard'],
                             help="Specify the difficulty.\n"
                             "If not specified, all problems will be grasped.")
    base_parser.add_argument('-v', '--verbose',
                             action="store_true",
                             default=False,
                             help="Verbose output")
    base_parser.add_argument('--login',
                            action="store_true",
                            default=False,
                            help="Pretend you have login and disp more information")

    subparsers = parser.add_subparsers(help='Available commands', dest='command')


    tag_parser = subparsers.add_parser('show_tags',
                                       parents=[base_parser],
                                       formatter_class=CustomFormatter,
                                       help='Display available tags or problems with specified tags')
    tag_parser.add_argument('-t', '--tag',
                            nargs='+',
                            help="Specify the tag")


    cat_parser = subparsers.add_parser('show_cate',
                                       parents=[base_parser],
                                       formatter_class=CustomFormatter,
                                       help='Display available categories or problems in specified categories')
    cat_parser.add_argument('-c', '--category',
                            nargs='+',
                            choices=ALL_CATEGORIES + ['all'],
                            help="Specify the category")


    sav_parser = subparsers.add_parser('save',
                                       parents=[base_parser],
                                       formatter_class=CustomFormatter,
                                       help='Save filtered problems in cur dir.')
    sav_parser.add_argument('-l', '--language',
                            nargs='+',
                            default=[],
                            choices=['all', 'cpp', 'java', 'python', 'c', 'c#', 'js', 'ruby', 'bash', 'mysql'],
                            help="Specify the language.\n"
                                 "If not specified, only the description will be saved.")
    sav_group = sav_parser.add_mutually_exclusive_group(required=True)
    sav_group.add_argument('-c', '--category',
                           nargs='+',
                           choices=ALL_CATEGORIES + ['all'],
                           help="Specify the category")
    sav_group.add_argument('-t', '--tag',
                           nargs='+',
                           help="Specify the tag")


    sav_sub_parser = subparsers.add_parser('save_sub',
                                           formatter_class=CustomFormatter,
                                           help='Save last accepted submissions.')
    sav_sub_parser.add_argument('-l', '--language',
                                nargs='+',
                                default=[],
                                choices=['all', 'cpp', 'java', 'python', 'c', 'c#', 'js', 'ruby', 'bash', 'mysql'],
                                help="Specify the language.\n"
                                "If not specified, all your latest accepted submissions will be grasped.")
    sav_sub_parser.add_argument('-v', '--verbose',
                                action="store_true",
                                default=False,
                                help="Verbose output")

    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        parser.print_help()
        sys.exit(1)

    filter_list = []

    argsDict = vars(args)

    if argsDict.get('number'):
        specified_numbers = set()
        for n in args.number:
            if n.isdigit():
                specified_numbers.add(n)
            elif '-' in n:
                b, e = n.split('-')
                specified_numbers.update({str(i) for i in range(int(b), int(e)+1)})
        filter_list.append(lambda x: x['number'] in specified_numbers)

        if args.verbose:
            print('Specified numbers are: {}'.format(specified_numbers))

    if argsDict.get('difficulty'):
        filter_list.append(lambda x: x['difficulty'] in args.difficulty)

        if args.verbose:
            print('Specified difficulty is: {}'.format(args.difficulty))

    if argsDict.get('language'):
        specified_langs = []
        for l in set(args.language):
            if l == 'all':
                specified_langs = ALL_LANGUAGES
                break
            elif l == 'c#':
                specified_langs.append('csharp')
            elif l == 'js':
                specified_langs.append('javascript')
            else:
                specified_langs.append(l)
        args.language = specified_langs
        if args.verbose:
            print('Specified languages are: {}'.format(', '.join(specified_langs)))

    c = crawler.Crawler(debug=args.verbose)
    w = crawler.Writer(args.verbose)
    
    if argsDict.get('login'): c.login()

    if argsDict.get('category'):
        if 'all' in args.category:
            args.category = ALL_CATEGORIES
        L = args.category
        urllist = [urljoin(c.BASEURL, i) for i in L]

        if args.verbose:
            print('Specified categories are: {}'.format(args.category))

    elif argsDict.get('tag'):
        w.BASEDIR = os.path.join(w.BASEDIR, 'Tag')
        alltags = c.get_tags()
        if 'all' in args.tag:
            args.tag = list(alltags.keys())
        L = args.tag
        urllist = [alltags[i][1] for i in L]

        if args.verbose:
            print('Specified tags are: {}'.format(args.tag))

    if args.command == 'show_tags':
        if not args.tag:
            print('Available tags are:')
            print(os.linesep.join(sorted(c.get_tags().keys())))
        else:
            print_problems(c, args.tag, urllist, filter_list)

    elif args.command == 'show_cate':
        if not args.category:
            print('Available categories are: {}'.format(', '.join(ALL_CATEGORIES)))
        else:
            print_problems(c, args.category, urllist, filter_list)

    elif args.command == 'save':
        for i, u in zip(L, urllist):
            try:
                plist = get_filtered_problems(c.get_problems_list(u), filter_list)
            except:
                print(sys.exc_info[2].tb_lineno, sys.exc_info()[1])
                continue

            if args.verbose:
                print('-----------8<---Problems List Begin---8<------------')
                print(plist)
                print('-----------8<---Problems List End-----8<------------')

            w.save_problems(c, plist, i, args.language)

    elif args.command == 'save_submissions':
        c.login()
        print('The process may take a while, depending on how much submissions you have')
        print('Why not take a rest and have a cup of coffee :)')
        if not args.language:
            specified_langs = ALL_LANGUAGES

        def sub_exec(info):
            if args.verbose:
                print('Submissions on this page:')
                print(info)
            w.save_submissions(c, info)

        with crawler.ThreadPoolExecutor(max_workers=5) as pool:
            pool.map(sub_exec, c.get_submissions(specified_langs))
            pool.shutdown(wait=True)
        print('All done!')

