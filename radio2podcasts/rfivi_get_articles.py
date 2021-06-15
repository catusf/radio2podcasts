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
    today = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

    vt_tz = pytz.timezone('Europe/Paris')

    for i in range(number):

        pub_date = today - datetime.timedelta(i+1)
        datestr1 = pub_date.strftime(r"%Y%m%d")
        datestr2 = pub_date.strftime(r"%Y%m")
        datestr3 = pub_date.strftime(r"%Y_%m_%d")

        if url == f"https://www.rfi.fr/vi/t%E1%BB%95ng-h%E1%BB%A3p/20210613-ch%C6%B0%C6%A1ng-tr%C3%ACnh-60-ph%C3%BAt":
            link = f'https://www.rfi.fr/vi/t%E1%BB%95ng-h%E1%BB%A3p/{datestr1}-ch%C6%B0%C6%A1ng-tr%C3%ACnh-60-ph%C3%BAt'
            media=f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/modules/actu/{datestr2}/VN_60MN_{datestr3}.mp3'
            title = f'{datestr1} CHƯƠNG TRÌNH 60 PHÚT'
            description = "60'"
        elif url == f"https://www.rfi.fr/vi/t%E1%BA%A1p-ch%C3%AD/13h00-13h17-gmt/20210614-th%C3%B4ng-tin-14-06-13h00-gmt":
            link = f'https://www.rfi.fr/vi/t%E1%BA%A1p-ch%C3%AD/13h00-13h17-gmt/{datestr1}-th%C3%B4ng-tin-14-06-13h00-gmt'
            media=f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/magazines/r001/13h00_-_13h17_gmt_{datestr1}.mp3'
            title = f"{datestr1} Phần đầu - 17'"
            description = "17'"
        elif url == f"https://www.rfi.fr/vi/t%E1%BA%A1p-ch%C3%AD/13h17-14h00-gmt/20210614-ph%E1%BA%A7n-c%C3%B2n-l%E1%BA%A1i-c%E1%BB%A7a-ch%C6%B0%C6%A1ng-tr%C3%ACnh-14-06-13h17-gmt":
            link = f'https://www.rfi.fr/vi/t%E1%BA%A1p-ch%C3%AD/13h17-14h00-gmt/{datestr1}-ph%E1%BA%A7n-c%C3%B2n-l%E1%BA%A1i-c%E1%BB%A7a-ch%C6%B0%C6%A1ng-tr%C3%ACnh-14-06-13h17-gmt'
            media=f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/magazines/r001/13h17_-_14h00_gmt_{datestr1}.mp3'
            title = f"{datestr1} Phần còn lại - 43'"
            description = "43'"

        mime = 'audio/mpeg'

        print(link, title, pub_date, media)

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
