"""This module purse Phatphapungdung website to get the contents for podcast feed.
"""

import collections
from datetime import datetime
import json
import pytz
import requests
from bs4 import BeautifulSoup


def find_episodes(link):
    ''' Finds all episodes of a single audio book of Phatphapungdung site
    '''
    # link =  'https://phatphapungdung.com/sach-noi/vua-co-lau-pham-minh-thao-bien-soan-178912.html'

    ret = requests.get(link)
    soup = BeautifulSoup(ret.content, 'html.parser')

    desc = soup.select_one('div.b-grid__desc').text.strip()

    # text_to_remove = {' - Sách Nói Online Hay': "",
    #                   'Sách nói ': "",
    #                   }

    # for text in text_to_remove:
    #     title = title.replace(text, text_to_remove[text])

    print(desc)
    media = soup.find('div', class_='c-chap-list alfAjax')
    items = items = media.select('div.b-grid__content')

    print(f'Length {len(items)}')
    episodes = []
    no_items = len(items)

    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    for n, i in enumerate(items):
        media_link = i.a['data-source']
        mime_type = 'audio/mpeg'
        etitle = i.a.text.strip()
        time_str = i.select_one('span.b-grid__time').text
        pub_time = datetime.strptime(time_str, r'%d/%m/%Y').astimezone(vt_tz)

        if no_items:
            if n == 0:
                etitle = f'▶ {n+1}/{no_items} ' + etitle
            else:
                etitle = f'{n+1}/{no_items} ' + etitle

        print(f"{etitle}\n\t{media_link}\n\t{mime_type}")

        episodes.append(
            {'episode_title': etitle, 'media': media_link, 'mime': mime_type, 'pub_time':pub_time})

    return episodes, desc


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

    content_soup = soup.select_one('ul.clearfix')
    items = content_soup.select('div.c-square-item__thumb')

    for n, i in enumerate(items):
        count = count + 1
        if count > no_items:
            break

        link = i.select_one('a').get('href')
        title = i.select_one('img').get('alt').strip()

        print(title, link)

        if item_titles != None:
            item_titles.append(title)

        episodes, description = find_episodes(link)

        for m, e in enumerate(episodes):
            # Add one second for every episode, so they can be sorted
            articles.append(
                feed_article(
                    link=link,
                    title=e['episode_title'],
                    description=description,
                    pub_date=e['pub_time'],
                    media=e['media'],
                    type=e['mime']))

    return articles
