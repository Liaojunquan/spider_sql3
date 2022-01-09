# -*- coding: utf-8 -*-
import re
import copy

delete_str = ['1080p', '1080', '720p', '720', '1920', '640p', '640', '540p', '540', '480p', '480', '450p',
              '450', '360p', '360']


def delete_special_str(file_name, title):
    name = copy.deepcopy(file_name)
    name = name.replace(title, '')
    r = re.findall('[Hx]\.?26[45]', file_name, re.IGNORECASE)
    for e in r:
        name = name.replace(e, '')  # 去掉'H.264'字符的干扰
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
        name = name.replace(e, '')         # 去掉年份19xx字符的干扰
    r = re.findall('\D(2[0]\d\d)\D', file_name)
    for e in r:
        name = name.replace(e, '')  # 去掉年份20xx字符的干扰
    return name


def return_season_and_episode(se, epi, is_tuple=False):
    if is_tuple:
        s = int(se[0][0])
        e = int(epi[0][1])
    else:
        s = int(se[0])
        e = int(epi[0])
    if s < 10:
        season = '0' + str(s)
    elif s > 50:
        return False
    else:
        season = str(s)
    if e < 10:
        episode = '0' + str(e)
    elif e > 72:
        return False
    else:
        episode = str(e)
    return 'S' + season + 'E' + episode


def get_season_and_episode(name_raw, title='/'):      # 使用正则表达式获取字幕文件名上的季和集信息
    name = delete_special_str(name_raw, title)
    season = None
    episode = None
    if len(re.findall('[SE](\d{5,12})\D', name, re.IGNORECASE)) > 0:
        return False
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
    if len(re.findall(r'(S[\. _-]?\d{1,3}[\. _x-]{0,2}EP?s?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'S[\. _-]?(\d{1,3})[\. _x-]{0,2}EP?s?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'S[\. _-]?\d{1,3}[\. _x-]{0,2}EP?s?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(sesong[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'sesong[\. _-]?(\d{1,3})[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'sesong[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(season[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'season[\. _-]?(\d{1,3})[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'season[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(season[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)?[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'season[\. _-]?(\d{1,3})[\. _x-]{0,2}(episodes|episode)?[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'season[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)?[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(S[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'S[\. _-]?(\d{1,3})[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,3}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'S[\. _-]?\d{1,3}[\. _x-]{0,2}(episodes|episode)[\. _-]?(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(season) == 0 or len(episode) == 0 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(S[\. _-]?\d{1,2}[\. _x-]{0,2}EP?s?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'S[\. _-]?(\d{1,2})[\. _x-]{0,2}EP?s?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'S[\. _-]?\d{1,2}[\. _x-]{0,2}EP?s?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(S[\. _-]?\d{1,2}[\. _x-]{0,2}EP?s?[\. _-]?\d{4}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'S[\. _-]?(\d{1,2})[\. _x-]{0,2}EP?s?[\. _-]?\d{4}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'S[\. _-]?\d{1,2}[\. _x-]{0,2}EP?s?[\. _-]?(\d{4})\D.*', name, re.IGNORECASE)
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
#    elif len(re.findall(r'(S[\. _-]?\d{1,2}[\. _x-]{0,2}E?P?s?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
#        season = re.findall(r'S[\. _-]?(\d{1,2})[\. _x-]{0,2}E?P?s?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
#        episode = re.findall(r'S[\. _-]?\d{1,2}[\. _x-]{0,2}E?P?s?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
#        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
#            return None
#        elif int(episode[0]) == 0:
#            return False
#        else:
#            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(season[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'season[\. _-]?(\d{1,2})[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'season[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(season[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)?[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'season[\. _-]?(\d{1,2})[\. _x-]{0,2}(episodes|episode)?[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'season[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)?[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'(S[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,2}\D).*', name, re.IGNORECASE)) > 0:
        season = re.findall(r'S[\. _-]?(\d{1,2})[\. _x-]{0,2}(episodes|episode)[\. _-]?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'S[\. _-]?\d{1,2}[\. _x-]{0,2}(episodes|episode)[\. _-]?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0][0]) == 0 and int(episode[0][1]) != 0):
            return None
        elif int(episode[0][1]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode, True)
    elif len(re.findall(r'([\. _-][sS]\d{4}[\. _-]).*', name)) == 1:
        season_and_episode = re.findall(r'[\. _-][sS](\d{4})[\. _-].*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return 'S' + season_and_episode[0][0:2] + 'E' + season_and_episode[0][2:]
    elif len(re.findall(r'([\. _-][sS]\d{3}[\. _-]).*', name)) == 1:
        season_and_episode = re.findall(r'[\. _-][sS](\d{3})[\. _-].*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return 'S0' + season_and_episode[0][0] + 'E' + season_and_episode[0][1:]
    elif len(re.findall(r'(\D\d{1,2}[\. _x-]{0,2}ep?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'\D(\d{1,2})[\. _x-]{0,2}ep?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'\D\d{1,2}[\. _x-]{0,2}ep?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(^\d{1,2}[\. _x-]{0,2}ep?\d{1,2}\D).*', name, re.IGNORECASE)) == 1:
        season = re.findall(r'^(\d{1,2})[\. _x-]{0,2}ep?\d{1,2}\D.*', name, re.IGNORECASE)
        episode = re.findall(r'^\d{1,2}[\. _x-]{0,2}ep?(\d{1,2})\D.*', name, re.IGNORECASE)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(^\d{1,2}[\.xX-]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'^(\d{1,2})[\.xX-]\d{1,2}\D.*', name)
        episode = re.findall(r'^\d{1,2}[\.xX-](\d{1,2})\D.*', name)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(\D\d{1,2}[\.xX-]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'\D(\d{1,2})[\.xX-]\d{1,2}\D.*', name)
        episode = re.findall(r'\D\d{1,2}[\.xX-](\d{1,2})\D.*', name)
        if len(season) != 1 or len(episode) != 1 or (int(season[0]) == 0 and int(episode[0]) != 0):
            return None
        elif int(episode[0]) == 0:
            return False
        else:
            return return_season_and_episode(season, episode)
    elif len(re.findall(r'(^\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'^(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return 'S' + season_and_episode[0][0:2] + 'E' + season_and_episode[0][2:]
    elif len(re.findall(r'(\D\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'\D(\d{4})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0:2] == '00' and season_and_episode[0][2:] != '00'):
            return None
        elif season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19' or season_and_episode[0][0:2] == '20':
            return False
        else:
            return 'S' + season_and_episode[0][0:2] + 'E' + season_and_episode[0][2:]
    elif len(re.findall(r'(^\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'^(\d{3})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return 'S0' + season_and_episode[0][0] + 'E' + season_and_episode[0][1:]
    elif len(re.findall(r'(\D\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'\D(\d{3})\D.*', name)
        if len(season_and_episode) != 1 or (season_and_episode[0][0] == '0' and season_and_episode[0][1:] != '00'):
            return None
        elif season_and_episode[0][1:] == '00':
            return False
        else:
            return 'S0' + season_and_episode[0][0] + 'E' + season_and_episode[0][1:]
    else:
        return None


def episode_return(epi):
    e = int(epi[0])
    if e < 10:
        episode = '0' + str(e)
    elif e > 72:
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
    elif len(re.findall('(ep?s?[\. _x-]{0,2}\d{1,3}\D).*', name, re.IGNORECASE)) == 1:
        episode = re.findall('ep?s?[\. _x-]{0,2}(\d{1,3})\D.*', name, re.IGNORECASE)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('^(\d{1,2}[\.xX]\d{1,2}\D).*', name)) == 1:
        episode = re.findall('^\d{1,2}[\.xX](\d{1,2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{1,2}[\.xX]\d{1,2}\D).*', name)) == 1:
        episode = re.findall('\D\d{1,2}[\.xX](\d{1,2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{4}\D).*', name)) == 1:
        episode = re.findall('^\d\d(\d\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{4}\D).*', name)) == 1:
        episode = re.findall('\D\d\d(\d\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{3}\D).*', name)) == 1:
        episode = re.findall('^\d(\d\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{3}\D).*', name)) == 1:
        episode = re.findall('\D\d(\d\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d{2}\D).*', name)) == 1:
        episode = re.findall('^(\d{2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(\D\d{2}\D).*', name)) == 1:
        episode = re.findall('\D(\d{2})\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return episode_return(episode)
    elif len(re.findall('(^\d\D).*', name)) == 1:
        episode = re.findall('^(\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return 'E0' + episode[0]
    elif len(re.findall('\D(\d\D).*', name)) == 1:
        episode = re.findall('\D(\d)\D.*', name)
        if len(episode) == 0 or int(episode[0]) == 0:
            return None
        else:
            return 'E0' + episode[0]
    else:
        return None
