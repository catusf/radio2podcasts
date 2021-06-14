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

    number = 5
    if item_titles:
        number = item_titles
    
    date = datetime.date.today()
    today = datetime.datetime(date.year, date.month, date.day)

    vt_tz = pytz.timezone('Europe/Paris')

    for i in range(number):

        pub_date = today - datetime.timedelta(i + 1)
        datestr1 = pub_date.strftime(r"%Y%m%d")
        link = f'https://www.rfi.fr/vi/t%E1%BB%95ng-h%E1%BB%A3p/{datestr1}-ch%C6%B0%C6%A1ng-tr%C3%ACnh-60-ph%C3%BAt'
        title = f'{pub_date.year}{pub_date.month}{pub_date.day} CHƯƠNG TRÌNH 60 PHÚT'
        description = "60'"
        datestr2 = pub_date.strftime(r"%Y%m")
        datestr3 = pub_date.strftime(r"%Y_%m_%d")

        media=f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/modules/actu/{datestr2}/VN_60MN_{datestr3}.mp3'

        mime = 'audio/mpeg'

        print(link, title, pub_date)

        if item_titles != None:
            item_titles.append(title)
        
        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date.astimezone(vt_tz),
                media=media,
                type=mime))
    

    return articles
