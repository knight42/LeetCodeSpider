README
======

Features:
------------
1. Save filtered problems on leetcode.com
2. Save all your latest accepted submissions

Note:
-----
* to save your submissions, please make sure the fields in `config.ini` have been filled in correctly.
* saved problems with specified language will be ignored
* when saving problems, cannot specify category and tag at the same time
* multiple tags/categories/difficulties/numbers are now separated by **space** not **comma**

Dependecies:
------------
* python >= 3.4
* python3-beautifulsoup4 4.3.2
* python3-requests 2.7.0

Commands:
------
```
usage: grasp.py [-h] {show_tags,show_cate,save,save_sub} ...

positional arguments:
  {show_tags,show_cate,save,save_sub}
                        Available commands
    show_tags           Display available tags or problems with specified tags
    show_cate           Display available categories or problems in specified
                        categories
    save                Save filtered problems in cur dir.
    save_sub            Save last accepted submissions.

optional arguments:
  -h, --help            show this help message and exit
```

#### For each sub-command's options, please run "grasp.py command -h/--help"


Example:
--------
* save all your latest accepted submissions
```
$ grasp.py save_sub
```
* save all your latest accepted submissions with specified language
```
$ grasp.py save_sub -l python
```
* save the problems whose numbers are in {1,2,3,4,5,12,16} in `algorithms` category and C & Python's default code:
```
$ grasp.py save -c algorithms -n 1-5 12 16 -l c python
```
* save the easy and hard problems in `database` category and only their description
```
$ grasp.py save -c database -d easy hard
```
* save the hard problems with tag `dynamic-programming` and C#'s default code':
```
$ grasp.py save -t dynamic-programming -d hard -l c#
```
* save all problems and all default code:
```
$ grasp.py save -t all -l all
$ grasp.py save -c all -l all
```
* display available tags:
```
$ grasp.py show_tags
```
* display available categories:
```
$ grasp.py show_cate
```
* show problems with specified tags:
```
$ grasp.py show_tags -t trie math 
```
* show easy problems in `algorithm` category:
```
$ grasp.py show_cate -c algorithms -d easy
```
