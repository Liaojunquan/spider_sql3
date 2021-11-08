# -*- coding: utf-8 -*-
import re


# Convert total seconds into hours, min, sec and milli sec
def sec_to_time(sec):
    hours = int(sec / 3600)
    minutes = int((sec % 3600) / 60)
    seconds = int(sec % 3600 % 60)
    milli = int(1000*round(sec - int(sec), 3))
    return hours, minutes, seconds, milli


# Convert hours, min, sec and milli sec to total sec
def time_to_sec(h, m, s, ms):
    return float(h * 3600 + m * 60 + s + ms / 60.0)


# Function to convert frame number to corresponding minutes and seconds
def frame_to_time(frame, frame_rate, span=0):
    sec = int(frame) / float(frame_rate)
    hours, minutes, seconds, milli = sec_to_time(sec+span)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, milli)


# Function to convert sub format to srt
def sub_to_srt(sub_data, span=0):
    line_count = 1
    srt_string = ''
    srt_string_23 = ''
    srt_string_24 = ''
    srt_string_25 = ''
    frame_rate = 0.0
    lines = sub_data.decode('utf-8').split('\n')
    index = 0
    while index < 5:
        str_tmp = lines[index][lines[index].rfind('}')+1:].replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').strip()
        if len(re.findall('(\D2\d\.\d+|^2\d\.\d+).*', str_tmp)) == 1:
            frame_rate_re = re.findall('.*(2\d\.\d+).*', str_tmp)[0]
            try:
                frame_rate = float(frame_rate_re)
            except:
                pass
            else:
                break
        if len(re.findall('(\D2\d\D|^2\d\D).*', str_tmp)) == 1:
            frame_rate_re = re.findall('.*(2\d)\D.*', str_tmp)[0]
            try:
                frame_rate = float(frame_rate_re)
            except:
                pass
            else:
                break
        index += 1
    if frame_rate == 0.0:                   # 若sub文件中没有指定帧速率，则返回23.976、24和25三种帧速率的srt二进制文件
        for i in range(len(lines)):
            if (line_count in range(0, 12) or i in range(len(lines) - 20, len(lines))) and \
                    ('.com' in lines[i].lower() or '.org' in lines[i].lower() or '.tv' in lines[i].lower() or
                     ' by ' in lines[i].lower() or '©' in lines[i] or 'www' in lines[i].lower() or
                     'http' in lines[i].lower() or '@' in lines[i]):
                # line_count = max(0, line_count - 1)
                continue
            # line_count += 1
            try:
                start_frame, end_frame, text = re.findall("\{(\d+)\}\{(\d+)\}(.*)$", lines[i])[0]
            except:
                continue
            if (int(end_frame)-int(start_frame))/25.0 < 0.5 or (int(end_frame)-int(start_frame))/25.0 > 10.0:   # 跳过持续时间小于0.5s或大于10s的对白
                continue
            start_time_23 = frame_to_time(start_frame, 23.976, span)
            end_time_23 = frame_to_time(end_frame, 23.976, span)
            start_time_24 = frame_to_time(start_frame, 24.0, span)
            end_time_24 = frame_to_time(end_frame, 24.0, span)
            start_time_25 = frame_to_time(start_frame, 25.0, span)
            end_time_25 = frame_to_time(end_frame, 25.0, span)
            if '' != text.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', ''):
                srt_string_23 += "%d\n%s --> %s\n%s\n\n" % (line_count, start_time_23, end_time_23, text.strip().replace("|", "\n"))
                srt_string_24 += "%d\n%s --> %s\n%s\n\n" % (line_count, start_time_24, end_time_24, text.strip().replace("|", "\n"))
                srt_string_25 += "%d\n%s --> %s\n%s\n\n" % (line_count, start_time_25, end_time_25, text.strip().replace("|", "\n"))
                line_count += 1
        return [srt_string_23.encode('utf-8'), srt_string_24.encode('utf-8'), srt_string_25.encode('utf-8')]
    else:                                                   # 若sub文件中指定帧速率，返回指定帧速率的srt二进制文件
        for i in range(index + 1, len(lines)):
            if (line_count in range(0, 12) or i in range(len(lines) - 20, len(lines))) and \
                    ('.com' in lines[i].lower() or '.org' in lines[i].lower() or '.tv' in lines[i].lower() or
                     ' by ' in lines[i].lower() or '©' in lines[i] or 'www' in lines[i].lower() or
                     'http' in lines[i].lower() or '@' in lines[i]):
                # line_count = max(0, line_count - 1)
                continue
            # line_count += 1
            try:
                start_frame, end_frame, text = re.findall("\{(\d+)\}\{(\d+)\}(.*)$", lines[i])[0]
            except:
                continue
            if (int(end_frame)-int(start_frame))/frame_rate < 0.5 or (int(end_frame)-int(start_frame))/frame_rate > 10.0:   # 跳过持续时间小于0.5s或大于10s的对白
                continue
            start_time = frame_to_time(start_frame, frame_rate, span)
            end_time = frame_to_time(end_frame, frame_rate, span)
            if '' != text.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', ''):
                srt_string += "%d\n%s --> %s\n%s\n\n" % (line_count, start_time, end_time, text.strip().replace("|", "\n"))
                line_count += 1
        return srt_string.encode('utf-8')
