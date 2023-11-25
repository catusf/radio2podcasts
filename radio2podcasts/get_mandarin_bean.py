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
from pathvalidate import sanitize_filename

from podcasts_utils import get_true_url


def title_to_filename(url):
    return sanitize_filename(f'Article-{url}.html')


ALL_PODCAST_NAME = 'All'

LEVEL_BAG = {'Advanced',
             'Beginner',
             'Intermediate'}

CATEGORY_BAG = {
    'Biz&Economics',
    'Culture',
    'Fun',
    'Lifestyle',
    'News',
    'Story',
}

HSK_BAG = {
    'HSK1'
    'HSK2',
    'HSK3',
    'HSK4',
    'HSK5',
    'HSK6',
}

TOO_LONG_CAT = 'Business &amp; Economics'
SHORT_CAT = 'Biz&Economics'


def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """
    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    year, month, day = 2021, 12, 31
    pub_date = datetime(year, month, day, 12, 0).astimezone(vt_tz)

    # Mappin between file names and urls of articles
    LINK_FILE_NAME = './radio2podcasts/MandarinBeanLinks.json'
    with open(LINK_FILE_NAME, 'r', encoding='utf-8') as f:
        print(f'Loading {LINK_FILE_NAME}')
        link_list = json.load(f)

    file_link_map = {}
    file_order_map = {}

    for i, link in enumerate(link_list):
        filename = '..\\' + title_to_filename(link_list[link])
        file_link_map[filename] = link
        file_order_map[filename] = i

    TITLE_PATTERN = r'Mandarin Bean (.+)'

    match = re.match(TITLE_PATTERN, podcast_title)

    if not match:
        exit(f'Wrong Title: {podcast_title}')

    podcast_name = match.group(1)

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

    hsk_list = []
    category_list = []
    level_list = []
    order_list = []

    for i in items:
        count = count + 1
        if count > no_items:
            break

        hsk = ''
        category = ''
        level = ''

        # pub_date = pub_date - timedelta(days=1)

        media = items[i]['mp3']

        if not media:
            print(f'{i=}')

            media = url

        tags = items[i]['tags']

        new_tags = []
        for tag in tags:
            if tag == TOO_LONG_CAT:
                tag = SHORT_CAT

            new_tags.append(tag)

            if tag in CATEGORY_BAG:
                category = tag
            elif tag in HSK_BAG:
                hsk = tag
            elif tag in LEVEL_BAG:
                level = tag

        tag_items = []
        if hsk:
            tag_items.append(hsk)

        if category:
            tag_items.append(category)

        tags_text = ' - '.join(tag_items)

        if podcast_name != ALL_PODCAST_NAME and podcast_name not in new_tags:
            continue  # Filtered out

        hsk_list.append(hsk)
        level_list.append(level)
        category_list.append(category)
        order_list.append(file_order_map[i])

        title = f"[{tags_text}] {items[i]['title_en']} - {items[i]['title_zh']}"

        text = ''.join(items[i]['text'])

        combined = ''

        for c, e, p in zip(items[i]['chinese'], items[i]['english'], items[i]['pinyin']):
            combined += f'{c} {p} - {e}\n'

        description = f'{text}\n{combined}'

        mime_type = 'audio/mpeg'
        link = file_link_map[i]

        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type=mime_type))

    sorted_list = []

    # if podcast_name == ALL_PODCAST_NAME:
    # Sort by order of appearance on website

    if podcast_name in CATEGORY_BAG:
        # Sorts by HSK level in the same category
        sorted_list = sorted(zip(hsk_list, articles), key=lambda t: t[0])
    else:
        # Sorts by order of appearance on website for easy of looking up
        sorted_list = sorted(zip(order_list, articles), key=lambda t: t[0])

    articles = list(zip(*sorted_list))[1]  # Unzip the list

    sorted_articles = []

    # Adds dates in proper order
    for a in articles:
        sorted_articles.append(feed_article(
            link=a.link,
            title=a.title,
            description=a.description,
            pub_date=pub_date,
            media=a.media,
            type=a.type))

        pub_date = pub_date - timedelta(days=1)

    return sorted_articles
