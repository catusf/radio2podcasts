"""This module purse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin, urlparse, urlunparse
from datetime import datetime, timedelta
import re
import pytz
import requests
from bs4 import BeautifulSoup
import json

from podcasts_utils import get_true_url

def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """
    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    year, month, day = 2021, 12, 31
    pub_date = datetime(year, month, day, 12, 0).astimezone(vt_tz)

#    del item_titles
    JSON_META_FILE = r'./radio2podcasts/all_meta.json'
    
    items = []
    with open(JSON_META_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    feed_article = collections.namedtuple(
        'feed_article', {
            'link', 'title', 'description', 'pub_date', 'media', 'type'})
    articles = list()

    # debug = False
    count = 0

    # items = soup.select('div.wrapper-item-large')
    for i in items:
        count = count + 1
        if count > no_items:
            break

        pub_date = pub_date - timedelta(days=1)

        media = items[i]['mp3']

        if not media:
            print(f'{i=}')

            media = url

        tags = ' - '.join(items[i]['tags'])
        title = f"{items[i]['title_en']} - {items[i]['title_zh']} # [{tags}] "

        text = ''.join(items[i]['text'])

        all = ''

        for c, e, p in zip(items[i]['chinese'], items[i]['english'], items[i]['pinyin']):
           all += f'{c} ({p} {e}) ' 

        description = f'{text}\n{all}'

        mime_type = 'audio/mpeg'

        articles.append(
            feed_article(
                link=url+i[3:],
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type=mime_type))

    return articles
