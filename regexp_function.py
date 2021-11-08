# -*- coding: utf-8 -*-
import re


def get_season_and_episode(name):      # 使用正则表达式获取字幕文件名上的季和集信息
    season = None
    episode = None
    if len(re.findall(r'.*([sS][\. _-]\d{1,2}[\. _xX-][eE][\. _-]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*[sS][\. _-](\d{1,2})[\. _xX-][eE][\. _-]\d{1,2}\D.*', name)
        episode = re.findall(r'.*[sS][\. _-]\d{1,2}[\. _xX-][eE][\. _-](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason[\. _-]\d{1,2}[\. _xX-][Ee]pisode[\. _-]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason[\. _-](\d{1,2})[\. _xX-][Ee]pisode[\. _-]\d{1,2}\D.*', name)
        episode = re.findall(r'.*[Ss]eason[\. _-]\d{1,2}[\. _xX-][Ee]pisode[\. _-](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason\d{1,2}[Ee]pisode\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason(\d{1,2})[Ee]pisode\d{1,2}\D.*', name)
        episode = re.findall(r'.*[Ss]eason\d{1,2}[Ee]pisode(\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*([Ss]eason\d{1,2}[\. _xX-][Ee]pisode\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*[Ss]eason(\d{1,2})[\. _xX-][Ee]pisode\d{1,2}\D.*', name)
        episode = re.findall(r'.*[Ss]eason\d{1,2}[\. _xX-][Ee]pisode(\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*(\D\d{1,2}[eE]\d{1,2}\D).*', name)) == 1 or len(re.findall(r'(^\d{1,2}[eE]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*(\d{1,2})[eE]\d{1,2}\D.*', name)
        episode = re.findall(r'.*\d{1,2}[eE](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*(\D\d{1,2}[eE][pP]\d{1,2}\D).*', name)) == 1 or len(re.findall(r'(^\d{1,2}[eE][pP]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*(\d{1,2})[eE][pP]\d{1,2}\D.*', name)
        episode = re.findall(r'.*\d{1,2}[eE][pP](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*(\D\d{1,2}[\. _xX-][eE]\d{1,2}\D).*', name)) == 1 or len(re.findall(r'(^\d{1,2}[\. _xX-][eE]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*(\d{1,2})[\. _xX-][eE]\d{1,2}\D.*', name)
        episode = re.findall(r'.*\d{1,2}[\. _xX-][eE](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00' \
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'.*(\D\d{1,2}[\. _xX-][eE][pP]\d{1,2}\D).*', name)) == 1 or len(re.findall(r'(^\d{1,2}[\. _xX-][eE][pP]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*(\d{1,2})[\. _xX-][eE][pP]\d{1,2}\D.*', name)
        episode = re.findall(r'.*\d{1,2}[\. _xX-][eE][pP](\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or season is None or len(season) != 1 or season[0] == '00'\
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'(^\d{1,2}[xX]\d{1,2}\D).*', name)) == 1 or len(re.findall(r'(\D\d{1,2}[xX]\d{1,2}\D).*', name)) == 1:
        season = re.findall(r'.*(\d{1,2})[xX]\d{1,2}\D.*', name)
        episode = re.findall(r'.*\d{1,2}[xX](\d{1,2})\D.*', name)
        if season is None or episode is None or len(season) != 1 or len(episode) != 1 or season[0] == '00'\
                or season[0] == '0' or episode[0] == '00' or episode[0] == '0':
            return None
        else:
            if len(season[0]) == 1:
                season[0] = '0' + season[0]
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'S' + season[0] + 'E' + episode[0]
    elif len(re.findall(r'(^\d{3}\D).*', name)) == 1 or len(re.findall(r'(\D\d{3}\D).*', name)) == 1:
        season_and_episode = re.findall(r'.*(\d{3})\D.*', name)
        if season_and_episode is None or len(season_and_episode) != 1 or season_and_episode[0][0] == '0'\
                or season_and_episode[0][1:] == '00':
            return None
        else:
            return 'S0' + season_and_episode[0][0] + 'E' + season_and_episode[0][1:]
    elif len(re.findall(r'(^\d{4}\D).*', name)) == 1 or len(re.findall(r'(\D\d{4}\D).*', name)) == 1:
        season_and_episode = re.findall(r'.*(\d{4})\D.*', name)
        if season_and_episode is None or len(season_and_episode) != 1 or season_and_episode[0][0:2] == '00'\
                or season_and_episode[0][2:] == '00' or season_and_episode[0][0:2] == '19'\
                or season_and_episode[0][0:2] == '20':
            return None
        else:
            return 'S' + season_and_episode[0][0:2] + 'E' + season_and_episode[0][2:]
    else:
        return None


def get_episode(name):    # 仅获取字幕文件名中的集的信息
    episode = None
    if len(re.findall('.*([eE]pisode\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*[eE]pisode(\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or episode[0] == '0' or episode[0] == '00':
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('.*([eE]\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*[eE](\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or episode[0] == '0' or episode[0] == '00':
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('.*([eE][pP]\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*[eE][pP](\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or episode[0] == '0' or episode[0] == '00':
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('.*(\D\d{1,2}\D).*', name)) == 1:
        episode = re.findall('.*\D(\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or episode[0] == '0' or episode[0] == '00':
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    elif len(re.findall('(^\d{1,2}\D).*', name)) == 1:
        episode = re.findall('^(\d{1,2})\D.*', name)
        if episode is None or len(episode) != 1 or episode[0] == '0' or episode[0] == '00':
            return None
        else:
            if len(episode[0]) == 1:
                episode[0] = '0' + episode[0]
            return 'E' + episode[0]
    else:
        return None
