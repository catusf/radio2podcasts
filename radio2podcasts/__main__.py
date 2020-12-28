# -*- coding: utf-8 -*-

"""This is the main program to read websites and generates corresponding podcast feeds.
"""
import collections
import os
import os.path
import json

from jinja2 import Environment, FileSystemLoader

from podcasts_utils import output_rss, rss_from_webpage, send_mail_on_error

from create_cover_image import create_image
from remove_marks import remove_marks
import voh_get_articles
import vov1_get_articles
import vov2_get_articles
import vov6_get_articles
import drt_get_articles
import vnexpress_get_articles

CWD = os.getcwd()

DEST_URL = 'catusf.github.io/radio2podcasts'

PODCASTS = {}

PODCASTS_FOLDER = 'site/'

# Maps site urls to their processing functions
PROCESS_FUNCTIONS = {
    'http://vov1.vov.vn/':vov1_get_articles.get_articles_from_html,
    'http://vov2.vov.vn/':vov2_get_articles.get_articles_from_html,
    'http://vov6.vov.vn/': vov6_get_articles.get_articles_from_html,
    'http://radio.voh.com.vn': voh_get_articles.get_articles_from_html,
    'http://www.drt.danang.vn/': drt_get_articles.get_articles_from_html,
    'https://vnexpress.net/podcast': vnexpress_get_articles.get_articles_from_html,
}

def main():
    """
    Entry point
    :return:
    """

    global PODCASTS

    if not os.path.exists(PODCASTS_FOLDER):
        os.makedirs(PODCASTS_FOLDER)

    with open('podcasts.json', 'r', encoding='utf-8') as outfile:
        PODCASTS = json.load(outfile)

    for site in PODCASTS['websites']:
        site_url = PODCASTS['websites'][site]['home']
        PODCASTS['websites'][site]['function'] = PROCESS_FUNCTIONS[site_url]

    feed_settings = collections.namedtuple('feed_settings',
                                           {'source_page_url',
                                            'no_items',
                                            'container_CSS_selector',
                                            'output_file',
                                            'output_url',
                                            'title',
                                            'subtitle',
                                            'author',
                                            'img_url',
                                            'language',
                                            'copyright',
                                            })

    file_loader = FileSystemLoader(os.path.join(os.getcwd(), 'templates'))
    env = Environment(loader=file_loader)
    index_file_name = 'index.html'
    index_file_path = PODCASTS_FOLDER + index_file_name

    template = env.get_template('template.html')

    render_sites = []

    for sitename in PODCASTS['websites']:
        website = PODCASTS['websites'][sitename]

        render_site = {'name': sitename,
                       'url': website['home'], 'podcasts': []}

        for name in website['programs']:
            program = website['programs'][name]
            # home = PODCASTS['broadcaster']['home']
            title = program['title']
            no_items = program['no']

            subtitle = program['subtitle']
            url = program['url']
            bare_title = remove_marks(title)
            filename = bare_title + PODCASTS['podcasts']['podcast_ext']
            output_file = PODCASTS_FOLDER + filename
            host = PODCASTS['podcasts']['host']
            output_url = host + filename
            image_file = bare_title + '.png'
            image_path = PODCASTS_FOLDER + image_file
            cover_url = host + image_file

            subslink = f"https://www.subscribeonandroid.com/{DEST_URL}/{filename}"
            render_site['podcasts'].append(
                {'title': title, 'subslink': subslink, 'link': output_url})

            print(output_file)

            create_image(sitename, title.upper(), image_path)

            # continue

            this_feed_settings = feed_settings(
                source_page_url=url,
                no_items=no_items,
                container_CSS_selector='h4.title-header',
                output_file=output_file,
                output_url=output_url,
                title=title,
                subtitle=subtitle,
                author={'name': 'catus.phan', 'email': 'catus.phan@gmail.com'},
                img_url=cover_url,
                language='vi',
                copyright=name,
            )

            # if sitename in {'VOV2'}:
            #     print('Here')

            rss = rss_from_webpage(this_feed_settings, website['function'])
            output_rss(rss, this_feed_settings.output_file)

        render_sites.append(render_site)

    output = template.render(sites=render_sites)
    # print(output)

    with open(index_file_path, 'w', encoding='utf-8') as file:
        file.write(output)

DE = False  # True

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
        send_mail_on_error(str(ex))
