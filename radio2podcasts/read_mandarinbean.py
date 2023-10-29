
import requests
import glob
import re
import json
from pathvalidate import sanitize_filename

import time 
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 


def download_url(url, filename, driver):
    print(f'Redownload {filename} {url}')

    driver.implicitly_wait(5)

    driver.get(url) 
    time.sleep(20)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)


def read_main_site():
    URL = r"https://mandarinbean.com/all-lessons/?jsf=epro-posts&pagenum="

    for i in range(1, 79):
        url = f'{URL}{i}'
        r = requests.get(url) 
        print(f'i=')
        with open(f'MandarinBean-{i:02}.html', 'w', encoding='utf-8') as f:
            f.write(str(r.text))

        print(r.content) 

def read_html_files():
    html_files = '*.html'
    files = glob.glob(html_files)

    contents = {}

    match_pattern = r'<span class="elementor-heading-title elementor-size-default"><a href="(.+?)">(.+?)<\/a><\/span>'

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()

            matches = re.findall(match_pattern, text)

            for url, title in matches:
                if title.find('<span') >=0:
                    continue

                contents[url] = title

            # if not match_object:
            #     exit(f'Cannot find matches')
            #     continue
                
            # url = match_object.group(1)
            # title = match_object.group(2)

            # print(f'{url=} {title=}')

            pass

    print(contents)

    print(f'Count: {len(contents)}')

    with open('MandarinBeanLinks.json', 'w', encoding='utf-8') as f:
        json.dump(contents, f)

def read_all_articles():
    with open('MandarinBeanLinks.json', 'r', encoding='utf-8') as f:
        contents = json.load(f)

        # Define the Chrome webdriver options
        options = webdriver.ChromeOptions() 
        options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability

        # By default, Selenium waits for all resources to download before taking actions.
        # However, we don't need it as the page is populated with dynamically generated JavaScript code.
        options.page_load_strategy = "none"

        # Pass the defined options objects to initialize the web driver 
        driver = Chrome(options=options) 
        # Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
        driver.implicitly_wait(5)
        
        count = 0
        for url in contents:
            count+=1

            print(f'{count:03} - {contents[url]}')

            # if count > 3:
            #     break

            filename = sanitize_filename(f'Article-{contents[url]}.html')

            no_mp3 = False

            with open(filename, 'r', encoding='utf-8') as fhtml:
                text = fhtml.read()

                no_mp3 = text.find('.mp3') < 0
            
            if no_mp3:
                download_url(url, filename, driver)
    
read_all_articles()

# url=r'https://mandarinbean.com/appscription-in-the-app-era/'
# # r = requests.get(url) 
# # print(r.text)



# driver.get(url) 
# time.sleep(20)

# with open(f'Test.html', 'w', encoding='utf-8') as f:
#     f.write(driver.page_source)

# print(f'Found {driver.page_source.find(".mp3") >= 0}')



