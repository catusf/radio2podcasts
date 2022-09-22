"""This module parse VOH website to get the contents for podcast feed.
"""

import collections
import datetime
import json
import pytz

# from podcasts_utils import get_true_url

def diff_positions(str1, str2):
    """
    Finds list of positions where the strings differs
    """
    return [i for i in range(len(str1)) if str1[i] != str2[i]]

def get_articles_from_html(soup, url, no_items, podcast_title, item_titles=None):
    """
    Takes an HTML string and extracts children according to
    Returns a set of namedtuples with link, title and description
    """
    del item_titles

    feed_article = collections.namedtuple(
        'feed_article', {
            'link', 'title', 'description', 'pub_date', 'media', 'type'})

    # debug = False

    file_list = []

    items = json.loads(soup.select('input')[0]['value'])
    for num, i in enumerate(items):

        if num > no_items:
            break

        file_name = i['sources'][0]['file']
        title = i['orig'].replace('.mp3', '')

        file_list.append((file_name, title))

    file_list.sort(key = lambda x: x[1])

    articles = []

    for num, i in enumerate(file_list):

        media = 'https://archive.org' + i[0]

        title = i[1]

        description = ''

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        year, month, day = 2021, 12, 22

        pub_date = datetime.datetime(year, month, day, 12, 0).astimezone(vt_tz)

        articles.append(
            feed_article(
                link=url,
                title=title,
                description=description,
                pub_date=pub_date,
                media=media,
                type='audio/mpeg')
            )

    return articles
