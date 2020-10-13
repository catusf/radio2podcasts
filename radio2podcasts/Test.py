'''Test creating cover images
'''
# from create_cover_image import create_image
# from os import system

# out = 'RADIO.png'
# create_image('VOH', 'Đọc truyện và hát ru cho bé ', out, title_height=800, desc_height=500)
# system(f'start {out}')
import smtplib
import datetime
import os
from email.message import EmailMessage
import pytz

EMAIL_SENDER_ENV = 'R2P_EMAIL_SENDER'
EMAIL_RECIPIENT_ENV = 'R2P_EMAIL_RECIPIENT'
EMAIL_PASSWORD_ENV = 'R2P_EMAIL_PASSWORD'

def send_mail_on_error(error):
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ.get('R2P_EMAIL_SENDER')
    recepient_email = os.environ.get('R2P_EMAIL_RECIPIENT')
    password = os.environ.get('R2P_EMAIL_PASSWORD')

    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    time = datetime.datetime.now().astimezone(vt_tz)

    try:
        msg = EmailMessage()
        msg.set_content(f'We found this error when creating podcasts on Heroku: {error}.\nTime: {time}')

        msg['From'] = sender_email
        msg['To'] = recepient_email
        msg['Subject'] = f'[Radio2Podcasts] Error found: {error}'

        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()

        print(f'Email sent to {recepient_email} with message: {error}')

    except Exception as ex:
        print('**** ERROR SENDING EMAIL:', ex)

send_mail_on_error("I'm hungry.")

'''
import json

from bs4 import BeautifulSoup

import requests

def findEpisodes(link):
    # link =  'https://phatphapungdung.com/sach-noi/vua-co-lau-pham-minh-thao-bien-soan-178912.html'

    ret = requests.get(link)
    soup = BeautifulSoup(ret.content, 'html.parser')

    media = soup.find('div', class_='fp-playlist-external')
    title = soup.find('title').text
    text_to_remove = ' - Sách Nói Online Hay'
    title = title.replace(text_to_remove, '')
    print(title)
    items = media.findAll('a')
    print(f'Length {len(items)}')
    episodes = []

    for n, i in enumerate(items):
        encoded = i['data-item']
        decoded = bytes(encoded, 'utf-8').decode('unicode-escape').replace('\\', '')
        decoded_json = json.loads(decoded)
        subtitle = decoded_json['fv_title']
        url = decoded_json['sources'][0]['src']
        mime_type = decoded_json['sources'][0]['type']

        print('    ', decoded_json['fv_title'])
        print('    ', decoded_json['sources'][0]['src'])
        print('    ', decoded_json['sources'][0]['type'])

        etitle = f"{n} {title} - {subtitle}"
        episodes.append({'episode_title': etitle, 'media':url, 'mime':mime_type,})

    return episodes

link =  'https://phatphapungdung.com/sach-noi/vua-co-lau-pham-minh-thao-bien-soan-178912.html'
results = findEpisodes(link)
print(f"Episodes: {len(results)}")

print(results)
'''
    # print(decoded)

""" Jinja template with Bootstrap

from jinja2 import Environment, FileSystemLoader

import os
import os.path
print(os.getcwd())

file_loader = FileSystemLoader(os.path.join(os.getcwd(), 'templates'))
env = Environment(loader=file_loader)

template = env.get_template('template.html')

sites = [
    {'name': 'VOH',
     'url': 'http://voh.com.vn',
     'podcasts': [
             {'title': 'Sóng điện ảnh', 'subslink': 'https://subs1.com',
                 'link': 'https://link.com', },
             {'title': 'Yêu âm nhạc', 'subslink': 'https://subs2.com',
                 'link': 'https://link.com', },
     ]
     },
    {'name': 'VOV2',
     'url': 'http://vov2.com.vn',
     'podcasts': [
             {'title': 'Đọc truyện và hát ru', 'subslink': 'https://vov21.com',
                 'link': 'https://link.com', },
             {'title': 'Chuyện cho thiếu nhi', 'subslink': 'https://subs2.com',
                 'link': 'https://link.com', },
     ],
     }
]

output = template.render(sites=sites)
print(output)

with open('./podcasts/index.html', 'w', encoding='utf-8') as file:
    file.write(output)
"""