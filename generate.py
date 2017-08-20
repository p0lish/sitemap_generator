#!/usr/bin/python
import datetime

import requests
import urllib.error
import urllib.request
import urllib.parse
import random
import sys
import argparse
from bs4 import BeautifulSoup

from logger import getLogger
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import fromstring, tostring

__author__ = "polish"

_description = "Scan and collect all links on a website."
parser = argparse.ArgumentParser(description=_description)

parser.add_argument('--url', metavar='url', type=str, help='The site url for scanning')

logger = getLogger(__name__, 'sitemap.generator.log')

ROOT_DIR = "./"
USERAGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
]

SKELETON_CONTENT = '''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                      </urlset>
                   '''

HTML_MIMETYPE = "text/html"
DEFAULT_PRIORITY=0.5

# get contents from url #


def random_user_agent():
    return random.choice(USERAGENTS)


USERAGENT = random_user_agent()


def get_content(url):
    try:
        req = requests.get(url, headers={'User-Agent': USERAGENT}, verify=False)
        content = req.content
        mimetype = req.headers['content-type']
        if HTML_MIMETYPE in mimetype:
            return content
    except urllib.error.HTTPError as e:
        logger.info("this url not working properly %s the error is: %s", url, e)
    except requests.exceptions.InvalidSchema as invalidschema:
        collect_wrong_urls(url)
    return ""


def collect_wrong_urls(url):
    with open("malformed_urls.txt", 'a') as f:
        f.write(url)


def generateFilename(url):
    filename = url.replace("/", "").replace(":", "")
    return "{}.xml".format(filename)


def apply_link_filter(link):
    if link is '':
        return False
    elif link is "#":
        return False
    elif link is "javascript://":
        return False
    else:
        return True

def is_link_in_same_domain(root, link):
    prefix="www."
    root_domain = root.split("//", 1)[1]
    if root_domain.startswith(prefix):
        root_domain = root_domain[len(prefix):]
    link_domain = link.split("//", 1)[1].split("/")[0].split("?")[0]
    if link_domain.startswith(prefix):
        link_domain = link_domain[len(prefix):]
    return root_domain == link_domain

def get_all_links_from(current_url, m, h):
    content = get_content(current_url)
    soupContent = BeautifulSoup(content, 'html.parser')
    urls = []
    links = soupContent.findAll('a', href=True)
    for i in links:
        link = i['href']
        link = create_valid_url(link, m, h)
        if is_link_in_same_domain(m, link):
            if apply_link_filter(link):
                urls.append(link)
    return urls


def url_to_xmlcontent(c):
    c = c.replace("&", "&amp;")
    xml_element = '''
    
    <url>
        <loc>{url}</loc>
        <lastmod>{lastmod}</lastmod>
        <priority>{priority}</priority>
    </url>
    
    '''.format(url=c,
               lastmod=datetime.datetime.now(),
               priority=DEFAULT_PRIORITY
               )
    return ET.fromstring(xml_element)


def create_valid_url(url, main_url, http_prefix):
    if url.startswith("//"):
        url = http_prefix + ":" + url
    elif url.startswith("/"):
        url = main_url + url
    elif url.startswith("../"):
        url = main_url + "/" + url
    elif url.startswith("http"):
        return url
    else:
        url = main_url + "/" + url
    return url


def ready(_url):
    if _url == None:
        print("No url given bye. please use ./lincCrawl --url <siteurl>")
        sys.exit()
    requests.packages.urllib3.disable_warnings()
    COUNTER = 0
    MAIN_URL = _url
    http_prefix = _url.split("://")[0]
    link_pool = set()
    visited_links = []
    with open(generateFilename(_url), 'w') as f_http:
        f_http.write(SKELETON_CONTENT)
    filename = generateFilename(_url)
    doc = ET.parse(filename)
    root = doc.getroot()
    link_pool.add(_url)
    while len(link_pool) > 0:
        current_url = link_pool.pop()
        if current_url not in visited_links:
            COUNTER += 1
            print(current_url, COUNTER, len(link_pool))
            links = get_all_links_from(current_url, MAIN_URL, http_prefix)
            xml_entry = url_to_xmlcontent(current_url)
            root.append(xml_entry)
            doc.write(filename)
            link_pool = link_pool.union(links)
            visited_links.append(current_url)
    ET.ElementTree(root).write(filename, encoding="utf-8", xml_declaration=True)


if __name__ == '__main__':

    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    args = parser.parse_args()
    ready(args.url)
