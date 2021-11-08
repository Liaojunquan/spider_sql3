# -*- coding: utf-8 -*-
# 该脚本用于爬取subscene网站的电视剧字幕
import time
import requests
from random import randint
import re
from lxml import etree
import sqlite3
import hashlib
import os
import logging
import zipfile
import chardet
from logging.handlers import TimedRotatingFileHandler
import rarfile
import json
import platform
import sys
import regexp_function
import converter

conn = sqlite3.connect('info.db')
cursor = conn.cursor()
subtitles_save_folder = '/data/series'    # 字幕文件和文件夹存放目录，仅支持绝对路径!
csv_file_path = './series.csv'              # 存放电视剧imdb列表的csv文件位置，与脚本文件在同一目录下
proxy = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}       # 代理地址，使用代理软件进行翻墙
USE_PROXY = False    # 是否使用代理的开关
is_save_error_file = True     # 是否保存非法的字幕文件，用于debug

language_dict = {                                          # 语言语种，不需要爬取的语种，使用#进行屏蔽
    "english": 'en', 'English subtitles': 'en',   # 英语
    "spanish": 'es',    # 西班牙语
    "greek": 'el',      # 希腊语
    "arabic": 'ar',     # 阿拉伯
    # "chinese": 'zh', "chinese-bg-code": 'zh', "chinese (china)": 'zh', "chinese (hong kong sar)": 'zh',     # 中文
    # "chinese (taiwan)": 'zh', "chinese-china": 'zh', "chinese-hong kong sar": 'zh', "chinese-macau sar": 'zh',
    # "chinese-taiwan": 'zh', "chinese bg code": 'zh', "chinese (macau sar)": 'zh',
    # "dutch": 'nl', 'Nederlandse Ondertitels': 'nl',     # 荷兰语
    # "serbian": 'sr', "serbian-latin": 'sr', "serbian-cyrillic": 'sr',      # 塞尔维亚
    "brazilian portuguese": 'pt', "portuguese-br": 'pt', "portuguese": 'pt', "brazillian-portuguese": 'pt',  # 葡萄牙语
    "portuguese (br)": 'pt', "brazillian portuguese": 'pt', "brazilian": 'pt', "br": 'pt', "(br)": 'pt',    # (巴西)葡萄牙语
    # "croatian": 'hr',     # 克罗地亚语
    # "french": 'fr',       # 法语
    # "turkish": 'tr',      # 土耳其
    # "indonesian": 'id',   # 印度尼西亚
    # "romanian": 'ro',     # 罗马尼亚语
    # "norwegian": 'no', "norwegian (bokmal)": 'no', "norwegian (nynorsk)": 'no', "norwegian-bokmal": 'no', "norwegian-nynorsk": 'no',  # 挪威
    # "bulgarian": 'bg',   # 保加利亚语
    # "farsi/persian": 'fa', "farsi_persia": 'fa', "farsi_persian": 'fa', "persian": 'fa', "farsi": 'fa',    # 波斯语
    # "hebrew": 'he',       # 希伯来语
    # "danish": 'da',       # 丹麦语
    # "hungarian": 'hu',    # 匈牙利
    # "finnish": 'fi', 'Suomi tekstitykset': 'fi',     # 芬兰语
    # "italian": 'it', "italian (switzerland)": 'it', "italian (italy)": 'it', "italian-switzerland": 'it', "italian-italy": 'it',   # 意大利语
    # "swedish": 'sv', 'Svenska undertexter': 'sv',   # 瑞典语
    # "malay": 'ms', "malay (brunei)": 'ms', "malay (malaysia)": 'ms', "malay-brunei": 'ms', "malay-malaysia": 'ms',   # 马来语
    # "slovenian": 'ls',    # 斯洛文尼亚语
    # "polish": 'pl',       # 波兰语
    # "bengali": 'bn',      # 孟加拉
    # "vietnamese": 'vi',   # 越南
    # "czech": 'cs', "chech": 'cs',   # 捷克语
    # "german": 'de',       # 德语
    # "russian": 'ru',      # 俄语
    # "macedonian": 'mk',   # 马其顿语
    # "thai": 'th',         # 泰国
    # "urdu": 'ur',         # 乌尔都语
    # "japanese": 'ja',     # 日文
    # "albanian": 'sq',     # 阿尔巴尼亚语
    # "korean": 'ko',       # 韩语
    # "lithuanian": 'lt',   # 立陶宛语
    # "bosnian": 'bs',      # 波斯尼亚语
    # "malayalam": 'ml',    # 马拉雅拉姆语
    # "icelandic": 'is',    # 冰岛语
    # "estonian": 'et',     # 爱沙尼亚语
    # "sundanese": 'su',    # 巽他语
    # "sinhala": 'si',      # 僧伽罗语
    # "hindi": 'hi',        # 印地语
    # "telugu": 'te',       # 泰卢固语
    # "galician": 'gl',     # 加利西亚
    # "afrikaans": 'af',    # 南非荷兰语
    # "armenian": 'hy',     # 亚美尼亚
#    "uzbek": 'uz',       # 乌兹别克语
#    "xhosa": 'xh',       # 科萨
#    "yiddish": 'yi',     # 意第绪语
#    "zulu": 'zu',        # 祖鲁
#    "assamese": 'as',    # 阿萨姆语
#    "azeri (latin)": 'az', "azeri (cyrillic)": 'az', "azeri-latin": 'az', "azeri-cyrillic": 'az', "azeri": 'az',   # 阿塞拜疆拉丁语
#    "myanmar": 'mm', "burma": 'mm', "burmese": 'mm',     # 缅甸语
#    "basque": 'eu',      # 巴斯克
#    "belarusian": 'be',  # 白俄罗斯语
#    "catalan": 'ca',    # 加泰罗尼亚语
#    'cambodian/khmer': 'kh', 'khmer': 'kh', 'cambodian': 'kh',   # 高棉语
#    "faeroese": 'fo',   # 法罗语
#    "gaelic": 'gd',     # 盖尔语
#    "georgian": 'ka',   # 格鲁吉亚
#    "gujarati": 'gu',   # 古吉拉特语
#    "kannada": 'kn',    # 卡纳达语
#    "kazakh": 'kk',     # 哈萨克语
#    "konkani": 'kok',   # 康卡尼
#    "kyrgyz": 'kz',     # 吉尔吉斯坦
#    "latvian": 'lv',    # 拉脱维亚语
#    "maltese": 'mt',    # 马耳他语
#    "marathi": 'mr',    # 马拉地语
#    "mongolian (cyrillic)": 'mn',    # 蒙古语（西里尔文）
#    "nepali (india)": 'ne', 'nepali': 'ne',   # 尼泊尔语
#    "oriya": 'or',      # 奥里亚
#    "punjabi": 'pa',    # 旁遮普语
#    "sanskrit": 'sa',   # 梵文
#    "rhaeto-romanic": 'rm',   # 拉丁语
#    "slovak": 'sk',     # 斯洛伐克语
#    "sorbian": 'sb',    # 索布
#    "sutu": 'sx',
#    "swahili": 'sw',    # 斯瓦希里语
#    "syriac": 'syr',    # 叙利亚语
#    "tamil": 'tt',      # 泰米尔语
#    "tsonga": 'ts',
#    "tswana": 'tn',
#    "ukrainian": 'uk',  # 乌克兰文
#    'kurdish': 'ku',    # 库尔德
#    'yoruba': 'yo',     # 约鲁巴语
#    'tagalog': 'tl',    # 他加禄语
    }


# ------------------------------以下内容非必要勿进行修改--------------------------------------
if platform.python_version_tuple()[0] == '3' and int(platform.python_version_tuple()[1]) >= 8:  # python 3.8或以上版本
    sys.stdout.reconfigure(encoding='utf-8')    # 使print函数输出utf-8编码的字符串

logger = logging.getLogger('tv_spider_log')  # 设置日志文件名
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')     # 设置日志输出内容
log_file_handler = TimedRotatingFileHandler(filename='tv_spider_log', when='MIDNIGHT', interval=1, backupCount=20)  # 每日产生一个日志文件log，凌晨生成，超过20个自动删除最旧的
log_file_handler.setFormatter(formatter)
log_file_handler.setLevel(logging.INFO)
logger.addHandler(log_file_handler)

USER_AGENTS_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]

season_dist = {'First Season': 'S01', 'Second Season': 'S02', 'Third Season': 'S03', 'Fourth Season': 'S04',
               'Fifth Season': 'S05', 'Sixth Season': 'S06', 'Seventh Season': 'S07', 'Eighth Season': 'S08',
               'Ninth Season': 'S09', 'Tenth Season': 'S10', 'Eleventh Season': 'S11', 'Twelfth Season': 'S12',
               'Thirteenth Season': 'S13', 'Fourteenth Season': 'S14', 'Fifteenth Season': 'S15',
               'Sixteenth Season': 'S16', 'Seventeenth Season': 'S17', 'Eighteenth Season': 'S18',
               'Nineteenth Season': 'S19', 'Twentieth Season': 'S20', 'Twenty-First Season': 'S21',
               'Twenty-Second Season': 'S22', 'Twenty-Third Season': 'S23', 'Twenty-Fourth Season': 'S24',
               'Twenty-Fifth Season': 'S25', 'Twenty-Sixth Season': 'S26', 'Twenty-Seventh Season': 'S27',
               'Twenty-Eighth Season': 'S28', 'Twenty-Ninth Season': 'S29', 'Thirtieth Season': 'S30',
               'Thirty-First Season': 'S31', 'Thirty-Second Season': 'S32', 'Thirty-Third Season': 'S33',
               'Thirty-Fourth Season': 'S34', 'Thirty-Fifth Season': 'S35', 'Thirty-Sixth Season': 'S36',
               'Thirty-Seventh Season': 'S37', 'Thirty-Eighth Season': 'S38', 'Thirty-Ninth Season': 'S39',
               'Fortieth Season': 'S40', 'Forty-First Season': 'S41', 'Forty-Second Season': 'S42',
               'Forty-Third Season': 'S43', 'Forty-Fourth Season': 'S44', 'Forty-Fifth Season': 'S45',
               'Forty-Sixth Season': 'S46', 'Forty-Seventh Season': 'S47', 'Forty-Eighth Season': 'S48',
               'Forty-Ninth Season': 'S49', 'Fiftieth Season': 'S50'}

insert_sql = "insert into series(imdb_id,episodes,moviename,language,languageShort,path) VALUES(?,?,?,?,?,?);"
select_sql = "select path from series where imdb_id=? and language=? and episodes=?;"
select_all_sql = "select moviename from series where imdb_id=? and language=? and episodes=? and path=?;"

session = requests.session()
url_set = set()


def print_and_log(msg):
    try:
        print(msg)
        logger.info(msg)
    except Exception as err:
        print('Error: Unable to print msg!!!')
        print(err)
        logger.info('Error: Unable to print msg!!!')
        logger.info(err)


def stander_header():     # 常规请求头
    return {
        'accept-encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def ajax_header():     # ajax请求头
    return {
        'accept-encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'accept': 'application/json, text/plain, */*',
        'Host': 'v2.sg.media-imdb.com',
        'Origin': 'https://www.imdb.com',
        'Referer': 'https://www.imdb.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def download_header():
    return {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://subscene.com/subtitles/searchbytitle',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }


def get_cookies():
    count = 0
    while count < 3:
        try:
            if USE_PROXY:
                res = session.get('https://subscene.com', headers=stander_header(), proxies=proxy)     # 获取cookies
            else:
                res = session.get('https://subscene.com', headers=stander_header())  # 获取cookies
        except:
            count += 1
            time.sleep(5)
            continue
        else:
            if res.status_code != 200:
                count += 1
                time.sleep(5)
                continue
            else:
                # print_and_log('Get cookies ok!')
                break


def get_response(url, my_header):
    time.sleep(5)
    res = None
    count = 0
    while count < 3:    # 3次重连机会
        try:
            if USE_PROXY:
                res = session.get(url, headers=my_header, proxies=proxy, timeout=15)
            else:
                res = session.get(url, headers=my_header, timeout=15)
        except Exception as err:
            count += 1
            print_and_log(err)
            print_and_log('Retry again!  '+str(count))
            time.sleep(10)
            continue
        else:
            if res.status_code != 200:
                count += 1
                print_and_log('Status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                if res.status_code == 403:
                    time.sleep(15)
                elif res.status_code == 409:
                    time.sleep(5)
                else:
                    time.sleep(10)
                continue
        if res is not None and res.status_code == 200:
            break
    if res is None or count >= 3:
        return None
    else:
        return res


def post_response(url, my_header, post_data):
    time.sleep(5)
    res = None
    count = 0
    while count < 3:     # 3次重连机会
        try:
            if USE_PROXY:
                res = session.post(url, headers=my_header, data=post_data, proxies=proxy, timeout=15)
            else:
                res = session.post(url, headers=my_header, data=post_data, timeout=15)
        except Exception as err:
            count += 1
            print_and_log('Post connect retry again! ' + str(count))
            print_and_log(err)
            time.sleep(10)
            continue
        else:
            if res.status_code != 200:
                count += 1
                print_and_log('Post status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                if res.status_code == 403:
                    time.sleep(15)
                elif res.status_code == 409:
                    time.sleep(5)
                else:
                    time.sleep(10)
                continue
        if res is not None and res.status_code == 200:
            break
    if res is None or count >= 3:
        return None
    else:
        return res


def transform_encode(data):      # 字幕文件转码为utf-8
    try:
        encode = chardet.detect(data)
        str_encode = encode['encoding']
        if str_encode == 'MacCyrillic':
            str_encode = 'Windows-1256'
        if str_encode is not None:
            d = data.decode(str_encode, errors='ignore')
        else:
            try:
                d = data.decode('UTF-8')
            except:
                try:
                    d = data.decode('gbk')
                except:
                    try:
                        d = data.decode('gb2312')
                    except:
                        try:
                            d = data.decode('cp437')
                        except:
                            try:
                                d = data.decode('cp850')
                            except:
                                print_and_log('Error: No suitable charset encoding is available!')
                                return None
        if d.find('\r') == -1:  # 不是CR和CRLF，则是LF
            d = d.replace('\n', '\r\n')  # LF转CRLF
        elif d.find('\r\n') == -1:  # 不是CRLF和LF，则是CR
            d = d.replace('\r', '\r\n')  # CR转CRLF
        elif d.find('\r\r\n') != -1:
            d = d.replace('\r\r\n', '\r\n')  # 转CRLF
        else:
            pass  # 是CRLF无需转换
        after = d.encode('UTF-8', errors='ignore')
    except Exception as err:
        print_and_log('Error in transform_encode!')
        print_and_log(err)
        return None
    else:
        return after


def file_name_translate(name):
    translate_name = None
    try:
        translate_name = name.replace('\u2019', '').encode('cp437', errors='ignore').decode('ascii', errors='ignore')
    except Exception as err:
        translate_name = None
        print_and_log('Error: No suitable charset encoding is available for file name!')
        print_and_log(err)
    return translate_name


def delete_special_char(name):
    # 去掉文件名中的括号和特殊字符
    return name.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '') \
        .replace(' .', '.').replace('. ', '.').replace('?', '').replace('&', '').replace("'", '').replace('%20', '-') \
        .replace('`', '').replace('!', '').replace(',', '').replace('-_-', '-').replace('#', '').replace('+', '-') \
        .replace('%', '').replace('@', '').replace('!', '').replace('$', '').replace('^', '').replace('*', '') \
        .replace('~', '').replace('<', '').replace('>', '').replace('|', '').replace('"', '').replace('=', '') \
        .replace(';', '').replace(':', '').replace(' ', '-').replace('._.', '-').replace('.-.', '-') \
        .replace('-.-', '-').replace('--', '-').replace('..', '.').replace('__', '-')


def check_file_format(data):
    raw_str = data.decode('utf-8')
    if ('ScriptType:' in raw_str or '[Script Info]' in raw_str) and '[Events]' in raw_str and \
            'Format:' in raw_str and 'Dialogue:' in raw_str:
        return 'ass'
    elif '<SAMI>' in raw_str.upper() and '<SYNC' in raw_str.upper():
        return 'smi'
    elif len(re.findall(r'(\{.*?\d+.*?\}\{.*?\d+.*?\})', raw_str)) > len(raw_str.split('\n')) * 0.9:
        return 'sub'
    elif '[INFORMATION]' in raw_str and '[TITLE]' in raw_str and '[AUTHOR]' in raw_str and '[END INFORMATION]' in raw_str:
        return 'sub1'
    re_list = re.findall(r'(\d+ {0,1}\r{0,1}\n\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d {0,2}\-{1,3}> {0,2}\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d {0,1}.*?\r{0,1}\n.*?\r{0,1}\n)', raw_str)
    # if len(re_list) == 0:
    #    return 'unknown'
    # diff = abs(len(re_list) - int(re_list[-1].split('\n')[0].replace('\r', '').strip()))
    if len(re_list) > 35:
        return 'srt'
    else:
        return 'unknown'


def save_convert_error_file(data, file_name):
    if not is_save_error_file:
        return None
    try:
        if not os.path.exists(os.path.abspath('.') + '/error_file'):
            os.mkdir(os.path.abspath('.') + '/error_file')
        with open(os.path.abspath('.') + '/error_file/' + file_name, 'wb') as f:
            f.write(data)
    except Exception as err:
        print_and_log('Error: Unable save error file!')
        print_and_log(err)


def download_subtitles_file(url, language, imdb, tv_name, subtitle_id, season):
    file_name = url.split('/')[-1] + '.zip'
    res = None
    count = 0
    while count < 8:
        res = get_response(url, my_header=download_header())  # 下载字幕文件zip包
        if res is None or res.status_code != 200:
            count += 1
            if res is not None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log(str(count) + '  Unable to download subtitles file!  ' + url)
            session.cookies.clear_session_cookies()
            time.sleep(5)
            get_cookies()
            continue
        else:
            count = 0
            break
    if res is None or count >= 8:
        return None
    try:
        with open(subtitles_save_folder+'/tmp/'+file_name, 'wb') as f:       # 字幕压缩包保存到E:/data/series/tmp目录下
            f.write(res.content)
    except Exception as err:
        print_and_log('Error: Unable save compress file to disk!!!')
        print_and_log(err)
        return None
    try:
        zip_file = zipfile.ZipFile(subtitles_save_folder + '/tmp/' + file_name, 'r')  # 尝试使用zip打开压缩包
    except:
        try:
            zip_file = rarfile.RarFile(subtitles_save_folder + '/tmp/' + file_name, 'r')  # 不成功，则尝试使用rar打开压缩包
        except Exception as err:
            print_and_log('Error: Unable to open compress file!!!')
            print_and_log(err)
            return None
    for srt_file_name in zip_file.namelist():     # 遍历压缩包内所有文件的文件名称
        srt_file = file_name_translate(srt_file_name)  # 文件名去除非ASC-II编码的字符
        if srt_file is None:
            continue
        if '/' in srt_file:  # 文件名带有目录的情况
            srt_file = delete_special_char(srt_file[srt_file.rfind('/') + 1:].replace('\\', ''))
        elif '\\' in srt_file:  # 文件名带有目录的情况
            srt_file = delete_special_char(srt_file[srt_file.rfind('\\') + 1:].replace('/', ''))
        else:  # 文件名不带有目录
            srt_file = delete_special_char(srt_file)
        try:
            srt_file = srt_file[:-4] + srt_file[-4:].lower()  # 后缀统一转小写
        except:
            pass
        is_error_file = False
        if not srt_file.endswith('.srt') and not srt_file.endswith('.ass') and not srt_file.endswith('.smi') and \
                not srt_file.endswith('.sub') and not srt_file.endswith('.ssa') and not srt_file.endswith('.txt'):  # 不是指定后缀的文件，则跳过
            print_and_log('Not a subtitle file:  ' + srt_file)
            is_error_file = True
        season_and_episode = regexp_function.get_season_and_episode(srt_file)  # 从文件名获取季和集信息
        if season_and_episode is None:
            episode = regexp_function.get_episode(srt_file)  # 从文件名获取集信息
            if episode is None:
                print_and_log('Error: File name not contain season and episode:  ' + srt_file)
                continue
            else:
                if season is None:
                    print_and_log('Error: Title and file name not contain season:  ' + srt_file)
                    continue
                else:
                    print_and_log('Only episode in file name: ' + srt_file)
                    season_and_episode = season + episode
        file_path = subtitles_save_folder+'/'+imdb+'/'+season_and_episode
        if not os.path.exists(file_path):         # 创建季和集文件夹，存放指定季和集的字幕文件
            os.mkdir(file_path)
        try:
            data = zip_file.read(srt_file_name)  # 根据文件名从zip包读取指定文件
        except Exception as err:
            print_and_log('Error: Unable to read file from compress file! (no replace)')
            print_and_log(err)
            try:
                data = zip_file.read(srt_file_name.replace('/', '\\'))  # 根据文件名从zip包读取指定文件
            except Exception as err:
                print_and_log('Error: Unable to read file from compress file! (replace /)')
                print_and_log(err)
                try:
                    data = zip_file.read(srt_file_name.replace('\\', '/'))  # 根据文件名从zip包读取指定文件
                except Exception as err:
                    print_and_log('Error: Unable to read file from compress file! (replace \\)')
                    print_and_log(err)
                    continue
        if len(data) < 1000 * 5:  # 数据小于5KB
            print_and_log('Subtitle file data too small: ' + srt_file + '  ' + str(len(data) / 1000) + 'KB')
            save_convert_error_file(data, srt_file)
            continue
        if is_error_file:
            save_convert_error_file(data, srt_file)
            continue
        data = transform_encode(data)
        if data is None:  # 字幕文件不成功转码为utf-8，则放弃
            continue
        file_format = check_file_format(data)
        if 'unknown' in file_format:  # 非字幕文件格式文件，跳过
            print_and_log('Error: this subtitle file format is unknown!!!  ' + srt_file)
            save_convert_error_file(data, srt_file)
            continue
        elif file_format == 'srt':  # srt字幕文件
            data_tmp = converter.convertSRT(data)
            if type(data_tmp) == str:
                print_and_log('Error: Unable to standardized srt file, ' + data_tmp)
                save_convert_error_file(data, srt_file)
                continue
            data = data_tmp
            srt_file = srt_file[:srt_file.rfind('.')] + '.srt'
            srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file  # 新文件绝对路径
        elif file_format == 'ass':  # ass字幕文件
            data_tmp = converter.convertASS(data)
            if type(data_tmp) == str:
                print_and_log('Error: Unable to convert ass file to srt file, ' + data_tmp)
                save_convert_error_file(data, srt_file)
                continue
            data = data_tmp
            srt_file = srt_file[:srt_file.rfind('.')] + '.ass'
            srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file + '.srt'  # 新文件绝对路径
        elif file_format == 'smi':  # smi字幕文件
            data_tmp = converter.convertSMI(data)
            if type(data_tmp) == str:
                print_and_log('Error: Unable to convert smi file to srt file, ' + data_tmp)
                save_convert_error_file(data, srt_file)
                continue
            data = data_tmp
            srt_file = srt_file[:srt_file.rfind('.')] + '.smi'
            srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file + '.srt'  # 新文件绝对路径
        elif file_format == 'sub':  # sub字幕文件
            data_tmp = converter.convertSUB(data)
            if type(data_tmp) == str:
                print_and_log('Error: Unable to convert sub file to srt file, ' + data_tmp)
                save_convert_error_file(data, srt_file)
                continue
            data = data_tmp
            srt_file = srt_file[:srt_file.rfind('.')] + '.sub'
            srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file + '.srt'  # 新文件绝对路径
        elif file_format == 'sub1':  # sub1字幕文件
            data_tmp = converter.convertSUB1(data)
            if type(data_tmp) == str:
                print_and_log('Error: Unable to convert sub1 file to srt file, ' + data_tmp)
                save_convert_error_file(data, srt_file)
                continue
            data = data_tmp
            srt_file = srt_file[:srt_file.rfind('.')] + '.sub'
            srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file + '.srt'  # 新文件绝对路径
        else:
            continue
        md5_this = None
        try:
            if type(data) == list:
                md5_this = hashlib.md5(data[0]).hexdigest()
            else:
                md5_this = hashlib.md5(data).hexdigest()
        except Exception as err:
            print_and_log('Error: 1---Unable to get file MD5!  '+srt_file)
            print_and_log(err)
            continue
        if md5_this is None:
            print_and_log('Error: 1---Unable to get file MD5!  ' + srt_file)
            continue
        result = ()
        try:
            cursor.execute(select_sql, (imdb, language, season_and_episode))      # 从数据库查询所有该电视剧、该语种、该季集的字幕文件路径
            result = cursor.fetchall()
        except Exception as err:
            print_and_log('Error: Unable to get data from DB!!! Unable to compare the subtitle file MD5 value!')
            print_and_log(err)
            continue
        is_exist = False    # 字幕文件是否已存在，默认为否
        for each_result in result:     # 分别比较已存在的文件与现在下载的文件的MD5值
            path = each_result[0]    # 去掉域名，变成本机文件地址
            try:
                with open(path, 'rb') as f:           # 读取文件，获取其MD5值
                    md5_result = hashlib.md5(f.read()).hexdigest()
            except Exception as err:
                print_and_log('Error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                print_and_log(err)
                continue
            if md5_result is None:
                print_and_log('Error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                continue
            if md5_this == md5_result:    # MD5相同，即为相同字幕文件
                is_exist = True
                # print_and_log('<< '+tv_name+' >> '+language+' '+season_and_episode+' '+srt_file_new.split('/')[-1]+' is existed on Disk!!!')
                break
        if not is_exist:   # 文件还没存在
            language_short = language_dict.get(language)   # 获取语言缩写
            result = ()
            try:
                if type(data) == list:
                    cursor.execute(select_all_sql, (imdb, language, srt_file_new.replace('.sub.srt', '') + '-23.976fps.sub.srt'))
                else:
                    cursor.execute(select_all_sql, (imdb, language, srt_file_new))  # 查询数据库是否已有该文件名称的电影记录
                result = cursor.fetchall()
            except Exception as err:
                print_and_log('Error: Unable to get data from DB!!! Unable to check this subtitle data existed or not on DB!')
                print_and_log(err)
                continue
            if len(result) > 0:  # 有该文件名称的电视剧记录
                random_code = format(int(str(time.time()).replace('.', '') + str(randint(0, 100))), 'x')
                if srt_file_new.endswith('.ass.srt'):
                    srt_file_new = srt_file_new.replace('.ass.srt', '') + '-' + random_code + '.ass.srt'  # 文件名增加随机码，以避开相同文件名
                elif srt_file_new.endswith('.smi.srt'):
                    srt_file_new = srt_file_new.replace('.smi.srt', '') + '-' + random_code + '.smi.srt'  # 文件名增加随机码，以避开相同文件名
                elif srt_file_new.endswith('.sub.srt'):
                    srt_file_new = srt_file_new.replace('.sub.srt', '') + '-' + random_code + '.sub.srt'  # 文件名增加随机码，以避开相同文件名
                else:
                    srt_file_new = srt_file_new.replace('.srt', '') + '-' + random_code + '.srt'  # 文件名增加随机码，以避开相同文件名
            try:
                if type(data) == list:
                    cursor.execute(insert_sql, (imdb, tv_name, language, language_short,
                                                srt_file_new.replace('.sub.srt', '') + '-23.976fps.sub.srt'))  # 插入数据库
                    cursor.execute(insert_sql, (imdb, tv_name, language, language_short,
                                                srt_file_new.replace('.sub.srt', '') + '-24fps.sub.srt'))  # 插入数据库
                    cursor.execute(insert_sql, (imdb, tv_name, language, language_short,
                                                srt_file_new.replace('.sub.srt', '') + '-25fps.sub.srt'))  # 插入数据库
                else:
                    cursor.execute(insert_sql, (imdb, tv_name, language, language_short, srt_file_new))  # 插入数据库
                conn.commit()
            except Exception as err:
                print_and_log('Error: Unable insert data to DB!!!')
                print_and_log(err)
                continue
            else:                # 插入数据库成功后，再把文件写入磁盘
                try:
                    if type(data) == list:
                        with open(srt_file_new.replace('.sub.srt', '') + '-23.976fps.sub.srt', 'wb') as f:
                            f.write(data[0])
                        with open(srt_file_new.replace('.sub.srt', '') + '-24fps.sub.srt', 'wb') as f:
                            f.write(data[1])
                        with open(srt_file_new.replace('.sub.srt', '') + '-25fps.sub.srt', 'wb') as f:
                            f.write(data[2])
                    else:
                        with open(srt_file_new, 'wb') as f:
                            f.write(data)
                except Exception as err:
                    print_and_log('Error: Unable save subtitle file to disk!!!')
                    print_and_log(err)
                    continue
                print_and_log('********<< ' + tv_name + ' >> ' + language + ' ' + season_and_episode + ' ' + srt_file_new.split('/')[-1] + ' is successfully insert to DB!')
    try:
        zip_file.close()     # 关闭压缩文件
    except Exception as err:
        print_and_log('Error: Unable to close compress file!!!  '+subtitles_save_folder+'/tmp/'+file_name)
        print_and_log(err)
    try:
        for each_compress_file in os.listdir(subtitles_save_folder+'/tmp'):
            os.remove(subtitles_save_folder+'/tmp/'+each_compress_file)        # 删除tmp目录下压缩包和字幕文件，节约空间
    except Exception as err:
        print_and_log('Error: Unable to delete compress file and subtitle file!!!')
        print_and_log(err)


def main():
    global subtitles_save_folder
    get_cookies()
    subtitles_save_folder = subtitles_save_folder.replace('\\', '/')
    if len(subtitles_save_folder.split('/')) < 2:
        print_and_log('subtitles_save_folder Error!!!')
        return None
    path_tmp = ''
    for i in range(len(subtitles_save_folder.split('/'))):
        if i == 0:
            path_tmp += subtitles_save_folder.split('/')[i]
        else:
            path_tmp += ('/' + subtitles_save_folder.split('/')[i])
            if not os.path.exists(path_tmp):
                os.mkdir(path_tmp)                            # 创建subtitles_save_folder各文件夹
    if not os.path.exists(subtitles_save_folder + '/tmp'):           # 创建存放压缩包的临时文件夹tmp
        os.mkdir(subtitles_save_folder + '/tmp')
    csv_file = open(csv_file_path, 'r')    # 读取csv文件
    imdb_str = csv_file.read()
    csv_file.close()
    imdb_list = imdb_str.split('\n')    # 获取csv文件中的所有电视剧imdb
    imdb_list_index = 0
    while imdb_list_index < len(imdb_list):
        print_and_log('IMDB now is '+imdb_list[imdb_list_index])
        print_and_log('IMDB schedule is ' + str(int((imdb_list_index + 1) / len(imdb_list) * 100)) + '%')
        imdb_url = 'https://v2.sg.media-imdb.com/suggestion/t/' + imdb_list[imdb_list_index] + '.json'
        tv_name_ajax = None
        res = get_response(imdb_url, my_header=ajax_header())
        if res is None or res.status_code != 200:
            if res is not None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('Error: Unable to get IMDB ajax response!')
        else:
            try:
                json_dict = json.loads(res.text)
                tv_name_ajax = json_dict['d'][0]['l']
            except Exception as err:
                print_and_log('Error: Unable to get TV name from json response!')
                print_and_log(err)
                tv_name_ajax = None
        imdb_url = 'https://www.imdb.com/title/' + imdb_list[imdb_list_index] + '/'
        res = get_response(imdb_url, my_header=stander_header())  # 搜索IMDB网站获取imdb对应的电视剧名称
        if res is None or res.status_code != 200:
            if res is not None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('Error: Unable to get IMDB page response!')
            imdb_list_index += 1
            continue
        html = etree.HTML(res.text)
        season = None
        if len(html.xpath('//select[@id="browse-episodes-season"]')) == 0 and \
                len(html.xpath('//div[starts-with(@class, "BrowseEpisodes__BrowseLinksContainer")]')) != 0:
            season = 'S01'  # 从imdb页面可知该电视剧是否只有一季
        h1 = html.xpath('//h1')
        if h1 is None or len(h1) == 0:
            print_and_log('Error: Unable to get this TV name title h1! ' + imdb_url)
            imdb_list_index += 1
            continue
        h1 = h1[0]
        tv_name = h1.getprevious().xpath('.//text()')  # 获取真正的电视剧名称，非剧集名称
        imdb_true = h1.getprevious().xpath('./a/@href')  # 获取真正的电视剧的imdb
        if tv_name is None or len(tv_name) == 0 or imdb_true is None or len(imdb_true) == 0:
            if tv_name_ajax is not None:
                tv_name = [tv_name_ajax]
            else:
                tv_name = h1.xpath('./text()')  # 若无，则该剧集名称就是电视剧名称
            imdb_true = None
        else:
            imdb_t = re.findall(r'.*\D(tt\d{7,8})\D.*', imdb_true[0])  # 有则获取真正电视剧的imdb
            if imdb_t is None or len(imdb_t) == 0:  # 无法获取真正的电视剧的imdb
                if tv_name_ajax is not None:
                    tv_name = [tv_name_ajax]
                else:
                    tv_name = h1.xpath('./text()')
                imdb_true = None
            else:
                imdb_true = imdb_t[0]
        if tv_name is None or len(tv_name) == 0:
            print_and_log('Error: Unable to get TV name!  ' + imdb_url)
            imdb_list_index += 1
            continue
        tv_name = ''.join(tv_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()      # 获取imdb对应的电视剧名称
        post_data = {'query': tv_name, 'l': ''}
        header_subscene = {
            'referer': 'https://subscene.com/subtitles/searchbytitle',
            'origin': 'https://subscene.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en',
            'accept-encoding': 'gzip, deflate',
            'ec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
        }
        h2 = None
        uls = None
        count = 0
        while count < 8:
            res = post_response('https://subscene.com/subtitles/searchbytitle', header_subscene, post_data)        # 使用subscene网站进行搜索
            if res is None or res.status_code != 200:
                if res is not None:
                    print_and_log('Status Code is ' + str(res.status_code))
                print_and_log(str(count)+'  Error: Unable to search: << '+tv_name+' >> in subscene.com  '+imdb_list[imdb_list_index])
                session.cookies.clear_session_cookies()
                time.sleep(30)
                count += 1
                get_cookies()
                continue
            html = etree.HTML(res.text)
            h2 = html.xpath('//div[@class="search-result"]/h2/text()')  # 获取标题(电视剧名称)
            uls = html.xpath('//div[@class="search-result"]/ul')  # 获取ul标签
            if h2 is None or uls is None or len(h2) == 0 or len(uls) == 0 or len(h2) != len(uls):
                print_and_log(str(count)+'  Error: Unable to get all TV subtitles title!!!  '+imdb_list[imdb_list_index])
                session.cookies.clear_session_cookies()
                time.sleep(5)
                count += 1
                get_cookies()
                continue
            else:
                break
        if count >= 8 or h2 is None or uls is None:
            imdb_list_index += 1
            continue
        lis = []
        if 'TV-Series' in h2:  # 有电视剧系列
            for i in range(len(h2)):
                if h2[i] == 'TV-Series':  # 仅获取电视剧系列
                    lis = uls[i].xpath('./li')
        else:  # 若无电视剧系列，则获取全部标题
            for i in range(len(h2)):
                lis += uls[i].xpath('./li')
        if len(lis) == 0:
            print_and_log('Error: Unable to get lis!!!  ' + imdb_list[imdb_list_index] + '  << ' + tv_name + ' >>')
            imdb_list_index += 1
            continue
        li_index = 0
        schedule = 0         # 每一个电视字幕文件的爬取进度
        is_not_found = True  # 是否找到指定imdb的电视剧，默认为否
        while li_index < len(lis):
            schedule += 1
            print_and_log('<< '+tv_name+' >>  schedule now is: '+str(int(schedule/len(lis)*100))+'%')
            href = lis[li_index].xpath('.//a/@href')  # 获取电视剧字幕详情页面URL
            title_name = lis[li_index].xpath('.//a/text()')  # 获取电视剧字幕详情页面标题
            if season is None and title_name is not None:
                title_name = ''.join(title_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()
                for each_season in season_dist.keys():
                    if each_season in title_name:
                        season = season_dist[each_season]
                        break
            if href is None or len(href) == 0:
                print_and_log('Unable to get subtitles detail page url!  ' + tv_name)
                li_index += 1
                continue
            tv_url = 'https://subscene.com' + href[0]
            if 'TV-Series' not in h2 and tv_url in url_set:      # 检测该url是否已被访问过
                li_index += 1
                continue
            res = get_response(tv_url, my_header=header_subscene)  # 打开该电视剧字幕详情页面
            if res is None or res.status_code != 200:
                if res is not None:
                    print_and_log('Status Code is ' + str(res.status_code))
                print_and_log('Unable to open page ' + tv_url + '  ' + imdb_list[imdb_list_index])
                li_index += 1
                continue
            url_set.add(tv_url)  # 设置该url已被访问过
            html = etree.HTML(res.text)
            imdb = html.xpath('//h2/a[@class="imdb"]/@href')
            if imdb is None or len(imdb) == 0:
                # print_and_log('Unable to get imdb, jump this!!!')
                li_index += 1
                continue
            imdb = imdb[0].split('/')[-1]
            if 'tt' not in imdb:
                li_index += 1
                continue  # 不是imdb，跳过
            try:
                imdb_tmp = str(int(imdb.replace('tt', '')))
            except Exception:    # imdb异常或不标准
                li_index += 1
                continue
            else:
                if len(imdb_tmp) > 8:  # imdb位数大于8，非正常imdb
                    li_index += 1
                    continue
                elif len(imdb_tmp) < 7:  # imdb位数小于7，补够7位
                    imdb = 'tt' + '0' * (7 - len(imdb_tmp)) + imdb_tmp
                else:  # 7位或8位，正常imdb
                    imdb = 'tt' + imdb_tmp
            if imdb not in imdb_list and imdb != imdb_true:
                li_index += 1
                continue  # 不是指定imdb的电视剧字幕，跳过
            else:
                is_not_found = False  # 是指定imdb的电视剧字幕
            a_s = html.xpath('//div[@class="content clearfix"]//tr/td[@class="a1"]/a')    # 获取页面上的字幕列表
            a_index = 0
            while a_index < len(a_s):      # 遍历字幕列表每一个字幕
                language = a_s[a_index].xpath('./span[1]/text()')     # 获取字幕语言
                file_page_url = a_s[a_index].xpath('./@href')       # 获取字幕下载详情页地址
                if file_page_url is None or language is None or len(file_page_url) == 0 or len(language) == 0:
                    print_and_log('Error: Unable to get subtitle title!  ' + imdb_list[imdb_list_index])
                    a_index += 1
                    continue
                language = language[0].replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip().lower()
                if 'big' in language or language_dict.get(language) is None:
                    a_index += 1
                    continue
                file_page_url = 'https://subscene.com' + file_page_url[0].replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
                subtitle_id = file_page_url.split('/')[-1]        # 获取该字幕的id
                count = 0
                download_url = None
                while count < 8:
                    res = get_response(file_page_url, my_header=stander_header())  # 打开字幕下载详情页面
                    if res is None or res.status_code != 200:
                        if res is not None:
                            print_and_log('Status Code is ' + str(res.status_code))
                        print_and_log(str(count) + '  Unable to open subtitles download page!  ' + file_page_url + '  ' + imdb_list[imdb_list_index])
                        session.cookies.clear_session_cookies()
                        count += 1
                        time.sleep(5)
                        get_cookies()
                        continue
                    html = etree.HTML(res.text)
                    download_url = html.xpath('//a[@id="downloadButton"]/@href')  # 获取字幕下载地址
                    if download_url is None or len(download_url) == 0:
                        print_and_log(str(count) + '  Unable to get subtitle download url!!!  ' + file_page_url)
                        count += 1
                        time.sleep(5)
                        continue
                    else:
                        break
                if count >= 8 or download_url is None or len(download_url) == 0:
                    a_index += 1
                    continue
                download_url = 'https://subscene.com' + download_url[0]
                if not os.path.exists(subtitles_save_folder+'/'+imdb_list[imdb_list_index]):     # 创建该电视剧的文件夹
                    os.mkdir(subtitles_save_folder+'/'+imdb_list[imdb_list_index])
                download_subtitles_file(download_url, language, imdb_list[imdb_list_index], tv_name, subtitle_id, season)    # 下载字幕文件zip包，并进行比较、转码和入库
                a_index += 1
            li_index += 1
        if is_not_found:
            if imdb_true is not None:
                print_and_log('Error: << ' + tv_name + ' >>  ' + imdb_list[imdb_list_index] + '  ->  ' + imdb_true + ' not Found !!!')
            else:
                print_and_log('Error: << ' + tv_name + ' >>  ' + imdb_list[imdb_list_index] + ' not Found !!!')
        imdb_list_index += 1
    print_and_log('-----------------Finish All!--------------------')


if __name__ == '__main__':
    main()
    cursor.close()
    conn.close()
