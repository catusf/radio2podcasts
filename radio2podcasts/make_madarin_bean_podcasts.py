import glob
import re
from bs4 import BeautifulSoup
import json

ALL_TAGS = {}

def read_html_files():
    html_files = '../Article*.html'
    files = glob.glob(html_files)

    contents = {}
    tooltip_pattern = r'(.+?):<br />\s(.+?)(.*)'
    for file in files:

        # if file != 'Article-Ballet.html':
        #     continue

        with open(file, 'r', encoding='utf-8') as f:
            print(f'Processing {file}')
            text = f.read().strip()

            if not text:
                print('Empty file.')
                continue

            soup = BeautifulSoup(text, 'html.parser')

            tags = []

            cat_pattern = r'<a href="https:\/\/mandarinbean.com\/category(.+?)" class="elementor-post-info__terms-list-item">(.+?)<\/a>'

            matches = re.findall(cat_pattern, text)

            for url, tag in matches:
                tags.append(tag)

            cat_pattern = r'<a href="https:\/\/mandarinbean.com\/tag(.+?)" class="elementor-post-info__terms-list-item">(.+?)<\/a>'

            matches = re.findall(cat_pattern, text)

            for url, tag in matches:
                tags.append(tag)

            for tag in tags:
                if tag in ALL_TAGS:
                    ALL_TAGS[tag] += 1
                else:
                    ALL_TAGS[tag] = 1

            mp3_pattern = r'(traffic.libsyn.com.+?\.mp3)'

            matches = re.findall(mp3_pattern, text)

            if matches:
                mp3_url = 'https://' + matches[0].replace('\\', '')
            else:
                mp3_url = ''

            title_en_pattern = r'<title>(.+?) - Mandarin Bean</title>'

            matches = re.search(title_en_pattern, text, re.MULTILINE)

            title_en = matches.group(1)

            title_zh_pattern = r'<h2 class="elementor-heading-title elementor-size-default"><span class="si">(.+?)</span>'

            matches = re.search(title_zh_pattern, text)

            title_zh = matches.group(1)

            html = soup.find(class_='elementor-widget-theme-post-content')

            paragraphs = html.find_all('p')

            chinese_text = ''

            for p in paragraphs:
                chinese_text += p.text + '\n'

            abbr = html.find_all('abbr')

            chinese = []
            english = []
            pinyin = []
            levels = []

            for a in abbr:
                
                tooltip = a.get('title')

                m = re.search(r'<br />(.*)', tooltip)

                chinese.append(a.span.text)
                pinyin.append(a.rt.text.replace(u'\xa0', ''))
                eng_text = m.group(1).strip()
                parenthesis = eng_text.find('(')

                if parenthesis < 0: # No level
                    english.append(eng_text)
                else:
                    english.append(eng_text[:parenthesis-1])
                    levels.append(eng_text[parenthesis+1:-1])

                pass
            
            # print(chinese)
            # print(english)
            # print(levels)
            # print(pinyin)

            contents[file] = {'tags': tags, 'mp3': mp3_url, 'title_en': title_en, 'title_zh': title_zh, 'chinese': chinese, 'english': english, 'pinyin': pinyin, 'levels': levels, 'text': chinese_text}

    print(f'Processed {len(files)}')
    print(ALL_TAGS)

    with open('all_meta.json', 'w', encoding='utf-8') as f:
        json.dump(contents, f)

    # print(contents)

read_html_files()

