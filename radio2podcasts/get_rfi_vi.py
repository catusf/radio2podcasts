"""This module purse RFI website to get the contents for podcast feed.
"""

import collections
import json
from urllib.parse import urlparse, urlunparse
from dateutil import parser
import pytz
import requests
from bs4 import BeautifulSoup

def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """

    del item_titles

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

        child = ssoup.select_one('div.m-feed-sub').select_one('script')
        data = json.loads(child.string)
        media = data['sources'][0]['url']

        datestr1 = pub_date.strftime(r"%Y%m%d")
        datestr2 = pub_date.strftime(r"%Y%m")
        datestr3 = pub_date.strftime(r"%Y_%m_%d")
        datestr4 = pub_date.strftime(r"%d-%m")

        # Other RFI podcasts have different media urls
        if podcast_title == "Chương trình 43'":
            link = f'https://www.rfi.fr/vi/t%E1%BA%A1p-ch%C3%AD/13h17-14h00-gmt/{datestr1}-ph%E1%BA%A7n-c%C3%B2n-l%E1%BA%A1i-c%E1%BB%A7a-ch%C6%B0%C6%A1ng-tr%C3%ACnh-{datestr4}-13h17-gmt'
            media = f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/magazines/r001/13h17_-_14h00_gmt_{datestr1}.mp3'
        elif podcast_title == "Chương trình 60'":
            link = f'https://www.rfi.fr/vi/t%E1%BB%95ng-h%E1%BB%A3p/{datestr1}-ch%C6%B0%C6%A1ng-tr%C3%ACnh-60-ph%C3%BAt'
            media = f'https://aod-rfi.akamaized.net/rfi/vietnamien/audio/modules/actu/{datestr2}/VN_60MN_{datestr3}.mp3'

        description = "Chương trình ngày " + pub_date.strftime(r'%d-%m-%Y ')
        title = pub_date.strftime(r'%d-%m-%Y ') + podcast_title

        mime = 'audio/mpeg'

        print(link, title, pub_date)

        if item_titles is not None:
            item_titles.append(title)

        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type=mime))

    return articles
