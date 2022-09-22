"""This module parse VOH website to get the contents for podcast feed.
"""

import collections
from urllib.parse import urlparse
import datetime
import json
import os
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
    temp_list = list()

    # debug = False

    file_list = []

    items = json.loads(soup.select('input')[0]['value'])
    for num, i in enumerate(items):

        if num > no_items:
            break

        file_name = i['sources'][0]['file']

        file_list.append(file_name)

    file_list.sort()

    articles = []

    for num, file_name in enumerate(file_list):

        media = 'https://archive.org' + file_name

        title = file_name[file_name.rfind('/')+1:-4]

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

    # if len(temp_list) < 2: # Just one item, returns it
    #     return temp_list

    # # Find the first difference if file name
    # parsed1 = urlparse(temp_list[0].media) # First item
    # parsed2 = urlparse(temp_list[1].media) # Second item

    # filebase1 = os.path.splitext(os.path.basename(parsed1.path))[0]
    # filebase2 = os.path.splitext(os.path.basename(parsed2.path))[0]

    # poss = diff_positions(filebase1, filebase2)

    # if len(poss) < 1:
    #     pos = min(len(filebase1), len(filebase2)) - 1
    # else:
    #     pos = poss[0]

    # sorted_list = list()

    # for i in temp_list:
    #     parsed = urlparse(i.media)
    #     filebase = os.path.splitext(os.path.basename(parsed.path))[0]
    #     num = filebase[pos:] # Extract the number part of the filename

    #     if num.isnumeric():
    #         sorted_list.append((i, num.zfill(2))) # Add one padding zero if this is a number and less than 10
    #     else:
    #         sorted_list.append((i, num))

    # sorted_list.sort(key=lambda x: x[1])

    # articles = list()

    # count = 1
    # for i, num in sorted_list:
    #     articles.append(
    #         feed_article(
    #             link=i.link,
    #             title=i.title,
    #             description=i.description,
    #             pub_date=i.pub_date + datetime.timedelta(minutes=count),
    #             media=i.media,
    #             type=i.type)
    #     )
    #     count = count + 1

    # for i in articles:
    #     print(i.pub_date, i.media)

    return articles
