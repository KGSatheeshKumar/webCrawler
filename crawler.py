import sys

sys.dont_write_bytecode = True

import requests
from bs4 import BeautifulSoup
import os
import time
import argparse
import random

from headers.agents import Headers
from banner.banner import Banner



class Colors:
    # Console colors
    W = '\033[0m'  # white (normal)
    R = '\033[31m'  # red
    G = '\033[32m'  # green
    O = '\033[33m'  # orange
    B = '\033[34m'  # blue
    P = '\033[35m'  # purple
    C = '\033[36m'  # cyan
    GR = '\033[37m'  # gray
    BOLD = '\033[1m'
    END = '\033[0m'


class Configuration:
    Crawler_ERROR_CODE_STANDARD = -1
    Crawler_SUCCESS_CODE_STANDARD = 0

    Crawler_MIN_DATA_RETRIEVE_LENGTH = 1
    Crawler_RUNNING = False
    Crawler_OS_UNIX_LINUX = False
    Crawler_OS_WIN32_64 = False
    Crawler_OS_DARWIN = False

    Crawler_REQUESTS_SUCCESS_CODE = 200
    Crawler_PROXY = False

    descriptions = []
    urls = []

    __Crawler_api__ = "https://ahmia.fi/search/?q="
    __proxy_api__ = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"


class Platform(object):
    def __init__(self, execpltf):
        self.execpltf = execpltf

    def get_operating_system_descriptor(self):
        cfg = Configuration()
        clr = Colors()

        if self.execpltf:
            if sys.platform == "linux" or sys.platform == "linux2":
                cfg.Crawler_OS_UNIX_LINUX = True
                print(clr.BOLD + clr.W + "Operating System: " + clr.G + sys.platform + clr.END)
            if sys.platform == "win64" or sys.platform == "win32":
                cfg.Crawler_OS_WIN32_64 = True
                print(clr.BOLD + clr.W + "Operating System: " + clr.G + sys.platform + clr.END)
            if sys.platform == "darwin":
                cfg.Crawler_OS_DARWIN = True
                print(clr.BOLD + clr.W + "Operating System: " + clr.G + sys.platform + clr.END)
        else:
            pass

    def clean_screen(self):
        cfg = Configuration()
        if self.execpltf:
            if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
                os.system('clear')
            else:
                os.system('cls')
        else:
            pass


class Proxies(object):
    def __init__(self):
        self.proxy = {}

    def assign_proxy(self):
        req = requests.get(Configuration.__proxy_api__)
        if req.status_code == Configuration.Crawler_REQUESTS_SUCCESS_CODE:
            for line in req.text.splitlines():
                if line:
                    proxy = line.split(':')
                    self.proxy["http"] = "http://" + proxy[0] + ':' + proxy[1]
        else:
            pass

    def get_proxy(self):
        return self.proxy["http"]

    def get_proxy_dict(self):
        return self.proxy


class Crawler(object):
    def crawl(self, query, amount):
        clr = Colors()
        prox = Proxies()

        headers = random.choice(Headers().useragent)
        if Configuration.Crawler_PROXY == True:
            prox.assign_proxy()
            proxy = prox.get_proxy()
            print(clr.BOLD + clr.P + "~:~ Using Proxy: " + clr.C + proxy + clr.END + '\n')
            page = requests.get(Configuration.__Crawler_api__ + query, proxies=prox.get_proxy_dict())
        else:
            page = requests.get(Configuration.__Crawler_api__ + query)
        page.headers = headers

        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find(id='ahmiaResultsPage')
        second_results = results.find_all('li', class_='result')
        res_length = len(second_results)

        for iterator in range(res_length):
            Configuration.descriptions.append(second_results[iterator].find('p').text)
            Configuration.urls.append(second_results[iterator].find('cite').text)
        # Remove duplicates
        Configuration.descriptions = list(dict.fromkeys(Configuration.descriptions))
        Configuration.urls = list(dict.fromkeys(Configuration.urls))
        try:
            if len(Configuration.descriptions) >= Configuration.Crawler_MIN_DATA_RETRIEVE_LENGTH:
                for iterator in range(amount):
                    site_url = Configuration.urls[iterator]
                    site_description = Configuration.descriptions[iterator]
                    print(clr.BOLD + clr.G + f"[+] Website: {site_description}\n\t> Onion Link: {clr.R}{site_url}\n" +
                          clr.END)
            else:
                print(clr.BOLD + clr.R + "[!] No results found." + clr.END)
        except IndexError as ie:
            print(clr.BOLD + clr.O + f"[~] No more results to be shown ({ie}): " + clr.END)


def Crawler_main():
    clr = Colors()
    cfg = Configuration()
    bn = Banner()
    prox = Proxies()

    Platform(True).clean_screen()
    Platform(True).get_operating_system_descriptor()
    Proxies().assign_proxy()
    bn.LoadCrawlerBanner()
    time.sleep(1.3)
    parser = argparse.ArgumentParser(
        description="This is a Web Crawler used for exploring the Deep Web.")
    parser.add_argument("-q",
                        "--query",
                        help="the keyword or string you want to search on the deepweb",
                        type=str,
                        required=False)
    parser.add_argument("-a",
                        "--amount",
                        help="the amount of results you want to retrieve (default: 10)",
                        type=int)

    parser.add_argument("-p",
                        "--proxy",
                        help="use Crawler proxy to increase anonymity",
                        action="store_true")

    args = parser.parse_args()

    
    if args.proxy:
        Configuration.Crawler_PROXY = True

    if args.query and args.amount:
        print(clr.BOLD + clr.B + f"Searching For: {args.query} and showing {args.amount} results...\n" + clr.END)
        Crawler().crawl(args.query, args.amount)

    elif args.query:
        print(clr.BOLD + clr.B + f"Searching For: {args.query} and showing 10 results...\n" + clr.END)
        Crawler().crawl(args.query, 10)

    else:
        print(
            clr.BOLD + clr.O + "[~] Note: No query arguments were passed. Please supply a query to search. " + clr.END)


if __name__ == "__main__":
    Crawler_main()
