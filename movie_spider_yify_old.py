# -*- coding: utf-8 -*-
# 该脚本用于爬取yify网站的电影字幕
import time
import requests
from random import randint
import json
from lxml import etree
# import pymysql
import sqlite3
import hashlib
import os
import logging
import copy
import zipfile
import chardet
import shutil
from logging.handlers import TimedRotatingFileHandler
import rarfile

# conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='subtitles')   # 连接数据库，字幕文件记录入数据库，以便可以增量爬取
conn = sqlite3.connect('info.db')
cursor = conn.cursor()
subtitles_save_folder = './data/movies'    # 字幕文件和文件夹存放目录，字幕保存地址示例：E:/data/movies/tt1234567/en/xxxxxx.srt
csv_file_path = './movies.csv'              # 存放电影imdb列表的csv文件位置，与脚本文件在同一目录下
proxy = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}       # 代理地址，使用代理软件进行翻墙
USE_PROXY = True    # 是否使用代理的开关

language_dict = {                                          # 语言语种，不需要爬取的语种，使用#进行屏蔽
    "english": 'en', 'English subtitles': 'en',   # 英语
    "spanish": 'es',    # 西班牙语
    "greek": 'el',      # 希腊语
    "arabic": 'ar',     # 阿拉伯
  # 葡萄牙语
    "portuguese (br)": 'pt', "brazillian portuguese": 'pt', "brazilian": 'pt', "br": 'pt', "(br)": 'pt',    # (巴西)葡萄牙语

   # "chinese": 'zh', "chinese-bg-code": 'zh', "chinese (china)": 'zh', "chinese (hong kong sar)": 'zh',     # 中文
    # "chinese (taiwan)": 'zh', "chinese-china": 'zh', "chinese-hong kong sar": 'zh', "chinese-macau sar": 'zh',
    # "chinese-taiwan": 'zh', "chinese bg code": 'zh', "chinese (macau sar)": 'zh',
    # "dutch": 'nl', 'Nederlandse Ondertitels': 'nl',     # 荷兰语
    # "serbian": 'sr', "serbian-latin": 'sr', "serbian-cyrillic": 'sr',      # 塞尔维亚
    # "brazilian portuguese": 'pt', "portuguese-br": 'pt', "portuguese": 'pt', "brazillian-portuguese": 'pt',  # 
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

# ------------------------------以下内容非必要勿进行修改---------------------------------------------

logger = logging.getLogger('yify_spider_log')  # 设置日志文件名
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')     # 设置日志输出内容
log_file_handler = TimedRotatingFileHandler(filename='yify_spider_log', when='MIDNIGHT', interval=1, backupCount=20)  # 每日产生一个日志文件log，凌晨生成，超过20个自动删除最旧的
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

insert_sql = "insert into subtitle (imdb_id,moviename,language,languageShort,path) VALUES (?,?,?,?,?);"
select_sql = "select path from subtitle where imdb_id=? and language=?;"
select_all_sql = "select moviename from subtitle where imdb_id=? and language=? and path=?;"

session = requests.session()

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

def download_header():
    return {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
    }

def get_cookies():
    count = 0
    while count < 3:
        try:
            if USE_PROXY:
                res = session.get('https://yts-subs.com', headers=stander_header(), proxies=proxy)     # 获取cookies
            else:
                res = session.get('https://yts-subs.com', headers=stander_header())  # 获取cookies
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
            session.cookies.clear_session_cookies()
            time.sleep(10)
            get_cookies()
            continue
        else:
            if res.status_code != 200:
                count += 1
                session.cookies.clear_session_cookies()
                if res.status_code == 404:
                    get_cookies()
                    break
                print_and_log('Status code is ' + str(res.status_code) + ' Retry again!  ' + str(count))
                if res.status_code == 403:
                    time.sleep(15)
                elif res.status_code == 409:
                    time.sleep(5)
                else:
                    time.sleep(10)
                get_cookies()
                continue
        if res != None and res.status_code == 200:
            break
    return res

def get_short_language(language):
    return language_dict.get(language)

def transform_encode(path):      # 字幕文件转码为utf-8
    try:
        f = open(path, 'rb')
        data = f.read()
        f.close()
        encode = chardet.detect(data)
        str_encode = encode['encoding']
        if str_encode == 'MacCyrillic':
            str_encode = 'Windows-1256'
        if str_encode != None:
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
                                return False
        after = d.encode('UTF-8', errors='ignore')
        ff = open(path, 'wb')
        ff.write(after)
        ff.close()
    except Exception as err:
        print_and_log('Error in transform_encode!')
        print_and_log(err)
        return False
    else:
        return True

def file_name_translate(name):
    try:
        translate_name = name.encode('cp437', errors='ignore').decode('utf-8', errors='ignore')
    except Exception as err:
        translate_name = None
        print_and_log('Error: No suitable charset encoding is available for file name!')
        print_and_log(err)
    return translate_name

def remove_file(path):
    try:
        os.remove(path)
    except Exception as err:
        print_and_log('Error: Unable to remove file '+path)
        print_and_log(err)

def replace_special_char(name):
    mv_name = copy.deepcopy(name)
    mv_name = mv_name.replace('%', '%25').replace('!', '%21').replace('"', '%22').replace('#', '%23').replace('$', '%24').replace('&', '%26')  # 转义URL特殊字符
    mv_name = mv_name.replace("'", '%27').replace('(', '%28').replace(')', '%29').replace('*', '%2A').replace('+', '%2B').replace(',', '%2C').replace('/', '%2F')
    mv_name = mv_name.replace(':', '%3A').replace(';', '%3B').replace('<', '%3C').replace('=', '%3D').replace('>', '%3E').replace('?', '%3F').replace('@', '%40')
    mv_name = mv_name.replace('\\', '%5C').replace('|', '%7C').replace('<', '%3C').replace('[', '%5B').replace(']', '%5D').replace(' ', '%20')
    return mv_name

def get_movie_name(imdb, use_ajax=False):
    mv_name = None
    if use_ajax:
        imdb_url = 'https://v2.sg.media-imdb.com/suggestion/t/' + imdb + '.json'
        ajax_header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'v2.sg.media-imdb.com',
            'Origin': 'https://www.imdb.com',
            'Referer': 'https://www.imdb.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': USER_AGENTS_LIST[randint(0, len(USER_AGENTS_LIST) - 1)]
        }
        res = get_response(imdb_url, my_header=ajax_header)  # 搜索IMDB网站获取imdb对应的电影名称
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('Error: Unable to get IMDB ajax response!  ' + imdb_url)
            return None
        res_dict = json.loads(res.text)
        try:
            mv_name = res_dict['d'][0]['l']
        except Exception as err:
            print_and_log('Error: Unable to get movie name from ajax response!!!  ' + imdb_url)
            print_and_log(err)
            return None
        if mv_name == None or len(mv_name) == 0:
            print_and_log('Error: Unable to get movie name from ajax response!!!  ' + imdb_url)
            return None
        mv_name = ''.join(mv_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()  # 获取imdb对应的电影名称
        return mv_name
    else:
        imdb_url = 'https://www.imdb.com/title/' + imdb + '/'
        res = get_response(imdb_url, my_header=stander_header())  # 搜索IMDB网站获取imdb对应的电影名称
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('Error: Unable to get IMDB page response!  ' + imdb_url)
            return None
        html = etree.HTML(res.text)
        mv_name = html.xpath('//h1/text()')  # 获取电影名称
        if mv_name == None or len(mv_name) == 0:
            print_and_log('Error: Unable to get this movie name!  ' + imdb_url)
            return None
        mv_name = ''.join(mv_name).replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()  # 获取imdb对应的电影名称
        return mv_name

def search_movie(mv_name, imdb):
    header_yify = copy.deepcopy(stander_header())
    header_yify.update({'referer': 'https://yts-subs.com/'})
    ul = None
    lis = None
    count = 0
    res = None
    while count < 3:
        res = get_response('https://yts-subs.com/search/' + mv_name, my_header=header_yify)  # 使用yify网站进行搜索
        if res == None or res.status_code != 200:
            if res != None:
                print_and_log('Status Code is ' + str(res.status_code))
            print_and_log('Unable to search: << ' + mv_name + ' >> in yify.com  ' + str(count))
            time.sleep(5)
            count += 1
            continue
        html = etree.HTML(res.text)
        ul = html.xpath('//div[@class="col-md-12"]/div[@id="movie-browser-paginate"]/ul')  # 获取页码标签ul
        lis = html.xpath('//div[@class="col-md-12"]/ul[@class="media-list"]/li')  # 获取li标签
        if ul == None or lis == None or len(ul) == 0 or len(lis) == 0:
            print_and_log('Error: Unable to get all movies subtitles title!!!')
            time.sleep(5)
            count = 3
            break
        else:
            break
    if count >= 3 or ul == None or lis == None:
        return None, None
    else:
        return ul, lis

def download_subtitles_file(url, language, imdb, mv_name, subtitle_id):
    file_name = url.split('/')[-1]
    header_download = download_header()
    header_download.update({'referer': url.replace('.zip', '').replace('.rar', '').replace('.7z', '').replace('.tar', '')})
    res = get_response(url, my_header=download_header())  # 下载字幕文件压缩包
    if res == None or res.status_code != 200:
        if res != None:
            print_and_log('Status Code is ' + str(res.status_code))
        print_and_log('Error: Unable to download subtitles file!  ' + url)
        return None
    else:
        # print_and_log('********Download subtitle zip file succeed!!!*********')
        pass
    try:
        with open(subtitles_save_folder+'/tmp_y/'+file_name, 'wb') as f:       # 字幕zip包保存到E:/data/movies/tmp_y目录下
            f.write(res.content)
    except Exception as err:
        print_and_log('Error: Download subtitles file error!!!')
        print_and_log(err)
        return None
    try:
        zip_file = zipfile.ZipFile(subtitles_save_folder + '/tmp_y/' + file_name, 'r')  # 尝试使用zip打开压缩包
    except:
        try:
            zip_file = rarfile.RarFile(subtitles_save_folder + '/tmp_y/' + file_name, 'r')  # 不成功，则尝试使用rar打开压缩包
        except Exception as err:
            print_and_log('Error: Unable to open compress file!!!')
            print_and_log(err)
            return None
    for srt_file_name in zip_file.namelist():     # 遍历压缩包内所有文件的文件名称
        srt_file = file_name_translate(srt_file_name)     # 文件名转码去除乱码字符
        if srt_file == None:
            continue
        # 字幕文件临时存放路径
        srt_file = srt_file.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('<', '').replace('>', '').replace('|', '').replace('"', '')  # 去掉windows文件名不支持的字符
        srt_file = subtitles_save_folder + '/tmp_y/' + srt_file.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '').replace(' .', '.').replace('. ', '.').replace(' ', '-')  # 去掉文件名中的括号
        if not srt_file.endswith('.srt'):  # 不是.srt后缀，则不是字幕文件，跳过
            continue
        language_short = get_short_language(language)  # 获取语言缩写
        file_path = subtitles_save_folder + '/' + imdb + '/' + language.replace(' ', '_').replace('/', '_')  # 字幕文件最终存放路径
        if language_short == None:
            continue
        else:
            file_path = subtitles_save_folder + '/' + imdb + '/' + language_short  # 字幕文件最终存放路径
            if not os.path.exists(file_path):  # 创建语言文件夹，存放指定语言的字幕文件
                os.mkdir(file_path)
        try:
            data = zip_file.read(srt_file_name)      # 根据文件名从压缩包读取指定文件
            with open(srt_file, 'wb') as f:     # 文件写入磁盘
                f.write(data)
        except Exception as err:
            print_and_log('Error: Unable to read file from compress file and save to disk!!!')
            print_and_log(err)
            continue
        if not transform_encode(srt_file):     # 字幕文件不成功转码为utf-8，则放弃
            remove_file(srt_file)
            continue
        srt_file_new = copy.deepcopy(srt_file)     # 拷贝文件名称
        srt_file_new = srt_file_new.split('/')[-1]
        srt_file_new = file_path + '/' + subtitle_id + '-' + srt_file_new   # 新文件名绝对路径
        md5_this = None
        try:
            md5_this = hashlib.md5(data).hexdigest()
        except Exception as err:
            print_and_log('Error: 1---Unable to get file MD5!  '+srt_file)
            print_and_log(err)
            remove_file(srt_file)
            continue
        if md5_this == None:
            print_and_log('Error: 1---Unable to get file MD5!  ' + srt_file)
            remove_file(srt_file)
            continue
        result = []
        try:
            cursor.execute(select_sql, (imdb, language))      # 从数据库查询所有该电影、该语种的字幕文件路径
            result = cursor.fetchall()
        except Exception as err:
            print_and_log('Error: Unable to get data from DB!!! Unable to compare the subtitle file MD5 value!')
            print_and_log(err)
            remove_file(srt_file)
            continue
        is_exist = False    # 字幕文件是否已存在，默认为否
        for each_result in result:     # 分别比较已存在的文件与现在下载的文件的MD5值
            path = each_result[0]
            try:
                with open(path, 'rb') as f:           # 读取文件，获取其MD5值
                    md5_result = hashlib.md5(f.read()).hexdigest()
            except Exception as err:
                print_and_log('Error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                print_and_log(err)
                continue
            if md5_result == None:
                print_and_log('Error: 2---Unable to get file MD5, skip this file!  ' + each_result[0])
                continue
            if md5_this == md5_result:    # MD5相同，即为相同字幕文件
                is_exist = True
                # print_and_log('<< '+mv_name+' >> '+language+' '+season_and_episode+' '+srt_file_new.split('/')[-1]+' is existed on Disk!!!')
                break
        if not is_exist:   # 文件还没存在
            result = []
            try:
                cursor.execute(select_all_sql, (imdb, language, srt_file_new))     # 查询数据库是否已有该文件名称的电影记录
                result = cursor.fetchall()
            except Exception as err:
                print_and_log('Error: Unable to get data from DB!!! Unable to check this subtitle data existed or not on DB!')
                print_and_log(err)
                # remove_file(srt_file)
                # continue
            if len(result) == 0:     # 没有该文件名称的电视剧记录
                try:
                    source_name = shutil.move(srt_file, file_path)    # 移动字幕文件从E:/data/movies/tmp_y目录到E:/data/movies/ttxxxxxxx/en目录下
                except Exception as err:
                    print_and_log('Error: Unable move file to ' + file_path)
                    print_and_log(err)
                    remove_file(srt_file)
                    continue
                try:
                    os.rename(source_name, srt_file_new)   # 修改为新文件名
                except Exception as err:
                    print_and_log('Error: Unable to subtitle change file name!!!')
                    print_and_log(err)
                    remove_file(source_name)
                    continue
                try:
                    cursor.execute(insert_sql, (imdb, mv_name, language, language_short, srt_file_new))     # 写入数据库
                    conn.commit()
                except Exception as err:
                    print_and_log('Error: Unable insert data to DB!!!')
                    print_and_log(err)
                    # remove_file(srt_file_new)
                else:
                    print_and_log('********<< '+mv_name+' >> '+language+' '+srt_file_new.split('/')[-1]+' is successfully insert to DB!')
            else:      # 已有该文件名称的电影记录
                print_and_log('********<< ' + mv_name + ' >> '+language+' '+srt_file_new.split('/')[-1]+' is existed on DB!')
    try:
        zip_file.close()     # 关闭压缩文件
    except Exception as err:
        print_and_log('Error: Unable to close compress file!!!  '+subtitles_save_folder+'/tmp_y/'+file_name)
        print_and_log(err)
    try:
        for each_compress_file in os.listdir(subtitles_save_folder+'/tmp_y'):
            os.remove(subtitles_save_folder+'/tmp_y/'+each_compress_file)        # 删除tmp目录下压缩包和字幕文件，节约空间
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
            path_tmp += ('/'+subtitles_save_folder.split('/')[i])
            if not os.path.exists(path_tmp):
                os.mkdir(path_tmp)                          # 创建subtitles_save_folder各文件夹
    if not os.path.exists(subtitles_save_folder+'/tmp_y'):          # 创建存放压缩包的临时文件夹tmp
        os.mkdir(subtitles_save_folder+'/tmp_y')
    csv_file = open(csv_file_path, 'r')    # 读取csv文件
    imdb_str = csv_file.read()
    csv_file.close()
    imdb_list = imdb_str.split('\n')    # 获取csv文件中的所有电视剧imdb
    imdb_list_index = 0
    while imdb_list_index < len(imdb_list):
        print_and_log('IMDB now is '+imdb_list[imdb_list_index])
        print_and_log('IMDB schedule is ' + str(int((imdb_list_index + 1) / len(imdb_list) * 100)) + '%')
        mv_name = get_movie_name(imdb_list[imdb_list_index])
        ul = None
        lis = None
        if mv_name != None:
            ul, lis = search_movie(replace_special_char(mv_name), imdb_list[imdb_list_index])
            if ul == None or lis == None:
                mv_name = get_movie_name(imdb_list[imdb_list_index], use_ajax=True)
                if mv_name == None:
                    print_and_log('Error: Unable to get movie name!')
                    imdb_list_index += 1
                    continue
        else:
            mv_name = get_movie_name(imdb_list[imdb_list_index], use_ajax=True)
            if mv_name == None:
                print_and_log('Error: Unable to get movie name!')
                imdb_list_index += 1
                continue
        ul, lis = search_movie(replace_special_char(mv_name), imdb_list[imdb_list_index])
        if ul == None or lis == None:
            imdb_list_index += 1
            continue
        max_page = 1
        page_a = ul[0].xpath('./li/a')
        if page_a == None or len(page_a) == 0:
            # print_and_log('Unable to get max page number!!!')
            pass
        else:
            try:
                page_tmp = page_a[-1].xpath('./@href')
            except:
                pass
            else:
                if len(page_tmp) != 0:
                    max_page = page_tmp[0].split('=')[-1]       # 获取最大页码数
        is_not_found = True
        for each_page in range(int(max_page)):      # 遍历所有页码的页面
            header_yify = copy.deepcopy(stander_header())
            header_yify.update({'referer': 'https://yts-subs.com/'})
            if each_page > 0:        # 第2页开始在循环内获取该页码的页面数据
                lis = None
                count = 0
                while count < 3:
                    res = get_response('https://yts-subs.com/search/' + mv_name + '?page=' + str(each_page+1), my_header=header_yify)  # 使用yify网站进行搜索
                    if res == None or res.status_code != 200:
                        if res != None:
                            print_and_log('Status Code is ' + str(res.status_code))
                        print_and_log('Error: Unable to search: << ' + mv_name + ' >> page '+str(each_page+1)+' in yify.com  ' + str(count))
                        time.sleep(5)
                        count += 1
                        continue
                    html = etree.HTML(res.text)
                    lis = html.xpath('//div[@class="col-md-12"]/ul[@class="media-list"]/li')  # 获取li标签
                    if lis == None or len(lis) == 0:
                        print_and_log('Error: Unable to get page ' + str(each_page+1) + ' all movies subtitles title!!!  ' + str(count))
                        time.sleep(5)
                        count += 1
                        continue
                    else:
                        break
                if count >= 3 or lis == None:
                    continue
            for each_li in lis:     # 遍历该页面所有的电影标题
                href = each_li.xpath('./div[@class="media-body"]/a/@href')    # 获取该电影字幕列表页面URL
                if href == None or len(href) == 0:
                    print_and_log('Error: unable to get imdb from movie title!!!')
                    continue
                imdb = href[0].split('/')[-1]           # 从URL中获取imdb
                if imdb != imdb_list[imdb_list_index]:  # 检测是否是指定的imdb，不是则跳过
                    continue
                is_not_found = False
                url = 'https://yts-subs.com' + href[0]
                header_yify.clear()
                header_yify = copy.deepcopy(stander_header())
                if each_page == 0:
                    header_yify.update({'referer': 'https://yts-subs.com/search/'+mv_name})
                else:
                    header_yify.update({'referer': 'https://yts-subs.com/search/' + mv_name + '?page=' + str(each_page+1)})
                res = get_response(url, my_header=header_yify)        # 打开该电影的字幕列表页面
                if res == None or res.status_code != 200:
                    if res != None:
                        print_and_log('Status Code is ' + str(res.status_code))
                    print_and_log('Error: Unable to open subtitles detail page!!!')
                    continue
                html = etree.HTML(res.text)
                trs = html.xpath('//div[@class="table-responsive"]/table/tbody/tr')   # 获取字幕列表元素
                for each_tr in trs:        # 遍历每一个字幕标题
                    language = each_tr.xpath('./td[2]/span[@class="sub-lang"]/text()')     # 获取语言
                    if language == None or len(language) == 0:
                        continue
                    language = language[0].replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip().lower()
                    if 'big' in language:
                        continue
                    download_page_url = each_tr.xpath('./td[3]/a/@href')           # 获取字幕下载详情页面地址
                    if download_page_url == None or len(download_page_url) == 0:
                        continue
                    download_page_url = 'https://yts-subs.com' + download_page_url[0]
                    subtitle_id = download_page_url.split('-')[-1]
                    header_yify.clear()
                    header_yify = copy.deepcopy(stander_header())
                    header_yify.update({'referer': url})
                    res = get_response(download_page_url, my_header=header_yify)    # 打开字幕下载详情页面
                    if res == None or res.status_code != 200:
                        if res != None:
                            print_and_log('Status Code is ' + str(res.status_code))
                        print_and_log('Error: Unable to open subtitles download page!!!')
                        continue
                    html = etree.HTML(res.text)
                    download_url = html.xpath('//a[@class="btn-icon download-subtitle"]/@href')    # 获取字幕下载地址
                    if download_url == None or len(download_url) == 0:
                        print_and_log('Error: Unable to get subtitles download url!!!')
                        continue
                    if not os.path.exists(subtitles_save_folder + '/' + imdb_list[imdb_list_index]):  # 创建该电影的文件夹
                        os.mkdir(subtitles_save_folder + '/' + imdb_list[imdb_list_index])
                    download_subtitles_file(download_url[0], language, imdb_list[imdb_list_index], mv_name, subtitle_id)
        if is_not_found:
            print_and_log('Error: << '+mv_name+' >>  '+imdb_list[imdb_list_index]+' Not Found !!!')
        imdb_list_index += 1
    print_and_log('-----------------Finish All!--------------------')

if __name__ == '__main__':
    main()
    cursor.close()
    conn.close()
