#!/usr/bin/env python3
"""Simple python3 module to poll shmmy.ntua.gr for exam results"""
import sys
import signal
import time
from html.parser import HTMLParser
import urllib.request
import argparse
# pankgeorg@gmail.com
# results from shmmy.ntua.gr

URL = 'https://shmmy.ntua.gr/forum/viewtopic.php?f=290&t=19705'
POSTS = 1
START = 0
SLEEP_TIME = 5
DEBUG = True and False
RESULTS = 2


class TermCol:
    """color class, copied from stackoverflow.com"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class ShmmyLastN(HTMLParser):
    """Class that reads replies from shmmy.ntua.gr/forum"""
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
                attr_type, attr_val = attrs[0]
            except:
                return
        else:
            return
        if attr_type == "class" and attr_val == "content":
            self.stack.append("THIS")
            self.flag = True

    def handle_endtag(self, tag):
        curr = self.stack.pop()
        if curr == "THIS":
            self.results.append(self.temp)
            self.flag = False
            self.stack.pop()
            self.temp = ""
        return

    def handle_data(self, data):
        if not self.flag:
            return
        self.temp += " " + data.strip()


class ShmmyCountPosts(HTMLParser):
    """Class that reads Counts from shmmy.ntua.gr/forum"""
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.found = False
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            try:
                attr_type, attr_val = attrs[0]
            except:
                return
        else:
            return
        if attr_type == "class" and attr_val == "pagination":
            self.flag = True

    def handle_endtag(self, tag):
        self.flag = False
        return

    def handle_data(self, data):
        if self.found:
            return
        if self.flag and "δημοσιεύσεις" in data:  # or whatever is after num
            try:
                if DEBUG:
                    print(data.strip())
                self.found = True
                self.count = int(data.strip().split()[0])
            except:
                if DEBUG:
                    print("Error reading count")
        else:
            return


def eol_by_79(string):
    """Wraps strings at 79 chars. Good for terminal, bad for anything else"""
    new_str = ""
    old_str = string
    while old_str:
        new_str += old_str[0:79] + '\n'
        old_str = old_str[79:]
    return new_str


def get_count():
    """Read and return how many posts are now in URL"""
    req = urllib.request.urlopen(URL)
    data = str(req.read(), 'utf-8')
    parser = ShmmyCountPosts()
    parser.feed(data)
    return parser.count


def get_result_list(result_count, page=-1):
    """Given the result count, read the last page of results"""
    if page < 0:  # assume that the request is for the last page
        last_page_count = result_count % 20
        suffix = str(result_count - last_page_count)
    else:
        suffix = str(page * 20)
    url2 = (URL + "&start=" + suffix)
    data = str(urllib.request.urlopen(url2).read(), 'utf-8')
    parser = ShmmyLastN()
    parser.feed(data)
    return parser.results


def show_results(result_list, how_many=5):
    """Take a given list and print results"""
    if how_many < 1:
        return
    print(TermCol.FAIL + 79 * "-" + TermCol.ENDC)
    for res in result_list[-how_many:]:
        print(TermCol.HEADER + eol_by_79(res.strip()) + TermCol.ENDC)
        print(TermCol.FAIL + 79 * "-" + TermCol.ENDC)


def main():
    """Basic user interaction"""
    nothing = '\rNothing new [poll # {}]'
    new_res = TermCol.WARNING + '\r{} new results available ' + TermCol.ENDC
    prompt = 'Poll for more results? [Y/n] '
    poll = START
    prev_count = START
    try:
        if RESULTS != 2:
            raise Exception()
        how_many = int(input("How many results to show? "))
    except:
        how_many = RESULTS
    while True:
        count = get_count()
        if count == prev_count:
            print(nothing.format(poll), end="")
            poll += 1
        else:
            print(new_res.format(count-prev_count))
            res_list = get_result_list(count)
            show_results(res_list, how_many)
            if DEBUG:
                print(res_list)
            reply = input(prompt)
            if not reply in "" and reply in "nN":  # Accepts n,N but not \n
                exit(0)
            prev_count = count
        sys.stdout.flush()
        time.sleep(SLEEP_TIME)


def signal_handler(sig, frame):
    """Catch Ctr+C Gracefully """
    print("\rControl C was pressed, exiting..")
    sys.exit(0)


if __name__ == "__main__":
    DESCR = "Simple program that reads results from shmmy.ntua.gr"
    parser = argparse.ArgumentParser(description=DESCR)
    parser.add_argument('--head', type=int)
    parser.add_argument('--url', type=str)
    parser.add_argument('--time', type=int)
    parser.add_argument('--results', type=int)
    args = parser.parse_args()
    if args.head:
        START = args.head
    if args.url:
        URL = args.url
    if args.time:
        SLEEP_TIME = args.time
    if args.results:
        RESULTS = args.results
    signal.signal(signal.SIGINT, signal_handler)
    main()
