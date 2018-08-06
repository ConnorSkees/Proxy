"""
Scrape proxies from https://free-proxy-list.net/ and output them as a list
"""
import argparse
import random
import re
import sys
import threading
import requests

def main():
    """
    function for cli
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("count", default=1, type=int,
                        help=("The number of proxies."))

    parser.add_argument("-ex", "--exclude", nargs="+", default=[], dest="exclude",
                        help=("Types of proxies to exclude. Valid values include"
                              " country codes (US, CA, etc.), country names "
                              "(United States, Canada, etc.), and proxy anonymity"
                              " levels (elite proxy, anonymous, and transparent)"))

    parser.add_argument("-r", "--require", nargs="+", default=[], dest="require",
                        help=("Include only proxies with these attributes. Valid"
                              " values include country codes (US, CA, etc.), "
                              "country names (United States, Canada, etc.), and "
                              "proxy anonymity levels (elite proxy, anonymous, and"
                              " transparent)"))

    parser.add_argument("--validate", action='store_true', default=False,
                        dest="validate", help=("Validate the proxies against a "
                                               "random website to make sure they work."))

    parser.add_argument("--http-only", action='store_true', default=False,
                        dest="http_only", help=("Only get http proxies"))

    parser.add_argument("--https-only", action='store_true', default=False,
                        dest="https_only", help=("Only get https proxies"))

    parser.add_argument("-v", "--verbose", action='store_true', default=False,
                        dest="verbose", help=("Get full data on proxy (country "
                                              "code, country name, and anonymity"
                                              " level)"))

    parser.add_argument("--max", action='store_true', default=False,
                        dest="max", help=("Get the maximum number of proxies possible"))

    args = parser.parse_args()
    sys.stdout.write(str(handle_args(args)))

def handle_args(args):
    """
    valid args are count (int), exclude (list), require (list), validate (bool),
                   http_only (bool), https_only (bool), verbose (bool)
    """
    prox = proxy(number=args.count, exclude=args.exclude, require=args.require,
          validate=args.validate, http_only=args.http_only, https_only=args.https_only,
          verbose=args.verbose, max_=args.max)

    return "\n{}\n".format(len(set(prox)))

VALID_PROXIES = []

def make_request(url):
    """
    Makes request to https://free-proxy-list.net/ and returns the table as a list

    Args:

    Returns:
        raw table of proxies and their attributes

    Called By:
        proxy()
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Encoding': 'gzip',
        'Content-Type': 'text/html; charset=utf-8',
        }

    # to avoid iterating over a string
    if isinstance(url, str):
        url = [url]

    total_data = []
    for u in url:
        response = requests.get(u, headers=headers).text
        data = re.findall(r"<tr><td>[^<]*</td><td>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td class='hx'>[^<]*</td><td class='hm'>[^<]*</td></tr>", response)
        total_data += data

    return total_data

def threader(function, *params):
    """
    Args:
        function: function name
        params: parameters for function
            params[0]: proxy

    Returns:

    Called By:
        proxy()
    """

    params = params[1]

    if not params:
        return []

    threads = []
    for i in params:
        task = threading.Thread(target=function, args=(i,))
        threads.append(task)

    for thread in threads:
        thread.daemon = True
        thread.start()

    for thread in threads:
        thread.join(timeout=1)

    del threads[:]

def proxy(number=1, exclude=[], require=[], validate=True, https_only=False, http_only=False, verbose=False, max_=False):
    """
    Args:
        function: function name
        params: parameters for function
        params[0]: proxy

    Returns:

    Called By:
        nothing
    """

    if not isinstance(require, (list, set, tuple)):
        require = [require]
    if not isinstance(exclude, (list, set, tuple)):
        exclude = [exclude]

    if number < 0:
        number = 1
    elif number > 300:
        max_ = True

    require = set([i.lower() for i in require])

    # make sure you aren't excluding things you want to include
    exclude = set([e.lower() for e in exclude])


    if not max:
        if not any((exclude, require, https_only, http_only)):
            raw_list = make_request('https://free-proxy-list.net/')[:number]
        else:
            raw_list = make_request('https://free-proxy-list.net/')
    else:
        if not any((exclude, require, https_only, http_only)):
            raw_list = make_request(['https://free-proxy-list.net/',
                                     'https://free-proxy-list.net/uk-proxy.html',
                                     'https://free-proxy-list.net/anonymous-proxy.html',
                                     'https://www.us-proxy.org/',
                                     'https://www.socks-proxy.net/',
                                     'https://www.sslproxies.org/',])[:number]
        else:
            raw_list = make_request(['https://free-proxy-list.net/',
                                     'https://free-proxy-list.net/uk-proxy.html',
                                     'https://free-proxy-list.net/anonymous-proxy.html',
                                     'https://www.us-proxy.org/',
                                     'https://www.socks-proxy.net/',
                                     'https://www.sslproxies.org/',])

    # splits valid data into a list
    raw = [m.replace("<tr><td>", "").replace("</td><td", "").replace("</td></tr>", "").split(">") for m in raw_list]

    # (sorry this is long) it creates the full ip (http://47.75.62.90:80 for example) and removes/cleans the other values
    proxies = [["{}{}:{}".format("https://" if m[6].replace("class='hm'", "") == "yes " else "http://", m[0], m[1])] + [m[2].replace("class='hm'", "").strip()] + [m[3]] + [m[4].replace("class='hm'", "").strip()] for m in raw]

    # remove values values not in require
    if require:
        proxies = [m for m in proxies if (m[1].lower() or m[2].lower() or m[3].lower()) in require]

    # remove values in exclude
    if exclude:
        proxies = [m for m in proxies if (m[1].lower() or m[2].lower() or m[3].lower()) not in exclude]

    if not all((https_only, http_only)):
        if https_only:
            proxies = [m for m in proxies if m[0].startswith("https://")]
        if http_only:
            proxies = [m for m in proxies if m[0].startswith("http://")]

    # gives country and level of anonymity (mostly for debug, but sometimes useful)
    if not verbose:
        proxies = [m[0] for m in proxies]

    if number > len(proxies):
        number = len(proxies)

    if validate:
        threader(validate_proxy, number, proxies)
        proxies = VALID_PROXIES

    if not proxies:
        print("You found no proxies. Try reducing your requirements or trying again later.")
        return []

    proxies = random.sample(proxies, number)


    return proxies if number > 1 else proxies[0]

def validate_proxy(proxy_):
    """
    Validates a proxy by checking the response from a website

    Args:
        proxy: string proxy

    Returns:
        appends to global variable 'VALID_PROXIES'

    Called By:
        threader()
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Encoding': 'gzip',
        'Content-Type': 'text/html; charset=utf-8',
        }

    try:
        requests.get("https://github.com", headers=headers, proxies={'http':proxy_})
    except IOError:
        return False
    else:
        VALID_PROXIES.append(proxy_)
    return True

if __name__ == "__main__":
    main()
