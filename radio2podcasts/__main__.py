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

import datetime
import pytz

from podcasts_utils import output_rss, rss_from_webpage, number_in_cirle, send_mail_on_error

from create_cover_image import create_image
from remove_marks import remove_marks
import get_mandarin_bean
import get_voh_com_vn
import get_vov1
import get_vov2
import get_vov6
import get_drt_danang_vn
import get_vnexpress_vn
import get_vovlive
import get_rfi_vi
import get_ppud
import get_vovlive_sachnoi
import get_archive_org

DE = True  # False

CWD = os.getcwd()

DEST_URL = 'catusf.github.io/radio2podcasts'

PODCASTS = {}

PODCASTS_FOLDER = 'site/'

# Maps site urls to their processing functions
PROCESS_FUNCTIONS = {
    'https://https://mandarinbean.com/': get_mandarin_bean.get_articles_from_html,
    'http://vov1.vov.vn/': get_vov1.get_articles_from_html,
    'http://vov2.vov.vn/': get_vov2.get_articles_from_html,
    'http://vov6.vov.vn/': get_vov6.get_articles_from_html,
    'http://radio.voh.com.vn': get_voh_com_vn.get_articles_from_html,
    'http://www.drt.danang.vn/': get_drt_danang_vn.get_articles_from_html,
    'https://vnexpress.net/podcast': get_vnexpress_vn.get_articles_from_html,
    'https://vovlive.vn/': get_vovlive.get_articles_from_html,
    'https://www.rfi.fr/vi/': get_rfi_vi.get_articles_from_html,
    'https://phatphapungdung.com/sach-noi/': get_ppud.get_articles_from_html,
    'https://vovlive.vn/sach-noi/': get_vovlive_sachnoi.get_articles_from_html,
    'https://archive.org/': get_archive_org.get_articles_from_html,
}

def cleanup_url(url):
    """
    Preprocess url for special cases.
    """

    newurl = re.sub(r"(archive.org/)(details)(/)", r'\1embed\3', url)

    return newurl


def main():
    """
    Entry point of the module
    :return: error code is issue occurs
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input', help='Name of JSON input file for podcast feed', type=str, required=True)
    parser.add_argument(
        '-o', '--output', help='Name of HTML output file containing description of all podcasts', type=str, required=True)
    parser.add_argument(
        '-d', '--debug', help='Debug mode True/False', default=False, type=bool)
    args = parser.parse_args()

    global PODCASTS

    # if args.debug:
    #     debug_sites = {'RFI',}

    if not os.path.exists(PODCASTS_FOLDER):
        os.makedirs(PODCASTS_FOLDER)

    with open(args.input, 'r', encoding='utf-8') as outfile:
        PODCASTS = json.load(outfile)

    with open('config.json', 'r', encoding='utf-8') as outfile:
        PODCASTS_CONFIG = json.load(outfile)

    for sitename in PODCASTS['websites']:
        # if args.debug:
        #     if not sitename in debug_sites:
        #         continue

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
        # if args.debug:
        #     if not sitename in debug_sites:
        #         continue

        website = PODCASTS['websites'][sitename]

        vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.datetime.now().astimezone(vt_tz).isoformat()

        render_site = {'name': sitename,
                       'url': website['home'], 
                       'podcasts': []}

        for program in website['programs']:
            title = program['title']
            no_items = program['no']
            subtitle = program['subtitle']

            time_regex = r'(\d+)$'
            match = re.search(time_regex, subtitle, re.I)
            if match:  # If there is episode number in subtitle, then makes a number in circle and puts it in title
                episode = int(match.group(0))
                title = number_in_cirle(episode) + " " + title

            url = cleanup_url(program['url'])
            bare_title = remove_marks(title)
            base_name = f"{sitename}-{bare_title}"
            filename = f"{base_name}{PODCASTS_CONFIG['podcasts']['podcast_ext']}"
            output_file = PODCASTS_FOLDER + filename
            host = PODCASTS_CONFIG['podcasts']['host']
            output_url = host + filename
            image_file = f"{base_name}.png"
            image_path = PODCASTS_FOLDER + image_file
            cover_url = host + image_file

            subslink = f"https://www.subscribeonandroid.com/{DEST_URL}/{filename}"

            print(output_file)

            create_image(sitename, title.upper(), image_path)

            this_feed_settings = feed_settings(
                source_page_url=url,
                no_items=no_items,
                container_CSS_selector='h4.title-header',
                output_file=output_file,
                output_url=output_url,
                title=title,
                subtitle=subtitle,
                author={'name': PODCASTS_CONFIG['podcasts']['name'],
                        'email': PODCASTS_CONFIG['podcasts']['email']},
                img_url=cover_url,
                language='vi',
                copyright=PODCASTS_CONFIG['podcasts']['name'],
            )

            item_titles = []

            rss = rss_from_webpage(this_feed_settings, website['function'], title, item_titles)
            output_rss(rss, this_feed_settings.output_file)

            render_site['podcasts'].append(
                {'title': title, 'subslink': subslink, 'link': output_url, 'item_titles': ' | '.join(item_titles).strip()})

        render_sites.append(render_site)

    output = template.render(sites=render_sites, date=now)

    with open(index_file_path, 'w', encoding='utf-8') as file:
        file.write(output)


if __name__ == "__main__":
    main()
    try:
        main()
    except Exception as ex:
        print(ex)
        send_mail_on_error(str(ex))
