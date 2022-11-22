"""This module purse Phatphapungdung website to get the contents for podcast feed.
"""

import collections
import datetime
import json
import pytz
import requests
import pickle
from bs4 import BeautifulSoup
import htmldate
from datetime import datetime
import hashlib


SITE_DATE_META = 'site_dates.json'

def find_episodes(link):
    ''' Finds all episodes of a single audio book of Phatphapungdung site
    '''
    # link =  'https://phatphapungdung.com/sach-noi/vua-co-lau-pham-minh-thao-bien-soan-178912.html'

    ret = requests.get(link)
    soup = BeautifulSoup(ret.content, 'html.parser')

    title = soup.find('title').text
    text_to_remove = {' - Sách Nói Online Hay': "",
                      'Sách nói ': "",
                      }

    for text in text_to_remove:
        title = title.replace(text, text_to_remove[text])

    print(title)
    media = soup.find('div', class_='td-post-content')
    items = media.findAll('a', {'data-item': True})

    if not items:
        items = media.findAll('div', {'data-item': True})

    print(f'Length {len(items)}')
    episodes = []
    no_items = len(items)
    for n, i in enumerate(items):
        encoded = i['data-item']
        decoded = bytes(encoded, 'utf-8').decode('unicode-escape').replace('\\', '').replace('\n', '')
        decoded_json = json.loads(decoded)
        subtitle = decoded_json.get('fv_title', '')
        media_link = decoded_json['sources'][0]['src']
        mime_type = decoded_json['sources'][0]['type']

        etitle = f"{title} - {subtitle}"
        if no_items:
            if n == 0:
                etitle = f'▶ {n+1}/{no_items} ' + etitle
            else:
                etitle = f'{n+1}/{no_items} ' + etitle

        print(f"{etitle}\n\t{media_link}\n\t{mime_type}")

        episodes.append(
            {'episode_title': etitle, 'media': media_link, 'mime': mime_type, })

    return episodes


def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """

    del url, podcast_title
    feed_article = collections.namedtuple(
        'feed_article', {
            'link', 'title', 'description', 'pub_date', 'media', 'type'})
    articles = list()

    # debug = False
    count = 0
    # now = datetime(2020, 7, 1) # Fixed published  dates because they are not available

    books = [ ]
    
    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')

    # Get the top articles
    content_soup = soup.select_one('div.td_block_inner')
    items = content_soup.select('div.td-module-thumb')
    for n, i in enumerate(items):
        count = count + 1
        if count > no_items:
            break

        item = i.a
        link = item.get('href')
        title = item.get('title')
        idesc = None #i.select_one('div.td-excerpt')
        if idesc:
            description = i.select_one('div.td-excerpt').text.strip()
        else:
            description = 'N/A'

        print(title, link)

        books.append({'link': link, 'description': description})

    content_soup = soup.select_one('div.td-ss-main-content')
    items = content_soup.select('div.item-details')

    for n, i in enumerate(items):
        count = count + 1
        if count > no_items:
            break

        item = i.select_one('h3.entry-title')
        link = item.a.get('href')
        title = item.text.strip()
        idesc = i.select_one('div.td-excerpt')
        if idesc:
            description = i.select_one('div.td-excerpt').text.strip()
        else:
            description = 'N/A'
            
        books.append({'link': link, 'description': description})

        print(title, link)

    with open(SITE_DATE_META, 'r', encoding='utf-8') as outfile:
        SITE_DATES = json.load(outfile)

        print(f'Number of sites stored: {len(SITE_DATES)}')

    for book in books:
        link = book['link']
        description = book['description']

        time_format = '%Y-%m-%dT%H:%M:%S' # r'%m/%d/%Y, %H:%M:%S'

        modified_date_str = htmldate.find_date(link, outputformat=time_format, extensive_search=False)
        modified_date = datetime.strptime(modified_date_str, time_format)

        hexdigest =  hashlib.md5(link.encode()).hexdigest()

        if hexdigest not in SITE_DATES:
            SITE_DATES[hexdigest] = {'modified': modified_date_str}
            print(f'New date: {modified_date_str}')
        else:
            if datetime.strptime(SITE_DATES[hexdigest]['modified'], time_format) >= modified_date:
                print('Nothing changes')
                # continue

        episodes = find_episodes(link)

        # Increase one minute every item
        min_added = datetime.timedelta(minutes=n)
        pub_date = (modified_date+min_added).astimezone(vt_tz)

        for m, e in enumerate(episodes):
            # Add one second for every episode, so they can be sorted
            sec_added = datetime.timedelta(seconds=m)
            articles.append(
                feed_article(
                    link=link,
                    title=e['episode_title'],
                    description=description,
                    pub_date=pub_date + sec_added,
                    media=e['media'],
                    type=e['mime']))

    with open(SITE_DATE_META, 'w', encoding='utf-8') as outfile:
        json_object = json.dumps(SITE_DATES, indent=4)
        outfile.write(json_object)

    return articles
