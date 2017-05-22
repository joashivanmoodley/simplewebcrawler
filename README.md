# simplewebcrawler
Simple Python Web Crawler
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
