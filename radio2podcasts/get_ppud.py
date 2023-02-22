"""This module purse Phatphapungdung website to get the contents for podcast feed.
"""

import xml.etree.ElementTree as ET

import collections
import json
from datetime import datetime, timedelta
import hashlib
import requests
import pytz
from bs4 import BeautifulSoup

SITEMAP_DATES = {}
SITEMAP_DATES_FILE = 'sitemap_dates.json'
SITE_DATE_META = 'site_dates.json'
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S' # Normalized time format

def load_rss(url):
    """
    Loads an XML from the internet and returns its string contents
    """

    # creating HTTP response object from given url
    resp = requests.get(url)

    return resp.content

def parse_xml(xmlstring):
    """
    Parses the XML string and returns list of urls:modified datses
    """

    # create element tree object
    tree = ET.ElementTree(ET.fromstring(xmlstring))

    # get root element
    root = tree.getroot()
  
    # create empty list for news items
    pages = {}
    print('Start parsing')
    
    # iterate news items
    count = 0
    for item in root:
        # print(item.tag, item.attrib)
        count += 1
        # if count > 3:
        #     break

        loc = item[0].text
        timestamp = item[1].text
        print(f'{timestamp}: {loc}')

        # append news dictionary to news items list
        link_hash =  hashlib.md5(loc.encode()).hexdigest()

        pages[link_hash] = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").strftime(TIME_FORMAT)
    
    print(f'Number of pages in sitemap: {count}')
    
    return pages
      
def load_sitemaps():
    ''' Read sitemap and return a list of urls:modified dates
    '''
    global SITEMAP_DATES

    # url of rss feed
    urls = [
        'https://phatphapungdung.com/sach-noi/post-sitemap2.xml',
        'https://phatphapungdung.com/sach-noi/post-sitemap1.xml']

    # load rss from web to update existing xml file
    for url in urls:
        contents = load_rss(url)
  
        # parse xml file
        SITEMAP_DATES = SITEMAP_DATES | parse_xml(contents)

    with open(SITEMAP_DATES_FILE, 'w', encoding='utf-8') as file:
        print(f'Number of pages in sitemap: {len(SITEMAP_DATES_FILE)}')
        
        file.write(json.dumps(SITEMAP_DATES, indent=4))

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

    del item_titles

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

        if item_titles is not None:
            item_titles.append(title)

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

        if item_titles is not None:
            item_titles.append(title)

        idesc = i.select_one('div.td-excerpt')
        if idesc:
            description = i.select_one('div.td-excerpt').text.strip()
        else:
            description = 'N/A'
            
        books.append({'link': link, 'description': description})

        print(title, link)

    with open(SITE_DATE_META, 'r', encoding='utf-8') as outfile:
        PAGES_DATES = json.load(outfile)

        print(f'Number of pages stored: {len(PAGES_DATES)}')

    if not len(SITEMAP_DATES):
        load_sitemaps()

    for book in books:
        link = book['link']
        description = book['description']

#        modified_date_str = htmldate.find_date(link, outputformat=TIME_FORMAT, extensive_search=False)
#        modified_date = datetime.strptime(modified_date_str, TIME_FORMAT)

        link_hash =  hashlib.md5(link.encode()).hexdigest()

        if link_hash not in SITEMAP_DATES:
            modified_date = datetime.today()
        else:
            modified_date = datetime.strptime(SITEMAP_DATES[link_hash],TIME_FORMAT)

        modified_date_str = datetime.strftime(modified_date, TIME_FORMAT)

        if link_hash not in PAGES_DATES or datetime.strptime(PAGES_DATES[link_hash]['modified'], TIME_FORMAT) < modified_date:
            PAGES_DATES[link_hash] = {'modified': modified_date_str}
            print(f'New date: {modified_date_str}')
        else:
            print('Nothing changes')
        #    continue

        episodes = find_episodes(link)

        # Increase one minute every item
        #book_time_added = timedelta(days=0)
        pub_date = (modified_date).astimezone(vt_tz)

        for m, e in enumerate(episodes):
            # Add one second for every episode, so they can be sorted
            episode_time_added = timedelta(hours=m)
            episode_link = f'{link}#{m}'
            articles.append(
                feed_article(
                    link=episode_link,
                    title=e['episode_title'],
                    description=description,
                    pub_date=pub_date + episode_time_added,
                    media=e['media'],
                    type=e['mime']))

    with open(SITE_DATE_META, 'w', encoding='utf-8') as outfile:
        
        outfile.write(json.dumps(PAGES_DATES, indent=4))

    return articles
