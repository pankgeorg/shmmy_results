#!/usr/bin/env python3
import os.path
import sqlite3
import argparse
import sys
import time
#pankgeorg@gmail.com
#results from shmmy.ntua.gr

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

URL = 'https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=19705'
POSTS = 1
START = -5
SLEEP_TIME = 2
DBFILE = 'conf.db'

def initiallizer():
    if os.path.isfile(DBFILE):
        conn = sqlite3.connect(DBFILE)
        curs = conn.cursor()
        curs.execute('select url, posts, start from config')


from html.parser import HTMLParser
class ShmmyLastN(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.results = []
        self.temp = ""
        self.stack = []

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

        if "div" == tag:
            try:
                x,y = attrs[0]
            except:
                return
        else:
            return

        if x == "class"  and y == "content" :
            self.stack.append("THIS")
            self.flag = True

    def handle_endtag(self, tag):
        x = self.stack.pop()
        if x == "THIS":
            self.results.append(self.temp)
            self.flag = False
            self.stack.pop()
            self.temp = ""
        return

    def handle_data (self, data):
        if not self.flag:
            return
        self.temp += " " + data.strip()

class ShmmyCountPosts(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.found = False
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            try:
                x,y = attrs[0]
            except:
                return
        else:
            return
        if x == "class" and y == "pagination":
            self.flag = True

    def handle_endtag(self, tag):
        self.flag = False
        return

    def handle_data(self, data):

        if self.found :
            return

        if self.flag and "δημοσιεύσεις" in data:
            try:
                print (data.strip())
                self.found = True
                self.count = int(data.strip().split()[0])
            except:
                print ("Error reading count")
                pass
        else:
            return

def mainprog(start=0):
    import datetime
    print("Ώρα: " +  str(datetime.datetime.now()))
    print()
    req = urllib.request.urlopen( URL )
    data = str(req.read(),'utf-8')
    parser = ShmmyCountPosts()
    parser.feed( data )
    count = parser.count

    print(bcolors.OKGREEN + "Έχουν δηλωθεί: ", count, "αποτελέσματα.\n")
    print("Τελευταία 5:\n")
    url2 = ( URL +"&start=" + str(parser.count -parser.count%20))
    data = str(urllib.request.urlopen(url2).read(),"utf-8")

    parser = ShmmyLastN()
    parser.feed ( data )
    for pr in parser.results[-5:]:
        print(bcolors.HEADER +"\t" + pr.strip() + bcolors.ENDC)
        print(bcolors.FAIL + "\t________________\n" + bcolors.ENDC)

    return count

import urllib.request

def main():
    c = 0
    start = START
    while True:
        req = urllib.request.urlopen( URL )
        data = str(req.read(),'utf-8')
        parser = ShmmyCountPosts()
        parser.feed(data)
        count = parser.count

        if count <= start:
            print("\rNothing new (check", c, ")",end ="")
            c +=1
        else:
            print(bcolors.WARNING +  "\rΝέο αποτέλεσμα διαθέσιμο!" + bcolors.ENDC)
            reply = input("Wanna see what it is? [Y/n] (no exits) ")
            if reply in "yesY \n":
                mainprog(START)
            if reply in "exitExitno":
                exit(0)
            start = count

        sys.stdout.flush()
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch new results and poll"+
                                     "for more")
    parser.add_argument('--new', action='store_true',
                        help='Use if you want to reset everything')
    parser.add_argument('--url')
    parser.add_argument('--time', type=float)
    parser.add_argument('--posts')
    parser.add_argument('--start')

    args = parser.parse_args()
    if args.url:
        URL = args.url
    if args.time:
        SLEEP_TIME = args.time
    if args.posts:
        POSTS = args.posts
    if args.start:
        START = args.start
    print(START, POSTS, SLEEP_TIME)

    main()
