"""This is the main program to read websites and generates corresponding podcast feeds for Phatphapungdung Audio files.
"""
import collections
import os

import os.path

import boto3

from jinja2 import Environment, FileSystemLoader

from podcasts_utils import output_rss, rss_from_webpage, number_in_cirle, upload_file_s3, send_mail_on_error

from create_cover_image import create_image
from remove_marks import remove_marks
import ppud_get_articles
# import drt_get_articles

XML_EXRA_ARGS = {'ContentType': 'application/xml',
                 'ContentDisposition': 'inline', 'ACL': 'public-read'}
HTM_EXRA_ARGS = {'ContentType': 'text/html',
                 'ContentDisposition': 'inline', 'ACL': 'public-read'}
IMG_EXRA_ARGS = {'ContentType': 'image/png', 'ACL': 'public-read'}


CWD = os.getcwd()


PODCASTS = {
    'podcasts': {
        'host': 'https://radio2podcasts.s3-ap-southeast-1.amazonaws.com/',
        'bucket_name': 'radio2podcasts',  # AWS bucket name
        'podcast_ext': '.xml',
        'name': 'catusf',
        'email': 'catus.phan@gmail.com',
    },
    'websites': {
        'PPUD': {
            'home': 'https://phatphapungdung.com/sach-noi/',
            'name': 'Sách nói - Phật pháp ứng dụng',
            'function': ppud_get_articles.get_articles_from_html,

            'programs': {
                'tct': {'url': 'https://phatphapungdung.com/sach-noi/sach-noi-tong-hop/truyen-co-tich', 'title':  'Truyện cổ tích', 'subtitle': 'Trang 1', 'cover': '', 'no': 100},

                'hg1': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon', 'title':  number_in_cirle(1) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 1', 'cover': '', 'no': 100},
                'hg2': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/2', 'title':  number_in_cirle(2) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 2', 'cover': '', 'no': 200},
                'hg3': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/3', 'title':  number_in_cirle(3) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 3', 'cover': '', 'no': 300},
                'hg4': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/4', 'title':  number_in_cirle(4) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 4', 'cover': '', 'no': 400},
                'hg5': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/5', 'title':  number_in_cirle(5) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 5', 'cover': '', 'no': 500},
                'hg6': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/6', 'title':  number_in_cirle(6) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 6', 'cover': '', 'no': 600},
                'hg7': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/7', 'title':  number_in_cirle(7) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 7', 'cover': '', 'no': 700},
                'hg8': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/8', 'title':  number_in_cirle(8) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 8', 'cover': '', 'no': 800},
                'hg9': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/9', 'title':  number_in_cirle(9) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 9', 'cover': '', 'no': 900},
                'hg10': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/10', 'title':  number_in_cirle(10) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 10', 'cover': '', 'no': 1000},
                'hg11': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/11', 'title':  number_in_cirle(11) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 11', 'cover': '', 'no': 1100},
                'hg12': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/12', 'title':  number_in_cirle(12) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 12', 'cover': '', 'no': 1200},
                'hg13': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/13', 'title':  number_in_cirle(13) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 13', 'cover': '', 'no': 1300},
                'hg14': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/14', 'title':  number_in_cirle(14) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 14', 'cover': '', 'no': 1400},
                'hg15': {'url': 'https://phatphapungdung.com/sach-noi/hat-giong-tam-hon/page/15', 'title':  number_in_cirle(15) + ' Hạt giống tâm hồn', 'subtitle': 'Trang 154', 'cover': '', 'no': 15400},

                'tt1': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio', 'title':  number_in_cirle(1) + ' Tiểu thuyết', 'subtitle': 'Trang 1', 'cover': '', 'no': 100},
                'tt2': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/2', 'title':  number_in_cirle(2) + ' Tiểu thuyết', 'subtitle': 'Trang 2', 'cover': '', 'no': 200},
                'tt3': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/3', 'title':  number_in_cirle(3) + ' Tiểu thuyết', 'subtitle': 'Trang 3', 'cover': '', 'no': 300},
                'tt4': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/4', 'title':  number_in_cirle(4) + ' Tiểu thuyết', 'subtitle': 'Trang 4', 'cover': '', 'no': 400},
                'tt5': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/5', 'title':  number_in_cirle(5) + ' Tiểu thuyết', 'subtitle': 'Trang 5', 'cover': '', 'no': 500},
                'tt6': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/6', 'title':  number_in_cirle(6) + ' Tiểu thuyết', 'subtitle': 'Trang 6', 'cover': '', 'no': 600},
                'tt7': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/7', 'title':  number_in_cirle(7) + ' Tiểu thuyết', 'subtitle': 'Trang 7', 'cover': '', 'no': 700},
                'tt8': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/8', 'title':  number_in_cirle(8) + ' Tiểu thuyết', 'subtitle': 'Trang 8', 'cover': '', 'no': 800},
                'tt9': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/9', 'title':  number_in_cirle(9) + ' Tiểu thuyết', 'subtitle': 'Trang 9', 'cover': '', 'no': 900},
                'tt10': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/10', 'title':  number_in_cirle(10) + ' Tiểu thuyết', 'subtitle': 'Trang 10', 'cover': '', 'no': 1000},
                'tt11': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/11', 'title':  number_in_cirle(11) + ' Tiểu thuyết', 'subtitle': 'Trang 11', 'cover': '', 'no': 1100},
                'tt12': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/12', 'title':  number_in_cirle(12) + ' Tiểu thuyết', 'subtitle': 'Trang 12', 'cover': '', 'no': 1200},
                'tt13': {'url': 'https://phatphapungdung.com/sach-noi/tieu-thuyet-audio/page/13', 'title':  number_in_cirle(13) + ' Tiểu thuyết', 'subtitle': 'Trang 13', 'cover': '', 'no': 1300},

                'stn1': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi', 'title': number_in_cirle(1) + ' Sách thiếu nhi', 'subtitle': 'Trang 1', 'cover': '', 'no': 100},
                'stn2': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/2', 'title': number_in_cirle(2) + ' Sách thiếu nhi', 'subtitle': 'Trang 2', 'cover': '', 'no': 100},
                'stn3': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/3', 'title': number_in_cirle(3) + ' Sách thiếu nhi', 'subtitle': 'Trang 3', 'cover': '', 'no': 100},
                'stn4': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/4', 'title': number_in_cirle(4) + ' Sách thiếu nhi', 'subtitle': 'Trang 4', 'cover': '', 'no': 100},
                'stn5': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/5', 'title': number_in_cirle(5) + ' Sách thiếu nhi', 'subtitle': 'Trang 5', 'cover': '', 'no': 100},
                'stn6': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/6', 'title': number_in_cirle(6) + ' Sách thiếu nhi', 'subtitle': 'Trang 6', 'cover': '', 'no': 100},
                'stn7': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/7', 'title': number_in_cirle(7) + ' Sách thiếu nhi', 'subtitle': 'Trang 7', 'cover': '', 'no': 100},
                'stn8': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/8', 'title': number_in_cirle(8) + ' Sách thiếu nhi', 'subtitle': 'Trang 8', 'cover': '', 'no': 100},
                'stn9': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/9', 'title': number_in_cirle(9) + ' Sách thiếu nhi', 'subtitle': 'Trang 9', 'cover': '', 'no': 100},
                'stn10': {'url': 'https://phatphapungdung.com/sach-noi/sach-thieu-nhi/page/10', 'title': number_in_cirle(10) + ' Sách thiếu nhi', 'subtitle': 'Trang 10', 'cover': '', 'no': 100},

                'td1': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/', 'title':  number_in_cirle(1) + ' Truyện dài', 'subtitle': 'Trang 1', 'cover': '', 'no': 100},
                'td2': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/2', 'title': number_in_cirle(2) + ' Truyện dài', 'subtitle': 'Trang 2', 'cover': '', 'no': 100},
                'td3': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/3', 'title': number_in_cirle(3) + ' Truyện dài', 'subtitle': 'Trang 3', 'cover': '', 'no': 100},
                'td4': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/4', 'title': number_in_cirle(4) + ' Truyện dài', 'subtitle': 'Trang 4', 'cover': '', 'no': 100},
                'td5': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/5', 'title': number_in_cirle(5) + ' Truyện dài', 'subtitle': 'Trang 5', 'cover': '', 'no': 100},
                'td6': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/6', 'title': number_in_cirle(6) + ' Truyện dài', 'subtitle': 'Trang 6', 'cover': '', 'no': 100},
                'td7': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/7', 'title': number_in_cirle(7) + ' Truyện dài', 'subtitle': 'Trang 7', 'cover': '', 'no': 100},
                'td8': {'url': 'https://phatphapungdung.com/sach-noi/truyen-dai-audio/page/8', 'title': number_in_cirle(8) + ' Truyện dài', 'subtitle': 'Trang 8', 'cover': '', 'no': 100},
            },
        },
    }
}

PODCASTS_FOLDER = 'podcasts\\'

AWS_PATH = 'radio2podcasts.s3-ap-southeast-1.amazonaws.com'

def main():
    """
    TODO docstring
    :return:
    """

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
    index_file_name = 'index-ppud.html'
    index_file_path = PODCASTS_FOLDER + index_file_name

    template = env.get_template('template.html')

    render_sites = []

    # S3 Client to upload file to desination bucket
    s3_client = boto3.client('s3')
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

            subslink = f"https://www.subscribeonandroid.com/radio2podcasts.s3-ap-southeast-1.amazonaws.com/{filename}"
            render_site['podcasts'].append(
                {'title': title, 'subslink': subslink, 'link': output_url})

            print(output_file)

            create_image(sitename, title.upper(), image_path, title_height=900)
            done = upload_file_s3(s3_client,
                                  os.path.join(CWD, image_path), PODCASTS['podcasts']['bucket_name'], IMG_EXRA_ARGS, image_file)

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

            rss = rss_from_webpage(this_feed_settings, website['function'])
            output_rss(rss, this_feed_settings.output_file)

            done = upload_file_s3(s3_client,
                                  os.path.join(CWD, output_file),
                                  PODCASTS['podcasts']['bucket_name'], XML_EXRA_ARGS, filename)
            print(f'Uploaded {output_file}: {done}')

        render_sites.append(render_site)

    output = template.render(sites=render_sites)
    # print(output)

    with open(index_file_path, 'w', encoding='utf-8') as file:
        file.write(output)

    done = upload_file_s3(s3_client,
                          os.path.join(CWD, index_file_path), PODCASTS['podcasts']['bucket_name'], HTM_EXRA_ARGS, index_file_name)
    print(f'{done} uploaded {index_file_name} to https://{AWS_PATH}/{index_file_name} ')


DE = False  # True

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        send_mail_on_error(str(ex))

