"""This is the main program to read websites and generates corresponding podcast feeds.
"""
import collections
import os

import os.path

import boto3

from jinja2 import Environment, FileSystemLoader

from podcasts_utils import output_rss, rss_from_webpage, upload_file_s3, send_mail_on_error

from create_cover_image import create_image
from remove_marks import remove_marks
import voh_get_articles
import vov1_get_articles
import vov2_get_articles
import vov6_get_articles

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
        'VOV1': {
            'home': 'http://vov1.vov.vn/',
            'name': 'VOV1 Đài tiếng nói Việt Nam',
            'function': vov1_get_articles.get_articles_from_html,

            'programs': {
                'ccqt': {'url': 'http://vov1.vov.vn/cau-chu7yen-quoc-te-cmobile55.aspx', 'title': 'Câu chuyện quốc tế', 'subtitle': 'Câu chuyện quốc tế', 'cover': '', 'no': 7, },
                'hssk': {'url': 'http://vov1.vov.vn/ho-so-su-kien-quoc-te-cmobile33.aspx', 'title': 'Hồ sơ sự kiện', 'subtitle': 'Hồ sơ sự kiện', 'cover': '', 'no': 7, },
                'tcvov': {'url': 'http://vov1.vov.vn/thuc-cung-vov-cmobile133.aspx', 'title': 'Thức cùng VOV', 'subtitle': 'Thức cùng VOV', 'cover': '', 'no': 3, },
                'ts22h': {'url': 'http://vov1.vov.vn/thoi-su-21h30-cmobile29.aspx', 'title': 'Thời sự 21h30', 'subtitle': 'Thời sự 21h30', 'cover': '', 'no': 2, },
                'ts18h': {'url': 'http://vov1.vov.vn/thoi-su-18h-cmobile14.aspx', 'title': 'Thời sự 18h', 'subtitle': 'Thời sự 18h', 'cover': '', 'no': 2, },
                'ts12h': {'url': 'http://vov1.vov.vn/thoi-su-12h-cmobile12.aspx', 'title': 'Thời sự 12h', 'subtitle': 'Thời sự 12h', 'cover': '', 'no': 2, },
                'ts06h': {'url': 'http://vov1.vov.vn/thoi-su-6h-cmobile11.aspx', 'title': 'Thời sự 6h', 'subtitle': 'Thời sự 6h', 'cover': '', 'no': 2, },
            },
        },
        'VOV2': {
            'home': 'http://vov2.vov.vn/',
            'name': 'VOV2 Đài tiếng nói Việt Nam',
            'function': vov2_get_articles.get_articles_from_html,

            'programs': {
                '30cv': {'url': 'http://vov2.vov.vn/30-phut-cung-vov2-cmobile138.aspx', 'title': '30\' cùng VOV2', 'subtitle': '30\' cùng VOV2', 'cover': '', 'no': 3},
                'cdkt': {'url': 'http://vov2.vov.vn/chuyen-di-ky-thu-cmobile111.aspx', 'title': 'Chuyến đi kỳ thú', 'subtitle': 'Chuyến đi kỳ thú', 'cover': '', 'no': 3},
                'ggsts': {'url': 'http://vov2.vov.vn/giu-gin-su-trong-sang-cua-tieng-viet-cmobile83.aspx', 'title': 'Sự trong sáng của tiếng Việt', 'subtitle': 'Giữ gìn sự trong sáng của tiếng Việt', 'cover': '', 'no': 3},
            },
        },
        'VOV6': {
            'home': 'http://vov6.vov.vn/',
            'name': 'VOV6 Đài tiếng nói Việt Nam',
            'function': vov6_get_articles.get_articles_from_html,

            'programs': {
                'dhvn': {'url': 'http://vov6.vov.vn/diem-hen-van-nghe-cmobile158.aspx', 'title': 'Điểm hẹn văn nghệ', 'subtitle': 'Điểm hẹn văn nghệ', 'cover': '', 'no': 3},
                'dtdk': {'url': 'http://vov6.vov.vn/doc-truyen-dem-khuya-cmobile11.aspx', 'title': 'Đọc tr. đêm khuya', 'subtitle': 'Đọc truyện đêm khuya', 'cover': '', 'no': 3},
                'kchr': {'url': 'http://vov6.vov.vn/ke-chuyen-va-hat-ru-cmobile43.aspx', 'title': 'Kể chuyện và hát ru cho bé', 'subtitle': 'Kể chuyện và hát ru cho bé', 'cover': '', 'no': 3},
                'trkb': {'url': 'http://vov6.vov.vn/tim-trong-kho-bau-cmobile54.aspx', 'title': 'Tìm trong kho báu', 'subtitle': 'Tìm trong kho báu', 'cover': '', 'no': 3},
                'vntn': {'url': 'http://vov6.vov.vn/van-nghe-thieu-nhi-cmobile44.aspx', 'title': 'Văn nghệ thiếu nhi', 'subtitle': 'Văn nghệ thiếu nhi', 'cover': '', 'no': 3},
            },
        },
        'VOH': {
            'home': 'http://radio.voh.com.vn',
            'name': 'VOH Đài tiếng nói nhân dân TPHCM',
            'function': voh_get_articles.get_articles_from_html,

            'programs': {
                'sda': {'url': 'https://radio.voh.com.vn/song-dien-anh-395.html', 'title': 'Sóng điện ảnh', 'subtitle': 'Sóng điện ảnh trên VOH', 'cover': '', 'no': 5},
                'lsx': {'url': 'https://radio.voh.com.vn/lan-song-xanh-386.html', 'title': 'Làn sóng xanh', 'subtitle': 'Làn sóng xanh trên VOH', 'cover': '', 'no': 5},
                'top10': {'url': 'https://radio.voh.com.vn/top-10-ca-khuc-quoc-te-402.html', 'title': 'Top 10 ca khúc quốc tế', 'subtitle': 'Top 10 ca khúc quốc tế thứ hai hàng tuần trên VOH', 'cover': '', 'no': 5},
                'qtan': {'url': 'https://radio.voh.com.vn/qua-tang-am-nhac-394.html', 'title': 'Quà tặng âm nhạc', 'subtitle': 'Quà tặng âm nhạc trên VOH', 'cover': '', 'no': 5},
                'sgbs': {'url': 'https://radio.voh.com.vn/sai-gon-buoi-sang-590.html', 'title': 'Sài gòn buổi sáng', 'subtitle': 'Thời sự buổi sáng hàng ngày trên VOH', 'cover': '', 'no': 2},
                'sgbc': {'url': 'https://radio.voh.com.vn/sai-gon-buoi-chieu-591.html', 'title': 'Sài gòn buổi chiều', 'subtitle': 'Thời sự buổi chiều hàng ngày trên VOH', 'cover': '', 'no': 2},
                'am610': {'url': 'https://radio.voh.com.vn/thoi-su-am-610-khz-599.html', 'title': 'Thời sự AM 610 Khz', 'subtitle': 'Thời sự AM 610 Khz hàng ngày trên VOH', 'cover': '', 'no': 3},
                'csvh': {'url': 'https://radio.voh.com.vn/cua-so-van-hoc-634.html', 'title': 'Cửa sổ văn học', 'subtitle': 'Cửa sổ văn học trên VOH', 'cover': '', 'no': 3},
            },
            # 'DRT': {
            #     'home': 'http://www.drt.danang.vn/',
            #     'name': 'DRT Đài phát thanh truyền hình Đà Nẵng',
            #     'function': drt_get_articles.get_articles_from_html,

            #     'programs': {
            #         'ccct': {'url': 'http://www.drt.danang.vn/chuong_trinh-203-cau_chuyen_cuoi_tuan', 'title': 'Câu chuyện cuối tuần', 'subtitle': 'Câu chuyện cuối tuần', 'cover': 'http://www.drt.danang.vn/Uploads/DichVu/cauchuyencuoituan.jpg', },
            #     },
            # },
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
    index_file_name = 'index.html'
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

            subslink = f"https://www.subscribeonandroid.com/{AWS_PATH}/{filename}"
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
