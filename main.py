# Copyright (c) 2020 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

# pip install icrawler
# pip install opencv-python opencv-contrib-python
# pip install selenium


from bs4 import BeautifulSoup
from icrawler.builtin import BingImageCrawler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Firefox
import codecs
import cv2
import datetime
import numpy as np
import os
import re
import requests
import tempfile
import time
import urllib.parse
import urllib.request


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())


# 検索パラメータ
AGE_MIN = 18
AGE_MAX = 30


# 定数
DATA_FILEPATH = os.path.join(
    currentdirectory, 'data', 'dat_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'data', 'log_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

HAARCASCADE_PATH = 'sources/data/haarcascades/haarcascade_frontalface_default.xml'
faceCascadeClassifier = cv2.CascadeClassifier(HAARCASCADE_PATH)

PHOTO_DIRPATH = os.path.join(currentdirectory, 'data', 'img')
TEMP_DIRPATH = os.path.join(currentdirectory, 'data', 'temp')

PERSONS_PER_PAGE = 20
WAITING_TIME = 2000
WAITING_TIME_SEARCH = 10

# URI
baseUris = [
    # https://www.talent-databank.co.jp/guideline/index.html
    'https://www.talent-databank.co.jp',
    'https://talemecasting-next.com'  # https://talemecasting-next.com/agreement
]
targetUris = [
    'https://www.talent-databank.co.jp/',
    'https://talemecasting-next.com/talent?sex_flg%5B%5D=1&genre%5B%5D=11&genre%5B%5D=12&genre%5B%5D=13&genre%5B%5D=15&genre%5B%5D=16&genre%5B%5D=17&genre%5B%5D=19&genre%5B%5D=20&age_min=' +
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


def imread2(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def imwrite2(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def collect():
    result_names = []

    os.makedirs(os.path.join(currentdirectory, 'data'), exist_ok=True)

    if os.path.exists(PHOTO_DIRPATH):
        nowstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        os.rename(PHOTO_DIRPATH, PHOTO_DIRPATH + '_' + nowstr + '.bak')
    os.makedirs(PHOTO_DIRPATH, exist_ok=True)

    with open(DATA_FILEPATH, 'a', encoding='utf-8') as datafile:
        with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
            print('\tcollect() Start: {}'.format(
                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
            binary = FirefoxBinary(
                'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
            profile = FirefoxProfile(
                'C:\\Users\\y\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\mv060idd.default')
            fox = webdriver.Firefox(
                firefox_profile=profile,
                firefox_binary=binary,
                executable_path='C:\\geckodriver\\geckodriver.exe'
            )
            fox.set_page_load_timeout(6000)
            try:
                fox.set_window_size(1280, 720)

                # talent-databank
                baseUri = baseUris[0]
                targetUri = targetUris[0]
                print('\tcollect() baseUri: {} {}'.format(
                    baseUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                print('\tcollect() targetUri: {} {}'.format(
                    targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                # 検索条件

                fox.get(targetUri)
                time.sleep(1)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.XPATH, '//body')))
                print('\tcollect() body', file=logfile, flush=True)

                # 「女性」
                clickSelector(fox, 'input[type="checkbox"][value="female"]')

                # #  「タレント・俳優・女優」（最初の要素）の「もっと詳しく」
                # clickLink(fox, 'もっと詳しく')

                # # 「女優」
                # clickSelector(fox, 'input[type="checkbox"][value=":女優"]')

                # 「女優」
                clickSelector(
                    fox, 'input[type="checkbox"][value="タレント,俳優,女優"]')
                clickSelector(fox, 'input[type="checkbox"][value="音楽"]')
                clickSelector(fox, 'input[type="checkbox"][value="スポーツ"]')
                clickSelector(fox, 'input[type="checkbox"][value="話す仕事"]')
                clickSelector(fox, 'input[type="checkbox"][value="モデル"]')

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
                print('\tcollect() body', file=logfile, flush=True)

                source = fox.page_source
                bs = BeautifulSoup(source, 'lxml')
                print('\tcollect() bs', file=logfile, flush=True)

                searchnavi_total = bs.find_all(
                    'span', class_=re.compile('searchnavi_total'))
                if len(searchnavi_total) == 0:
                    return
                count_all = int(searchnavi_total[0].text)
                last_page = -((-1 * count_all) // PERSONS_PER_PAGE)  # 切り上げ

                for i in range(last_page):
                    print('\tcollect() page: {} {} {} {}'.format(
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
                                        name = str(link.text).replace(' ', '')

                                        profile_page = baseUri + \
                                            '/search/' + link.get('href')

                                        genre = tr.findAll(
                                            'td')[3].text.replace('\n', '')

                                        result_names.append(name + ' ' + genre)

                                        # データファイルに出力
                                        print('{}\t\t{}\t\t{}'.format(name, profile_page, genre),
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
                        print('\tcollect() body', file=logfile, flush=True)

                        source = fox.page_source
                        bs = BeautifulSoup(source, 'lxml')
                        print('\tcollect() bs', file=logfile, flush=True)
                    except:
                        break

                # talemecasting-next
                baseUri = baseUris[1]
                targetUri = targetUris[1]
                print('\tcollect() baseUri: {} {}'.format(
                    baseUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                print('\tcollect() targetUri: {} {}'.format(
                    targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                fox.get(targetUri)
                time.sleep(1)
                WebDriverWait(fox, WAITING_TIME).until(
                    EC.presence_of_element_located((By.XPATH, '//body')))
                print('\tcollect() body', file=logfile, flush=True)

                source = fox.page_source
                bs = BeautifulSoup(source, 'lxml')
                print('\tcollect() bs', file=logfile, flush=True)

                total = bs.find_all(
                    'span', class_=re.compile('required'))
                if len(total) == 0:
                    return
                count_all = int(total[0].text)
                last_page = -((-1 * count_all) // PERSONS_PER_PAGE)  # 切り上げ

                for i in range(last_page):
                    print('\tcollect() page: {} {} {} {}'.format(
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
                                    summaries = li.find_all(
                                        'div', class_='talent-summary')
                                    if len(divs) > 0:
                                        div = divs[0]
                                        smr = summaries[0]
                                        imgs = div.find_all('img')
                                        if len(imgs) > 0:
                                            img = imgs[0]
                                            name = str(img.get(
                                                'alt')).replace('　', '')

                                            download_img(img.get('src'), name)

                                            links = li.find_all('a')
                                            if len(links) > 0:
                                                link = links[0]
                                                profile_page = baseUri + \
                                                    link.get('href')

                                                genre = smr.find_all(
                                                    'div', class_='genre')[0].text.replace('\n', '')
                                                result_names.append(
                                                    name + ' ' + genre)

                                                # データファイルに出力
                                                print('{}\t\t{}\t\t{}'.format(name, profile_page, genre),
                                                      file=datafile, flush=True)

                                except Exception as e:
                                    print(e, file=logfile, flush=True)

                    # 次のページに行く
                    try:
                        clickClassName(fox, 'next')

                        time.sleep(1)
                        WebDriverWait(fox, WAITING_TIME).until(
                            EC.presence_of_element_located((By.XPATH, '//body')))
                        print('\tcollect() body', file=logfile, flush=True)

                        source = fox.page_source
                        bs = BeautifulSoup(source, 'lxml')
                        print('\tcollect() bs', file=logfile, flush=True)
                    except:
                        break

            except Exception as e:
                print(e, file=logfile, flush=True)
            finally:
                # 終了時の後片付け
                try:
                    fox.close()
                    fox.quit()
                    print('\tcollect() Done: {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                except:
                    print(e, flush=True)
    return result_names


def search(names):
    names = list(set(names))
    for name in names:
        profile_dirpath = os.path.join(PHOTO_DIRPATH, name)
        os.makedirs(profile_dirpath, exist_ok=True)
        crawler = BingImageCrawler(storage={"root_dir": profile_dirpath})
        crawler.crawl(keyword=name, max_num=100)
        time.sleep(WAITING_TIME_SEARCH)


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
    with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
        print('\tdownload_img() LOG: {} {} {}'.format(
            datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix), file=logfile, flush=True)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            print('\tdownload_img() get: {} {} {} 200'.format(
                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix), file=logfile, flush=True)
            with open(os.path.join(PHOTO_DIRPATH, filename_prefix + '_' + getFilename(url)), 'wb') as f:
                f.write(r.content)
                print('\tdownload_img() write: {} {} {} 200 f'.format(
                    datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix), file=logfile, flush=True)

                img = imread2(f.name)
                print('\tdownload_img() imread2: {} {} {} img f type:{}'.format(
                    datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix, type(img)), file=logfile, flush=True)

                if img is not None:
                    print('\tdownload_img() img is not Null: {} {} {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix), file=logfile, flush=True)
                    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = faceCascadeClassifier.detectMultiScale(src_gray)
                    print('\tdownload_img() faces: {} {} {}'.format(
                        datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix), file=logfile, flush=True)
                    for x, y, w, h in faces:
                        print('\tdownload_img() faces: {} {} {} xywh: {} {} {} {}'.format(
                            datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix, x, y, w, h), file=logfile, flush=True)
                        try:
                            face = img[y: y + h, x: x + w]
                            filesplt = os.path.splitext(
                                os.path.basename(getFilename(url)))
                            facefile = os.path.join(
                                PHOTO_DIRPATH, filename_prefix + '_' + filesplt[0] + '_{:04}-{:04}-{:04}-{:04}'.format(y, y + h, x, x + w) + filesplt[1])
                            imwrite2(facefile, face)
                        except Exception as e:
                            print('Exception: {} {}'.format(
                                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), e), file=logfile, flush=True)
        else:
            print('\tdownload_img() get: {} {} {} status: {}'.format(
                datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), url, filename_prefix, r.status_code), file=logfile, flush=True)


if __name__ == '__main__':
    with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
        print('Start', file=logfile, flush=True)
    names = collect()
    search(names)
    with open(LOG_FILEPATH, 'a', encoding='utf-8') as logfile:
        print('Done', file=logfile, flush=True)
