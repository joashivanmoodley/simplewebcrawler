'''
Simple script which includes threadpools to process links from a given url and
returns its static assets for all internal links found of the given url
lxml.html returns a tuple which looks like the following:
(<Element link at 0x107b4a208>, 'href', 'assets/css/bootstrap/bootstrap.css', 0)

    > function get_urls returns a list of internal links and saves it into a text file (sitemap.txt).
    > function get_assets  is called after we have a list of  urls and crawls each url and stores
      its returns in the same text file as above.
      script requires:
      > python 2.7x
      > lxml
      > requests
      > multiprocessing(default with python)
Usage:

> run tests:
  python webcrawler.py run-tests
> run crawls:
   python webcrawler.py <www.domain.com>
'''

#!/usr/bin/python

import sys
from lxml import html
import requests
import re
from multiprocessing.pool import ThreadPool
import unittest

ASSETS_SEARCH_TERMS = re.compile(".css|.js|.png|.jpeg|.jpg|.gif|.svg")


class TestCrawler(unittest.TestCase):
    def runTest(self):
        # check to see if any of our search terms are in the data returned.
        test_passed = False
        data = get_assets("http://www.yoyowallet.com/index.html", test=True)
        for url in data:
            if ASSETS_SEARCH_TERMS.search(url):
                test_passed = True
                break
        if test_passed:
            print "Success"
        else:
            print "not static files found"

    def runTestCheckReturnType(self):
        # check to see if get_urls returning a list
        if type(get_urls('http://www.yoyowallet.com', True)) is list:
            print "Success"
        else:
            print "Fail %s" % type(get_urls('http://www.yoyowallet.com', True))


def get_urls(domain, test=False):
    URLS = []
    try:
        response = requests.get(domain)
        if response.status_code == 200:
            page = html.fromstring(response.content)
            striped_domain = domain.replace('http://', '').replace('https://', '')
            for l in page.iterlinks():
                # we only interested in anything that has a href tag here
                if l[1] == 'href':
                    # remove protocol to compare apples with apples
                    link = l[2].replace('http://', '').replace('https://', '')
                    if link.startswith(striped_domain):
                        if not l[2].startswith("http"):
                            link = "http://%s/%s" % (striped_domain, link)
                        # check for links where the protocol isn't there by default
                        elif l[2].startswith("//"):
                            link = "http:%s" % link
                        URLS.append(link)
                    else:
                        if link.endswith('.html') and (
                            link.startswith('/') or '/' not in link
                        ):
                            # check for relative links
                            URLS.append(link)
                        elif link.startswith('/') and not ASSETS_SEARCH_TERMS.search(link):
                            # make sure we not collect static urls
                            URLS.append(link)

                        else:
                            if not link.startswith('www.') and link != '#' and not ASSETS_SEARCH_TERMS.search(link):
                                if 'http' not in l[2]:
                                    URLS.append(l[2])
            if not test:
                f = open("sitemap.txt", "a")
                f.write("sitemap:\n")
                for url in URLS:
                    f.write("%s\n" % url)
                f.close()
            return map(lambda url: "%s/%s" % (domain, url) if not url.startswith('/') else "%s%s" % (domain, url), URLS)
        else:
            print "Website is not reachable., status code: %s" % response.status_code
            return []
    except Exception, e:
        print e
        return []


def get_assets(domain, test=False):
    ASSETS = []
    response = requests.get(domain)
    root_domain = sys.argv[1]
    if "http" not in root_domain:
        # if the protocol is not included default to http
        root_domain = "http://%s" % root_domain
    if response.status_code == 200:
        page = html.fromstring(response.content)
        domain = domain.replace('http://', '').replace('https://', '')
        try:
            for l in page.iterlinks():
                link = l[2].strip()
                # check if any of the urls  match our regex for asset files
                if ASSETS_SEARCH_TERMS.search(link):
                    if not link.startswith("http"):
                        # check if we have a relative link
                        link = "%s/%s" % (root_domain, link)
                    elif l[2].startswith("//"):
                        # if protocol not included
                        link = "http:%s" % link
                    elif l[2].startswith('/'):
                        # because the above will excute before this line its save to add this check here to see if there is relative links to static file urls
                        link = "%s/%s" % (root_domain, link)

                    ASSETS.append(link)
            if not test:
                f = open("sitemap.txt", "a")
                f.write("\nAssets on %s\n" % domain)
                for asset in ASSETS:
                    f.write("%s\n" % asset)
                f.close()
            else:
                return ASSETS
        except Exception, e:
            print e
    else:
        print "Unable to access %s, status code: %s" % (domain, response.status_code)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        # Get the Domain that we going to crawl
        args = sys.argv[1]
        if args in ['run-tests']:
            tests = TestCrawler()
            tests.runTestCheckReturnType()
            tests.runTest()
            sys.exit(0)
        elif "http" not in args:
            # if the protocol is not included default to http
            args = "http://%s" % args
    else:
        print "No URL given."
        sys.exit(0)
    try:
        # Enable Treading to allow for faster processing
        pool = ThreadPool(100)
        pool.map(get_assets, get_urls(args))
        pool.close()
        pool.join()
    except Exception, e:
        print e
        sys.exit(0)
