README
======

Description:
------------
Save filtered problems on leetcode.com in current dir.

Note:
-----
* saved problems with specified language will be ignored
* when save problems, cannot specify category and tag at the same time
* multiple tags/categories/difficulties/numbers are now separated by **space** not **comma**

Dependecies:
------------
* python >= 3.4
* python3-beautifulsoup4 4.3.2
* python3-requests 2.7.0


Commands:
------
```
usage: grasp.py [-h] {save,show_tags,show_categories} ...

positional arguments:
  {save,show_tags,show_categories}
                        Available commands
    save                Save filtered problems in cur dir.
    show_tags           Display available tags or problems with specified tags
    show_categories     Display available categories or problems in specified
                        categories

optional arguments:
  -h, --help            show this help message and exit
```

#### For each sub-command's options, please run "grasp.py command -h/--help"


Example:
--------
* save all the problems in `shell` category and Python's default code:
```
$ grasp.py save -c shell -l python
```
* save the problems whose numbers are in {1,2,3,4,5,12,16} in `algorithms` category and C's default code:
```
$ grasp.py save -c algorithms -n 1-5 12 16 -l c
```
* save the easy and hard problems in `database` category and JavaScript's default code:
```
$ grasp.py save -c database -d easy hard -l js
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
$ grasp.py show_categories
```
* show problems with specified tags:
```
$ grasp.py show_tags -t trie math
```
* show easy problems in `algorithm` category:
```
$ grasp.py show_categories -c algorithms -d easy
```
