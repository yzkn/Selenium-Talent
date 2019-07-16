#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 YA-androidapp(https://github.com/YA-androidapp) All rights reserved.

# ファイル名設定用
import configparser
import datetime
import os

# Seleniumのドライバ
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# # Seleniumで要素の読み込みを待機するためのパッケージ類
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# BS4
from bs4 import BeautifulSoup
import codecs
import re
import requests

# Get json
import json
import urllib.request

import time

import urllib.parse


currentdirectory = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdirectory)
print(os.getcwd())

# 定数
DATA_FILEPATH = os.path.join(
    currentdirectory, 'dat_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')
LOG_FILEPATH = os.path.join(
    currentdirectory, 'log_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt')

WAITING_TIME = 10000

# URI
baseUris = [
    'https://www.talent-databank.co.jp',
    'https://talemecasting-next.com'
]
targetUris = [
    'https://www.talent-databank.co.jp/',
    'https://talemecasting-next.com/talent?birth_year_min=&birth_year_max=&age_min=22&age_max=24&genre%5B%5D=15&height_min=&height_max=&weight_min=&weight_max=&blood=&constellation=&keyword=&carrier='
]

# カテゴリ毎に、取得するページ数
MAX_PAGE = [
    20,
    20
]


# スクショ保存時のファイル名を生成
def get_filepath():
    now = datetime.datetime.now()
    filename = 'screen_{0:%Y%m%d%H%M%S}.png'.format(now)
    filepath = os.path.join(currentdirectory, filename)
    return filepath


def main():
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

                # サイトごとに一覧を取得
                for i, targetUri in enumerate(targetUris):
                    print('\ttargetUri: {} {}'.format(
                        targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)

                    # category = (targetUri.split(baseUris[i] + '/')[1]).split('/archive/')[0]

                    # fox.get(targetUri)
                    # time.sleep(1)
                    # WebDriverWait(fox, WAITING_TIME).until(
                    #     EC.presence_of_element_located((By.CLASS_NAME, 'm-pageNation')))
                    # print('m-pageNation', file=logfile, flush=True)
                    # # time.sleep(1)

                    # for i in range(0, MAX_PAGE_PER_CATEGORY):
                    #     print('i: {}'.format(i), file=logfile, flush=True)

                    #     # スクレイピング
                    #     if i > 0:
                    #         targetUri = targetUri.split(
                    #             '?bn=')[0] + '?bn='+str(i)+'1'
                    #         print('\ttargetUri: {} {}'.format(
                    #             targetUri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                    #         fox.get(targetUri)
                    #         time.sleep(1)
                    #         WebDriverWait(fox, WAITING_TIME).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, 'm-pageNation')))
                    #         print('m-pageNation', file=logfile, flush=True)

                    #     source = fox.page_source
                    #     # BeautifulSoup(source, 'html.parser')
                    #     bs = BeautifulSoup(source, 'lxml')
                    #     print('bs', file=logfile, flush=True)
                    #     # print(source, file=logfile, flush=True)

                    #     # 記事毎に取得
                    #     contents = (bs.find_all('div', id='CONTENTS_MAIN'))
                    #     print('i: {} ; contents: {}'.format(i, len(contents)),
                    #           file=logfile, flush=True)
                    #     if len(contents) == 0:
                    #         continue
                    #     cards = contents[0].find_all('div', class_='m-miM09')
                    #     print('i: {} ; count: {}'.format(i, len(cards)),
                    #           file=logfile, flush=True)

                    #     for card in cards:
                    #         # 明示的に初期化
                    #         title = ''
                    #         uri = ''
                    #         pubdate = ''
                    #         body = ''

                    #         try:
                    #             # print(card.text, file=logfile, flush=True)
                    #             titleclass = (card.find_all('h3', attrs={
                    #                 'class': 'm-miM09_title'}))[0]
                    #             uri = (titleclass.find_all('a'))[0].get("href")
                    #             uri = baseUris[i] + uri
                    #             title = (titleclass.find_all('span', attrs={
                    #                      'class': 'm-miM09_titleL'}))[0].text
                    #             pubdate = (card.find_all('span', attrs={
                    #                        'class': 'm-miM09_date'}))[0].text
                    #             print('\ttitle: ' + title,
                    #                   file=logfile, flush=True)
                    #             print('\turi: ' + uri, file=logfile, flush=True)
                    #             print('\tpubdate: ' + pubdate,
                    #                   file=logfile, flush=True)

                    #             # 記事の1ページ目
                    #             print('\tarticleUri: {} {}'.format(
                    #                 uri, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')), file=logfile, flush=True)
                    #             fox.get(uri)


                    #             # データファイルに出力
                    #             print('{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(
                    #                 category, title, pubdate, uri, body), file=datafile, flush=True)
                    #         except Exception as e:
                    #             print(e, file=logfile, flush=True)

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


def clickClassName(fox, className):
    fox.find_element_by_class_name(className).click()


def clickId(fox, id):
    fox.find_element_by_id(id).click()


def clickLink(fox, text):
    fox.find_element_by_link_text(text).click()


def clickName(fox, name):
    fox.find_element_by_name(name).click()


def clickSelector(fox, selector):
    fox.find_elements_by_css_selector(selector).click()


def clickXpath(fox, xpath):
    fox.find_element_by_xpath(xpath).click()


def clearAndSendKeys(fox, name, text):
    fox.find_element_by_name(name).clear()
    fox.find_element_by_name(name).send_keys(text)


if __name__ == '__main__':
    main()
