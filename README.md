README
======

Description:
------------
Save filtered problems on leetcode.com

Note: saved problems will be ignored

PS: At present, the script can only save the *description* of problems.  Although I want to save the code with specified language at the same time, I don't know how to get it since the code seems to be generated dynamically. If you know, please tell me! Any help would be appreciated.

Dependecies:
------------
* python >= 3.2
* python3-beautifulsoup4 4.3.2
* python3-requests 2.7.0

Options:
------
```
usage: grasp.py [-h] [-n NUMBER] [-c CATEGORY] [-d DIFFICULTY] [-t TAG]
                [--show_tags] [-v]

optional arguments:
  -h, --help            Show this help message and exit
  -n NUMBER, --number NUMBER
                        Specify the question number
  -c CATEGORY, --category CATEGORY
                        Specify the category: algorithms, database, shell, all
  -d DIFFICULTY, --difficulty DIFFICULTY
                        Specify the difficulty: easy, medium, hard
                        If not specified, all problems will be grasped
  -t TAG, --tag TAG     Specify the tag
  --show_tags           Display problems with specified tags
  -v, --verbose         verbose output
```

Example:
--------
* save all the problems in `shell` category:
```
    $ grasp.py -c shell
```
* save the problems whose numbers are in {1,2,3,4,5,12,16} in `algorithms` category:
```
    $ grasp.py -c algorithms -n 1-5,12,16
```
* save the easy and hard problems in `database` category:
```
    $ grasp.py -c database -d easy,hard
```
* save the hard problems with tag `dynamic-programming`:
```
    $ grasp.py -t dynamic-programming -d hard
```
* save all problems:
```
    $ grasp.py -t all
    $ grasp.py -c all
```
* display available tags:
```
    $ grasp.py --show_tags
```
* show problems with specified tags:
```
    $ grasp.py --show_tags -t trie,math
```
