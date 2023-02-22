"""This module parse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urljoin
import datetime
import re
import pytz

def process_item(title, rmedia, rlink, url):
    '''
    Takes title, media and link, then produces necessary item for podcasts:
    '''
    media = urljoin(url, rmedia)
    link = urljoin(url, rlink)

    time_regex = r'(\d+)-(\d+)-(\d+)'
    match = re.search(time_regex, title, re.M | re.I)

    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    year, month, day = int(match.group(3)), int(match.group(2)), int(match.group(1))

    pub_date = datetime.datetime(
        year, month, day, 12, 0).astimezone(vt_tz)

    return (link, media, pub_date)

def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """
    del item_titles

    del podcast_title

    feed_article = collections.namedtuple(
        'feed_article', {'link', 'title', 'description', 'pub_date', 'media', 'type'})

    articles = list()

    # debug = False
    count = 0

    top_item = soup.find('script', text=re.compile('mp3'))
    string = top_item.string
    pieces = re.split(r"[()',;]", string)
    rmedia = pieces[2]
    title = pieces[8]
    rlink = pieces[11]
    description = title

    link, media, pub_date = process_item(title, rmedia, rlink, url)

    print(link, title, pub_date)

    if item_titles is not None:
        item_titles.append(title)

    articles.append(
        feed_article(
            link=url,
            title=title,
            description=description,
            pub_date=pub_date,
            media=media,
            type='audio/mpeg')
        )


    items = soup.select('div.TinTuc_Left_Item')
    for i in items:
        count = count + 1
        if count > no_items:
            break

        item = i.select_one('a', class_='text_Green')
        rmedia = item['data-url']
        rlink = item['href']
        title = item['data-title']
        description = title

        link, media, pub_date = process_item(title, rmedia, rlink, url)

        print(link, title, pub_date)

        articles.append(
            feed_article(
                link=link,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type='audio/mpeg')
            )

    return articles
