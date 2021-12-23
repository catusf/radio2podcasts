"""This module parse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin
import datetime
import json
import re
import pytz
import requests
from bs4 import BeautifulSoup

# from podcasts_utils import get_true_url


def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
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

    items = json.loads(soup.select('input')[0]['value'])
    for n, i in enumerate(items):
        # try:
        count = count + 1
        if count > no_items:
            break
        media = 'https://archive.org' + i['sources'][0]['file']
        title = podcast_title + " P" + str(n)

        description = ''

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        year, month, day = 2021,12,22

        pub_date = datetime.datetime(year, month, day, 12, 0).astimezone(vt_tz)

        articles.append(
            feed_article(
                link=url,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type='audio/mpeg'))

        # except:
        #     print(f'An exception occured while processing {link}')

    return articles
