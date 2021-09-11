# -*- coding: utf-8 -*-

"""This is the main program to read websites and generates corresponding podcast feeds.
"""
import collections
import os
import os.path
import json
import re
import argparse

from jinja2 import Environment, FileSystemLoader

from podcasts_utils import output_rss, rss_from_webpage, number_in_cirle, send_mail_on_error

from create_cover_image import create_image
from remove_marks import remove_marks
import voh_get_articles
import vov1_get_articles
import vov2_get_articles
import vov6_get_articles
import drt_get_articles
import vnexpress_get_articles
import vovlive_get_articles
import rfivi_get_articles
import ppud_get_articles

DE = True # False

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
    'https://vovlive.vn/': vovlive_get_articles.get_articles_from_html,
    'https://www.rfi.fr/vi/': rfivi_get_articles.get_articles_from_html,
    'https://phatphapungdung.com/sach-noi/': ppud_get_articles.get_articles_from_html,
}

def main():
    """
    Entry point of the module
    :return: error code is issue occurs
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Name of JSON input file for podcast feed', type=str, required=True)
    parser.add_argument('-o', '--output', help='Name of HTML output file containing description of all podcasts', type=str, required=True)
    parser.add_argument('-d', '--debug', help='Debug mode True/False', default=False, type=bool)
    args = parser.parse_args()

    global PODCASTS

    if args.debug:
        debug_sites = {'RFI',}

    if not os.path.exists(PODCASTS_FOLDER):
        os.makedirs(PODCASTS_FOLDER)

    with open(args.input, 'r', encoding='utf-8') as outfile:
        PODCASTS = json.load(outfile)

    for sitename in PODCASTS['websites']:
        if args.debug:
            if not sitename in debug_sites:
                continue

        site_url = PODCASTS['websites'][sitename]['home']
        PODCASTS['websites'][sitename]['function'] = PROCESS_FUNCTIONS[site_url]

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
    index_file_name = args.output
    index_file_path = PODCASTS_FOLDER + index_file_name

    template = env.get_template('template.html')

    render_sites = []

    for sitename in PODCASTS['websites']:
        if args.debug:
            if not sitename in debug_sites:
                continue

        website = PODCASTS['websites'][sitename]

        render_site = {'name': sitename,
                       'url': website['home'], 'podcasts': []}

        for name in website['programs']:
            program = website['programs'][name]
            # home = PODCASTS['broadcaster']['home']
            title = program['title']
            no_items = program['no']

            subtitle = program['subtitle']

            time_regex = r'(\d+)$'
            match = re.search(time_regex, subtitle, re.I)
            if match: # If there is episode number in subtitle, then makes a number in circle and puts it in title
                episode = int(match.group(0))

                title = number_in_cirle(episode) + " " + title

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
            # render_site['podcasts'].append(
            #     {'title': title, 'subslink': subslink, 'link': output_url})

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

            item_titles = []

            rss = rss_from_webpage(this_feed_settings, website['function'], title, item_titles)
            output_rss(rss, this_feed_settings.output_file)

            render_site['podcasts'].append(
                {'title': title, 'subslink': subslink, 'link': output_url, 'item_titles': ', '.join(item_titles)})

        render_sites.append(render_site)

    output = template.render(sites=render_sites)
    # print(output)

    with open(index_file_path, 'w', encoding='utf-8') as file:
        file.write(output)

if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as ex:
    #     print(ex)
    #     send_mail_on_error(str(ex))
