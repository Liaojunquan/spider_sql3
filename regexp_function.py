# -*- coding: utf-8 -*-
import re
import copy


delete_str = ['1080p', '1080', '720p', '720', '1920', '640p', '640', '540p', '540', '480p', '480', '450p',
              '450', '360p', '360', '2160p', '2160', '1280']
digit_dict = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
              'six': '6', 'seven': '7', 'eight': '8', 'night': '9', 'ten': '10'}
season_re_str = r'(sesong|season|series|saeson|Sezoni)'
episode_re_str = r'(episodes|episode|episod|Extra|Part|afsnit|Disc|Episodi|Trailer|Teaser|Minisode)'


def delete_special_str(file_name, title):
    name = copy.deepcopy(file_name)
    if title.isdigit():      # 电视剧名称为纯数字
        if len(re.findall('[^a-zA-Z][se][\. _-]{0,2}'+title+'\D', file_name)) == 0 and len(re.findall('[SE][\. _-]{0,2}'+title+'\D', file_name)) == 0 and\
                len(re.findall('(season|series|sesong|episodes|episode|episod)[\. _-]?'+title+'\D', file_name, re.IGNORECASE)) == 0:  # 跳过Exx、Episodexx、Sxx
            name = name.replace(title, '-', 1)                  # 去掉电视剧名称数字字符的干扰
    elif '/' != title and len(re.findall('\d+', title)) > 0:   # 电视剧名称含有数字
        title_reg = ''
        for c in title:
            if c == ' ' or c == '.' or c == '_' or c == '-' or c == ':':   # 替换特殊字符
                title_reg += '[\\. _-]'
            elif c == "'":
                title_reg += '[\\. _-]?'
            else:
                title_reg += c
        title_reg += '[\\. _-]'
        title_reg = title_reg.replace('[\\. _-][\\. _-][\\. _-]', '[\\. _-]{1,3}').replace('[\\. _-][\\. _-]', '[\\. _-]{1,2}')
        r = re.findall(title_reg, file_name, re.IGNORECASE)
        if len(r) > 0:
            for e in r:
                name = name.replace(e, '-')  # 去掉电视剧名称字符的干扰
        else:
            title_digit = re.findall('\d+', title)
            for td in title_digit:
                if len(td) > 1 and len(re.findall('[^a-zA-Z][se][\. _-]{0,2}'+td+'\D', file_name)) == 0 and len(re.findall('[SE][\. _-]{0,2}'+td+'\D', file_name)) == 0 and \
                        len(re.findall('(season|series|sesong|episodes|episode|episod)[\. _-]?'+td+'\D', file_name, re.IGNORECASE)) == 0:  # 跳过Exx、Episodexx、Sxx
                    name = name.replace(td, '-', 1)  # 去掉电视剧名称数字字符的干扰
    r = re.findall('[Hx]?\.?26[45]', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '-')  # 去掉'H.264'字符的干扰
    r = re.findall('UTF-?8', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉'UTF-8'字符的干扰
    for each_str in delete_str:
        name = name.replace(each_str, '')
    r = re.findall('\D(\d+[KM]B)', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉'300MB'字符的干扰
    r = re.findall('\D(\d{1,2}\.\d+GB)', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉'1.34GB'字符的干扰
    r = re.findall('\D(1[89]\d\d)\D', file_name)
    for e in r:
        name = name.replace(e, '-')         # 去掉年份19xx字符的干扰
    r = re.findall('\D(2[0]\d\d)\D', file_name)
    for e in r:
        name = name.replace(e, '-')  # 去掉年份20xx字符的干扰
    r = re.findall('([\. _-]\d[HT][DV])[\. _-]', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉xHD或xTV字符的干扰
    if len(re.findall('\d+', file_name)) > 1:
        r = re.findall('Chapter-\d+', file_name, re.IGNORECASE)
        for e in r:
            name = name.replace(e, '')  # 去掉Chapter-15字符的干扰
    r = re.findall('((23.976|24|25)fps)', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e[0], '-')  # 去掉帧率字符的干扰
    r = re.findall('(season|series|sesong|episodes|episode|episod|saeson)[\. _-]{1,3}(One|Two|Three|Four|Five|Six|Seven|Eight|Neight|Ten)\D', file_name, re.IGNORECASE)
    if len(r) == 1:
        name = name.replace(r[0][1], digit_dict[r[0][1].lower()])   # 将英文数字转为数字字符
    while 1:
        r = re.findall('\D0+\D', name)
        if len(r) == 0:
            break
        for e in r:
            name = name.replace(e, e.replace('0', '-'))  # 去掉无意义的0干扰如：S0、E0、000、S000等
    r = re.findall('0000\d+', file_name)
    for e in r:
        name = name.replace(e, '-')  # 去掉无意义数字字符的干扰
    r = re.findall('tracke?s?\d+', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉track29字符的干扰
    return name


def return_season_and_episode(se, epi):
    if type(se[0]) is tuple:
        if len(se[0]) == 2:
            s = int(se[0][0])
        elif len(se[0]) == 3:
            s = int(se[0][1])
        else:
            return False
    else:
        s = int(se[0])
    if type(epi[0]) is tuple:
        if len(epi[0]) == 2:
            e = int(epi[0][1])
        elif len(epi[0]) == 3:
            e = int(epi[0][2])
        else:
            return False
    else:
        e = int(epi[0])
    if s < 10:
        season = '0' + str(s)
    elif s > 50:
        return False
    else:
        season = str(s)
    if e < 10:
        episode = '0' + str(e)
    elif e > 90:
        return False
    else:
        episode = str(e)
    return 'S' + season + 'E' + episode


def get_season_and_episode(name_raw, title='/'):      # 使用正则表达式获取字幕文件名上的季和集信息
    name = delete_special_str(name_raw, title)
    season = None
    episode = None
    if len(re.findall('[SE](\d{5,12})\D', name, re.IGNORECASE)) > 0:
        flag = False
        re_tmp = re.findall('(E\d{1,2}(1[89]\d\d)\D)', name, re.IGNORECASE)
        if len(re_tmp) == 1:
            name = name.replace(re_tmp[0][0], re_tmp[0][0].replace(re_tmp[0][1], ''))
            flag = True
        re_tmp = re.findall('(E\d{1,2}(20\d\d)\D)', name, re.IGNORECASE)
        if len(re_tmp) == 1:
            name = name.replace(re_tmp[0][0], re_tmp[0][0].replace(re_tmp[0][1], ''))
            flag = True
        if flag is False:
            re_tmp = re.findall('([SE]\d{5,12})\D', name, re.IGNORECASE)
            for each in re_tmp:
                name = name.replace(each, '')

    if len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            if len(episode[0]) == 3:     # 特殊处理S01Exxx这类
                s = str(int(season[0]))
                e = episode[0]
                if s == e[:e.find(s)+1]:
                    return return_season_and_episode(season, [e[e.find(s)+1:]])  # E106中season为1去掉
                elif '0' == e[0]:
                    return return_season_and_episode(season, [e[1:]])   # E011中0去掉
            else:
                return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _-].*[\. _-]\d{1,3} +)', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _-].*[\. _-]\d{1,3} +', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _-].*[\. _-](\d{1,3}) +', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](EP?i?X?s?[\. _-]?\d{1,3}[\. _x-]{0,2}Se?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,3})[\. _x-]{0,2}Se?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        season = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,3}[\. _x-]{0,2}Se?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](EP?i?X?s?[\. _-]?\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,3})[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        season = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,3})\D', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,3})[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'((episodes|episode|episod)[\. _-]?\d{1,3}[\. _x-]{0,2}'+season_re_str+r'[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'(episodes|episode|episod)[\. _-]?(\d{1,3})[\. _x-]{0,2}'+season_re_str+r'[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        season = re.findall(r'(episodes|episode|episod)[\. _-]?\d{1,3}[\. _x-]{0,2}'+season_re_str+r'[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,3})[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            pass
            # return None
        elif int(episode[0][2]) == 0:
            pass
            # return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    if len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3})\D', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,3})[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,3}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'((episodes|episode|episod)[\. _-]?\d{1,3}[\. _x-]{0,2}Se?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'(episodes|episode|episod)[\. _-]?(\d{1,3})[\. _x-]{0,2}Se?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        season = re.findall(r'(episodes|episode|episod)[\. _-]?\d{1,3}[\. _x-]{0,2}Se?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3})\D', name, re.IGNORECASE)) > 0:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,2})[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](EP?i?X?s?[\. _-]?\d{1,2}[\. _x-]{0,2}Se?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,2})[\. _x-]{0,2}Se?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        season = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2}[\. _x-]{0,2}Se?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,2}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2})\D', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,2})[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2}\D', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,2}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,2})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[\. _x-](M[\. _-]?\d{1,2}[\. _x-]{0,2}T[\. _-]?\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'[\. _x-]M[\. _-]?(\d{1,2})[\. _x-]{0,2}T[\. _-]?\d{1,2}\D.*', name)
        episode = re.findall(r'[\. _x-]M[\. _-]?\d{1,2}[\. _x-]{0,2}T[\. _-]?(\d{1,2})\D.*', name)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{4}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,2})[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{4}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?(\d{4})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        elif int(episode[0][:2]) != 0:
            return return_season_and_episode(season, [episode[0][:2]])
        elif int(episode[0][2:]) != 0:
            return return_season_and_episode(season, [episode[0][2:]])
        else:
            return False
    elif len(re.findall(r'(Season[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'Season[\. _-]?(\d{1,2})[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'Season[\. _-]?\d{1,2}[\. _x-]{0,2}[ET]P?i?X?s?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](EP?i?X?s?[\. _-]?\d{1,2}[\. _x-]{0,2}Season[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,2})[\. _x-]{0,2}Season[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        season = re.findall(r'[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2}[\. _x-]{0,2}Season[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(Season[\. _-]?\d{1,2}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2})\D', name, re.IGNORECASE)) == 1:
        season = re.findall(r'Season[\. _-]?(\d{1,2})[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?\d{1,2}\D', name, re.IGNORECASE)
        episode = re.findall(r'Season[\. _-]?\d{1,2}[\. _x-]{0,2}.*[^a-zA-Z]EP?i?X?s?[\. _-]?(\d{1,2})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,2})[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'((episodes|episode|episod)[\. _-]?\d{1,2}[\. _x-]{0,2}'+season_re_str+r'[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'(episodes|episode|episod)[\. _-]?(\d{1,2})[\. _x-]{0,2}'+season_re_str+r'[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        season = re.findall(r'(episodes|episode|episod)[\. _-]?\d{1,2}[\. _x-]{0,2}'+season_re_str+r'[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,2})[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            pass
            # return None
        elif int(episode[0][2]) == 0:
            pass
            # return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    if len(re.findall(r'('+season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2})\D', name, re.IGNORECASE)) > 0:
        season = re.findall(season_re_str+r'[\. _-]?(\d{1,2})[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D', name, re.IGNORECASE)
        episode = re.findall(season_re_str+r'[\. _-]?\d{1,2}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,2})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][1]) == 0 and int(episode[0][2]) != 0):
            return None
        elif int(episode[0][2]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,2})[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,2}[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'((episodes|episode|episod)[\. _-]?\d{1,2}[\. _x-]{0,2}Se?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'(episodes|episode|episod)[\. _-]?(\d{1,2})[\. _x-]{0,2}Se?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        season = re.findall(r'(episodes|episode|episod)[\. _-]?\d{1,2}[\. _x-]{0,2}Se?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,2}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2})\D', name, re.IGNORECASE)) > 0:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,2})[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?\d{1,2}\D', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,2}[\. _x-]{0,2}.*[\. _x-]{0,2}'+episode_re_str+r'[\. _-]?(\d{1,2})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(S\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'S(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0:2]], [season_and_episode[0][2:]])
    elif len(re.findall(r'([^a-zA-Z]s\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'[^a-zA-Z]s(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0:2]], [season_and_episode[0][2:]])
    elif len(re.findall(r'([^a-zA-Z]s\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'[^a-zA-Z]s(\d{3})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0]], [season_and_episode[0][1:]])
    elif len(re.findall(r'(S\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'S(\d{3})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0]], [season_and_episode[0][1:]])
    elif len(re.findall(r'[^a-zA-Z](Se?[\. _-]?\d{1,3}[\. _x-]{1,2}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'[^a-zA-Z]Se?[\. _-]?(\d{1,3})[\. _x-]{1,2}\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'[^a-zA-Z]Se?[\. _-]?\d{1,3}[\. _x-]{1,2}(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'([\. _-]ep?[\. _-]?\d{1,3}[\. _x-]{0,2}ep?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        return None
    elif len(re.findall(r'([\. _-]ep?[\. _-]?\d{1,3}[\. _x-]{1,3}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        return None
    elif len(re.findall(r'(\D\d{1,2}[\. _x-]{0,2}ep?i?\d{1,2}[\. _-]).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'\D(\d{1,2})[\. _x-]{0,2}ep?i?\d{1,2}[\. _-].*', name, re.IGNORECASE)
        episode = re.findall(r'\D\d{1,2}[\. _x-]{0,2}ep?i?(\d{1,2})[\. _-].*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(^\d{1,2}[\. _x-]{0,2}ep?i?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'^(\d{1,2})[\. _x-]{0,2}ep?i?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'^\d{1,2}[\. _x-]{0,2}ep?i?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(^\d{1,3}[\._xX-]?[\._xX-][\._xX-]?\d{1,3}\D).*', name)) == 1:
        season = re.findall(r'^(\d{1,3})[\._xX-]?[\._xX-][\._xX-]?\d{1,3}\D.*', name)
        episode = re.findall(r'^\d{1,3}[\._xX-]?[\._xX-][\._xX-]?(\d{1,3})\D.*', name)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    elif len(re.findall(r'(\D\d{1,3}[\._xX-]?[\._xX-][\._xX-]?\d{1,3}\D).*', name)) == 1:
        season = re.findall(r'\D(\d{1,3})[\._xX-]?[\._xX-][\._xX-]?\d{1,3}\D.*', name)
        episode = re.findall(r'\D\d{1,3}[\._xX-]?[\._xX-][\._xX-]?(\d{1,3})\D.*', name)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    if len(re.findall(r'(^\d{1,3}[\. _-].*(sesong|season|series|saeson)[\. _-]?\d{1,3}\D)', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'^(\d{1,3})[\. _-].*(sesong|season|series|saeson)[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        season = re.findall(r'^\d{1,3}[\. _-].*(sesong|season|series|saeson)[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][1]) == 0 and int(episode[0][0]) != 0):
            return None
        elif int(episode[0][0]) == 0:
            return False
        else:
            return return_season_and_episode([season[0][1]], [episode[0][0]])
    elif len(re.findall(r'\D(\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D)', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'\D(\d{1,3})[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        season = re.findall(r'\D\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    if len(re.findall(r'^(\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D)', name, re.IGNORECASE)) > 0:
        episode = re.findall(r'^(\d{1,3})[\. _-].*[^a-zA-Z]Se?[\. _-]?\d{1,3}\D', name, re.IGNORECASE)
        season = re.findall(r'^\d{1,3}[\. _-].*[^a-zA-Z]Se?[\. _-]?(\d{1,3})\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    if len(re.findall(r'([\. _-]\d{1,2}[a-z]{2}[\. _-]{1,3}Season[\. _-]{1,3}\d{1,3}\D)', name, re.IGNORECASE)) > 0:   # Crunchyroll-Golden-Kamuy-2nd-Season--12-English-us.ass
        episode = re.findall(r'[\. _-]\d{1,2}[a-z]{2}[\. _-]{1,3}Season[\. _-]{1,3}(\d{1,3})\D', name, re.IGNORECASE)
        season = re.findall(r'[\. _-](\d{1,2})[a-z]{2}[\. _-]{1,3}Season[\. _-]{1,3}\d{1,3}\D', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            result = return_season_and_episode(season, episode)
            if result is not False:
                return result
    if len(re.findall(r'((sesong|season|series|saeson)[\. _-]{0,2}\d{3,4}\D)', name, re.IGNORECASE)) == 1:
        season_and_episode = re.findall(r'(sesong|season|series|saeson)[\. _-]{0,2}(\d{3,4})\D', name, re.IGNORECASE)
        if len(season_and_episode) != 1 or \
                (int(season_and_episode[0][1][:-2]) == 0 and int(season_and_episode[0][1][-2:]) != 0):
            pass
        elif int(season_and_episode[0][1][-2:]) == 0:
            pass
        else:
            return return_season_and_episode([season_and_episode[0][1][:-2]], [season_and_episode[0][1][-2:]])
    if len(re.findall(r'(\w+s[\. _-]?\d{3,4}[\. _x-]{0,2}\w+).*', name, re.IGNORECASE)) == 1:
        season_and_episode = re.findall(r'\w+s[\. _-]?(\d{3,4})[\. _x-]{0,2}\w+.*', name, re.IGNORECASE)
        if len(season_and_episode) != 1 or \
                (int(season_and_episode[0][:-2]) == 0 and int(season_and_episode[0][-2:]) != 0):
            pass
            # return None
        elif int(season_and_episode[0][-2:]) == 0:
            pass
            # return False
        else:
            return return_season_and_episode([season_and_episode[0][:-2]], [season_and_episode[0][-2:]])
    elif len(re.findall(r'^e[\. _-]?\d{3,4}\D.*', name, re.IGNORECASE)) == 1:
        return False
    elif len(re.findall(r'[^a-zA-Z]e[\. _-]?\d{3,4}\D.*', name, re.IGNORECASE)) == 1:
        return False
    elif len(re.findall(r'(^\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'^(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0:2]], [season_and_episode[0][2:]])
    elif len(re.findall(r'(\D\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'\D(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0:2]], [season_and_episode[0][2:]])
    elif len(re.findall(r'(^\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'^(\d{3})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0]], [season_and_episode[0][1:]])
    elif len(re.findall(r'(\D\d{3}\D).*', name)) > 0:
        season_and_episode = re.findall(r'\D(\d{3})\D.*', name)
        if len(season_and_episode) == 0 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return return_season_and_episode([season_and_episode[0][0]], [season_and_episode[0][1:]])
    else:
        return None


def episode_return(epi):
    e = int(epi[0])
    if e < 10:
        episode = '0' + str(e)
    elif e > 90:
        return None
    else:
        episode = str(e)
    return 'E' + episode


def get_episode(name_raw, title='/'):    # 仅获取字幕文件名中的集的信息
    name = delete_special_str(name_raw, title)
    episode = None
    if len(re.findall('(episodes?[\. _x-]{0,2}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall('episodes?[\. _x-]{0,2}(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('^(ep?x?s?[\. _x-]{0,2}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall('^ep?x?s?[\. _x-]{0,2}(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('[^a-zA-Z](ep?x?s?[\. _x-]{0,2}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall('[^a-zA-Z]ep?x?s?[\. _x-]{0,2}(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('^(\d{1,2}[_-]?[\.xX][_-]?\d{1,2}\D).*', name)) == 1:
        episode = re.findall('^\d{1,2}[_-]?[\.xX][_-]?(\d{1,2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('[^a-zA-Z](\d{1,2}[_-]?[\.xX][_-]?\d{1,2}\D).*', name)) == 1:
        episode = re.findall('[^a-zA-Z]\d{1,2}[_-]?[\.xX][_-]?(\d{1,2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('^(S|season|series|sesong)[\. _-]{0,2}\d{1,3}[\. _-]', name, re.IGNORECASE)) == 1:
        return None
    elif len(re.findall('[^a-zA-Z](S|season|series|sesong)[\. _-]{0,2}\d{1,3}[\. _-]', name, re.IGNORECASE)) == 1:
        return None
    elif len(re.findall('[\. _-]\d{1,2}of\d{1,2}[\. _-]', name, re.IGNORECASE)) == 1:
        episode = re.findall('[\. _-](\d{1,2})of\d{1,2}[\. _-]', name, re.IGNORECASE)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{4}[\. _-]).*', name)) == 1:
        episode = re.findall('^\d\d(\d\d)[\. _-].*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{4}[\. _-])', name)) == 1:
        episode = re.findall('\D\d\d(\d\d)[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{3}[\. _-]).*', name)) == 1:
        episode = re.findall('^\d(\d\d)[\. _-].*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{3}[\. _-])', name)) == 1:
        episode = re.findall('\D\d(\d\d)[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{2}[\. _-]).*', name)) == 1:
        episode = re.findall('^(\d{2})[\. _-].*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{2}[\. _-])', name)) == 1:
        episode = re.findall('\D(\d{2})[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{2}[vV]\d{1,2}[\. _-])', name)) == 1:
        episode = re.findall('\D(\d{2})[vV]\d{1,2}[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d[\. _-])', name)) == 1:
        episode = re.findall('^(\d)[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return 'E0' + episode[0]
    elif len(re.findall('\D\d[\. _-]', name)) == 1:
        episode = re.findall('\D(\d)[\. _-]', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return 'E0' + episode[0]
    else:
        return None
