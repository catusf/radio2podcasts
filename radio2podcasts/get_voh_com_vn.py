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

    items = soup.select('div.wrapper-item-large')
    for i in items:
        count = count + 1
        if count > no_items:
            break

        item = i.select_one('h3.title-article')
        link = urljoin(url, item.a.get('href'))
        title = item.text.strip()
        description = i.select_one('p.time').text.strip()

        time_regex = r'(\d+):(\d+) - (\d+)/(\d+)/(\d+)'
        match = re.search(time_regex, description, re.M | re.I)

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        year, month, day, hour, minute = int(match.group(5)), int(match.group(4)), int(
            match.group(3)), int(match.group(1)), int(match.group(2))

        pub_date = datetime.datetime(
            year, month, day, hour, minute).astimezone(vt_tz)

        print(link, title, pub_date)

        if item_titles is not None:
            item_titles.append(title)

        spage = requests.get(link)
        ssoup = BeautifulSoup(spage.content, 'html.parser')

        # print(spage.content)
        rmedia = ssoup.select_one('source')['src']
        mime = ssoup.select_one('source')['type']
        parsed = urlparse(url)
        home = urlunparse((parsed[0], parsed[1], '', '', '', ''))

        media = rmedia
        # # print(media)

        true_url = get_true_url(media)  # Get length of media file

        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=true_url,
                type=mime))

    return articles
