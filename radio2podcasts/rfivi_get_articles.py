"""This module purse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin, urlparse, urlunparse
import datetime
from dateutil import parser
import json
import re
import pytz
import requests
from bs4 import BeautifulSoup

from podcasts_utils import get_true_url


def get_articles_from_html(soup, url, no_items, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """

    feed_article = collections.namedtuple(
        'feed_article', {
            'link', 'title', 'description', 'pub_date', 'media', 'type'})
    articles = list()

    # debug = False
    count = 0
    items = soup.select('div.m-item-list-article')
    for i in items:
        count = count + 1
        if count > no_items:
            break

        title = i.select_one('p.article__title').text.strip()
        link = i.a.get('href')
        
        parsed = urlparse(url)
        link = urlunparse((parsed[0], parsed[1], link, '', '', ''))
        
        # media = i.a.get('data-source')
        # description = i.select_one('div.b-grid__desc').text.strip()
        time_string = i.find('time').get('datetime')

        vt_tz = pytz.timezone('Europe/Paris')

        pub_date = parser.parse(time_string).astimezone(vt_tz)

        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        spage = requests.get(link, headers=headers)
        ssoup = BeautifulSoup(spage.content, 'html.parser')

        # print(spage.content)
        child = ssoup.select_one('button.m-feed-sub__audio').select_one('script')
        
        j=json.loads(list(child.children)[0])
        media = j['sources'][0]['url']
        title = description = j['diffusion']['title'] + " " + str(pub_date.date())
        mime = 'audio/mpeg'

        print(link, title, pub_date)
        
        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type=mime))

    return articles
