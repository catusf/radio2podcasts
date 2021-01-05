"""This module purse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin, urlparse, urlunparse
import datetime
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
    items = soup.select('div.b-grid__content')
    for i in items:
        count = count + 1
        if count > no_items:
            break

        item = i.select_one('h2.b-grid__title')
        if not item:
            continue
        title = item.text.strip()
        link = url
        media = item.a.get('data-source')
        description = i.select_one('div.b-grid__desc').text.strip()
        time_string = i.select_one('span.b-grid__time').text

        time_regex = r'(\d+)/(\d+)/(\d+)'
        match = re.search(time_regex, time_string, re.M | re.I)

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        year, month, day = int(match.group(3)), int(match.group(2)), int(match.group(1))

        pub_date = datetime.datetime(
            year, month, day, 12, 0).astimezone(vt_tz)

        print(link, title, pub_date)

        mime = 'audio/mpeg'

        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type=mime))

    return articles
