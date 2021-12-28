"""This module parse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin
import datetime
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

    items = soup.select('div.story')
    for i in items:
        # try:
        count = count + 1
        if count > no_items:
            break

        if i.h1:
            item = i.h1
        else:
            item = i.h4

        title = item.text.strip().replace('\n', ' ')

        link = urljoin(url, item.a['href'])
        description = i.find('p', class_='moreless-content').get_text().strip()
        updated = i.find('span', class_='time').text

        time_regex = r'(\d+)/(\d+)/(\d+)'
        match = re.search(time_regex, updated, re.M | re.I)

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        year, month, day = int(match.group(3)), int(match.group(2)), int(match.group(1))

        pub_date = datetime.datetime(year, month, day, 12, 0).astimezone(vt_tz)

        spage = requests.get(link)
        ssoup = BeautifulSoup(spage.content, 'html.parser')

        print(link, title, pub_date)

        if item_titles is not None:
            item_titles.append(title)

        # print(spage.content)
        source = ssoup.find('source')
        mime = ssoup.select_one('source')['type']

        true_url = ''
        if source:
            true_url = source['src']

        if title and pub_date and true_url:
            articles.append(
                feed_article(
                    link=link,
                    title=title,
                    description=description,
                    pub_date=pub_date,
                    media=true_url,
                    type=mime))

        # except:
        #     print(f'An exception occured while processing {link}')

    return articles
