"""This module contains utility functions for podcast generation.
"""
import datetime
import os
import sys
import linecache
import smtplib
from email.message import EmailMessage

import requests

from bs4 import BeautifulSoup
import pytz

from podgen import Podcast, Person, Media, Category #, htmlencode

# from botocore.exceptions import ClientError

EMAIL_SENDER_ENV = 'R2P_EMAIL_SENDER'
EMAIL_RECIPIENT_ENV = 'R2P_EMAIL_RECIPIENT'
EMAIL_PASSWORD_ENV = 'R2P_EMAIL_PASSWORD'

def exception_info():
    """
    Gets details of where exception occurs
    """
    exc_type, exc_obj, tbtype = sys.exc_info()
    frame = tbtype.tb_frame
    lineno = tbtype.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, frame.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def send_mail_on_error(error):
    """Send error message by email (Gmail specifically)

    Args:
        error ([string]): Description of the error (exception)
    """
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ.get('R2P_EMAIL_SENDER')
    recepient_email = os.environ.get('R2P_EMAIL_RECIPIENT')
    password = os.environ.get('R2P_EMAIL_PASSWORD')

    if (not sender_email) or (not recepient_email) or (not password):
        print('Email environments not set.')
        return

    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    time = datetime.datetime.now().astimezone(vt_tz)
    exception = exception_info()
    try:
        msg = EmailMessage()
        msg.set_content(f'We found this error when creating podcasts on Heroku: {error}.\nTime: {time}\n\n{exception}')

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

def get_true_url(url):
    """
    Gets true url of file, which is redirected destination.
    """
    response = requests.head(url)
    true_url = response.headers['Location'] # Detects redirection and get destination's url

    return true_url


def output_rss(rss, filename):
    """
    Sends RSS to a file, and stdout if debugging
    :param feed_xml: valid RSS XML
    :return: none
    """

    rss.rss_file(filename)


def rss_from_webpage(feed_settings, get_articles_from_html, podcast_title, item_titles):
    """
    TODO docstring
    :param feed_settings:
    :return:
    """
    print(f'Processing: {podcast_title}')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

    source_page_html = requests.get(feed_settings.source_page_url, headers=headers).content
    soup = BeautifulSoup(source_page_html, 'html.parser')

    container_html = soup  # soup.select(feed_settings.container_CSS_selector)
    articles = get_articles_from_html(
        container_html, feed_settings.source_page_url, feed_settings.no_items, feed_settings.title, item_titles)
    rss = generate_rss_from_articles(feed_settings, articles)
    return rss


def generate_rss_from_articles(feed_settings, articles):
    """
    Creates a FeedGenerator feed from a set of feed_entries.

    :param feed_settings: a feed_settings object containing
    :param articles:
    :return:
    """
    # Initialize the feed
    podcast = Podcast()
    podcast.name = feed_settings.title
    author = Person(feed_settings.author['name'], feed_settings.author['email'])
    podcast.authors.append(author)
    podcast.website = feed_settings.source_page_url
    podcast.copyright = feed_settings.copyright
    podcast.description = feed_settings.subtitle
    podcast.summary = feed_settings.subtitle
    podcast.subtitle = feed_settings.subtitle
    podcast.language = 'vi'
    podcast.feed_url = feed_settings.output_url
    podcast.image = feed_settings.img_url
    podcast.category = Category('Music', 'Music Commentary')
    podcast.explicit = False
    # p.complete = False
    # p.new_feed_url = 'http://example.com/new-feed.rss'
    podcast.owner = author
    # p.xslt = "http://example.com/stylesheet.xsl"

    vt_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    pastdate = datetime.datetime(2000, 1, 1, 0, 0).astimezone(vt_tz)
    # podcast.last_updated = datetime.datetime.now(vt_tz)

    for article in articles:
        episode = podcast.add_episode()
        episode.id = article.link
        episode.title = article.title
        episode.summary = article.description
        episode.link = article.link
        # episode.authors = [Person('Lars Kiesow', 'lkiesow@uos.de')]
        episode.publication_date = article.pub_date
        pastdate = max(pastdate, article.pub_date)
        # episode.media = Media.create_from_server_response(article.media, size=None, duration=None)
        episode.media = Media(article.media, size=None, duration=None, type=article.type)

    podcast.last_updated = pastdate
    podcast.publication_date = pastdate

    return podcast


def number_in_cirle(num):
    '''
    Gets the Unicode character coresponding to a number
    '''
    if num < 0 or num > 20:
        print(f'Number {num} too big for number-in-circle. Use original')
        return str(num)
        # raise ValueError

    return chr(9311+num)
