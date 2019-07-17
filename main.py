#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

from bs4 import BeautifulSoup
from icrawler.builtin import GoogleImageCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Firefox
import codecs
import datetime
import os
import re
import requests
import time
import urllib.parse
import urllib.request


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())


# 検索パラメータ
AGE_MIN = 22
AGE_MAX = 24


# 定数
DATA_FILEPATH = os.path.join(
    currentdirectory, 'dat_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

PHOTO_DIRPATH = os.path.join(currentdirectory, 'img')

PERSONS_PER_PAGE = 20
WAITING_TIME = 10000

# URI
baseUris = [
    # https://www.talent-databank.co.jp/guideline/index.html
    'https://www.talent-databank.co.jp',
    'https://talemecasting-next.com'  # https://talemecasting-next.com/agreement
]
targetUris = [
    'https://www.talent-databank.co.jp/',
    'https://talemecasting-next.com/talent?sex_flg%5B%5D=1&genre%5B%5D=15&age_min=' +
    str(AGE_MIN)+'&age_max='+str(AGE_MAX)
]

# # カテゴリ毎に、取得するページ数
# MAX_PAGE = [
#     20,
#     20
# ]


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def collect():
    result_names = []

    if os.path.exists(PHOTO_DIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(PHOTO_DIRPATH, PHOTO_DIRPATH + '_' + nowstr + '.bak')
    os.makedirs(PHOTO_DIRPATH, exist_ok=True)

    with open(DATA_FILEPATH, 'a', encoding='utf-8') as datafile:
        with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
            print('Start: {}'.format(
                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
            binary = FirefoxBinary(
                'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
            profile = FirefoxProfile(
                'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\hqterean.default')
            fox = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary,
                                    executable_path='C:\\geckodriver\\geckodriver.exe')
            fox.set_page_load_timeout(6000)
            try:
                fox.set_window_size(1280, 720)

                # talent-databank
                baseUri = baseUris[0]
                targetUri = targetUris[0]
                print('\tbaseUri: {} {}'.format(
                    baseUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                print('\ttargetUri: {} {}'.format(
                    targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                # 検索条件

                fox.get(targetUri)
                time.sleep(1)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.XPATH, '//body')))
                print('body', file=logfile, flush=True)

                # 「女性」
                clickSelector(fox, 'input[type="checkbox"][value="female"]')

                #  「タレント・俳優・女優」（最初の要素）の「もっと詳しく」
                clickLink(fox, 'もっと詳しく')

                # 「女優」
                clickSelector(fox, 'input[type="checkbox"][value=":女優"]')

                # 年齢
                clearAndSendKeys(fox, 'age_min', str(AGE_MIN))
                clearAndSendKeys(fox, 'age_max', str(AGE_MAX))

                # 「すべての条件を併せて検索」
                clickSelector(
                    fox, 'input[type="image"][src="img/top_search_btn.jpg"]')

                # 検索結果1ページ目
                time.sleep(1)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.XPATH, '//body')))
                print('body', file=logfile, flush=True)

                source = fox.page_source
                bs = BeautifulSoup(source, 'lxml')
                print('bs', file=logfile, flush=True)
                # print(source, file=logfile, flush=True)

                searchnavi_total = bs.find_all(
                    'span', class_=re.compile('searchnavi_total'))
                if len(searchnavi_total) == 0:
                    return
                count_all = int(searchnavi_total[0].text)
                last_page = -((-1 * count_all) // PERSONS_PER_PAGE)  # 切り上げ

                for i in range(last_page):
                    print('\tpage: {} {} {} {}'.format(
                        i, last_page, count_all, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                    tables = bs.find_all(
                        'table', id=re.compile('search-results'))
                    if len(tables) > 0:
                        table = tables[0]
                        trs = table.find_all('tr')
                        if len(trs) > 0:
                            for tr in trs:
                                name = ''
                                profile_page = ''

                                try:
                                    # 個人
                                    links = tr.find_all(
                                        'a', class_=re.compile('talent'))
                                    if len(links) > 0:
                                        link = links[0]
                                        name = str(link.text)
                                        result_names.append(name)

                                        profile_page = baseUri + \
                                            '/search/' + link.get('href')

                                        # データファイルに出力
                                        print('{}\t\t{}'.format(name, profile_page),
                                              file=datafile, flush=True)

                                        try:
                                            imgs = tr.find_all('img')
                                            if len(imgs) > 0:
                                                download_img(
                                                    baseUri + imgs[0].get('src'), name)
                                        except:
                                            pass
                                except Exception as e:
                                    print(e, file=logfile, flush=True)

                    # 次のページに行く
                    try:
                        clickLink(fox, '次のページ')

                        time.sleep(1)
                        WebDriverWait(fox, WAITING_TIME).until(
                            EC.presence_of_element_located((By.XPATH, '//body')))
                        print('body', file=logfile, flush=True)

                        source = fox.page_source
                        bs = BeautifulSoup(source, 'lxml')
                        print('bs', file=logfile, flush=True)
                    except:
                        break

                # talemecasting-next
                baseUri = baseUris[1]
                targetUri = targetUris[1]
                print('\tbaseUri: {} {}'.format(
                    baseUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                print('\ttargetUri: {} {}'.format(
                    targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                fox.get(targetUri)
                time.sleep(1)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.XPATH, '//body')))
                print('body', file=logfile, flush=True)

                source = fox.page_source
                bs = BeautifulSoup(source, 'lxml')
                print('bs', file=logfile, flush=True)
                # print(source, file=logfile, flush=True)

                total = bs.find_all(
                    'span', class_=re.compile('required'))
                if len(total) == 0:
                    return
                count_all = int(total[0].text)
                last_page = -((-1 * count_all) // PERSONS_PER_PAGE)  # 切り上げ

                for i in range(last_page):
                    print('\tpage: {} {} {} {}'.format(
                        i, last_page, count_all, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                    uls = bs.find_all('ul', id=re.compile('display-image'))
                    if len(uls) > 0:
                        ul = uls[0]
                        lis = ul.find_all('li')
                        if len(lis) > 0:
                            for li in lis:
                                name = ''
                                profile_page = ''

                                try:
                                    # 個人
                                    divs = li.find_all(
                                        'div', class_='talent-head-img')
                                    if len(divs) > 0:
                                        div = divs[0]
                                        imgs = div.find_all('img')
                                        if len(imgs) > 0:
                                            img = imgs[0]
                                            name = str(img.get(
                                                'alt')).replace('　', ' ')
                                            result_names.append(name)
                                            download_img(img.get('src'), name)

                                            links = li.find_all('a')
                                            if len(links) > 0:
                                                link = links[0]
                                                profile_page = baseUri + \
                                                    link.get('href')

                                                # データファイルに出力
                                                print('{}\t\t{}'.format(name, profile_page),
                                                      file=datafile, flush=True)

                                except Exception as e:
                                    print(e, file=logfile, flush=True)

                    # 次のページに行く
                    try:
                        clickClassName(fox, 'next')

                        time.sleep(1)
                        WebDriverWait(fox, WAITING_TIME).until(
                            EC.presence_of_element_located((By.XPATH, '//body')))
                        print('body', file=logfile, flush=True)

                        source = fox.page_source
                        bs = BeautifulSoup(source, 'lxml')
                        print('bs', file=logfile, flush=True)
                    except:
                        break

            except Exception as e:
                print(e, file=logfile, flush=True)
            finally:
                # 終了時の後片付け
                try:
                    fox.close()
                    fox.quit()
                    print('Done: {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                except:
                    pass
    return result_names


def search(names):
    names = list(set(names))
    for name in names:
        profile_dirpath = os.path.join(PHOTO_DIRPATH, name)
        os.makedirs(profile_dirpath, exist_ok=True)
        crawler = GoogleImageCrawler(storage={"root_dir": profile_dirpath})
        crawler.crawl(keyword=name, max_num=10)


def clickClassName(fox, className):
    fox.find_element_by_class_name(className).click()


def clickId(fox, id):
    fox.find_element_by_id(id).click()


def clickLink(fox, text):
    fox.find_element_by_link_text(text).click()


def clickName(fox, name):
    fox.find_element_by_name(name).click()


def clickSelector(fox, selector):
    fox.find_element_by_css_selector(selector).click()


def clickXpath(fox, xpath):
    fox.find_element_by_xpath(xpath).click()


def clearAndSendKeys(fox, name, text):
    fox.find_element_by_name(name).clear()
    fox.find_element_by_name(name).send_keys(text)


def getFilename(url):
    basename = os.path.basename(str(url))
    basename = basename.split('?')[0] if ('?' in basename) else basename
    return basename


def download_img(url, filename_prefix):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(os.path.join(PHOTO_DIRPATH, filename_prefix + '_' + getFilename(url)), 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    names = collect()
    search(names)
