# -*- coding: utf-8 -*-
import re

# -----------------------------------ass --->  srt------------------------------------
_REG_CMD = re.compile(r'{.*?}')


class SimpleTime(object):
    def __init__(self, string):
        """The string is like '19:89:06.04'."""
        h, m, s = string.split(':', 2)
        s, cs = s.split('.')
        self.hour = int(h)
        self.minute = int(m)
        self.second = int(s)
        # It's centisec in ASS
        self.microsecond = int(cs) * 10
        if self.microsecond < 0:
            self.microsecond = 0

    def sort_key(self):
        """Used by sort(key=...)."""
        return (self.hour, self.minute, self.second, self.microsecond)

    def __sub__(self, other):
        return (self.hour - other.hour) * 3600 + (self.minute - other.minute) * 60 + \
                (self.second - other.second) + (self.microsecond - other.microsecond) / 1000

    def __str__(self):  # SRT Format
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(self.hour, self.minute, self.second, self.microsecond)
    __unicode__ = __str__


class StrDialogue(object):
    def __init__(self, time_from, time_to, text=''):
        self.time_from = time_from
        self.time_to = time_to
        self.text = text

    def __unicode__(self):
        return '{} --> {}\r\n{}\r\n'.format(self.time_from, self.time_to, self.text)
    __str__ = __unicode__


class AssDialogueFormater(object):
    def __init__(self, format_line):
        colums = format_line[7:].split(',')
        self._columns_names = [c.strip().lower() for c in colums]

    def format(self, dialogue_line):
        columns = dialogue_line[9:].split(',', len(self._columns_names) - 1)
        formated = {name: columns[idx] for idx, name in enumerate(self._columns_names)}
        formated['start'] = SimpleTime(formated['start'])
        formated['end'] = SimpleTime(formated['end'])
        return formated


def _preprocess_line(line):
    """Remove line endings and comments."""
    line = line.strip()
    if line.startswith(';'):
        return ''
    else:
        return line


def convertASS(ass_data, no_effect=False, only_first_line=False):
    ass_str = ass_data.decode('utf-8')
    lines = ass_str.split('\n')
    if len(lines) == 0:
        return 'Ass data is null!'
    index = 0
    while index < len(lines):          # Locate the Events tag.
        line = _preprocess_line(lines[index])
        if not line.startswith('[Events]'):
            if index == len(lines) - 1:
                return 'Unable to find tag: [Events]'
            index += 1
        else:
            index += 1
            break
    formater = None
    while index < len(lines):
        line = _preprocess_line(lines[index])
        if line.startswith('Format:'):
            formater = AssDialogueFormater(line)
            index += 1
            if formater is None:
                return "Unable to find Events tag or format line in this file!"
            else:
                break
        else:
            if index == len(lines) - 1:
                return 'Unable to find format line!'
            index += 1
    # Iterate and convert all Dialogue lines:
    srt_dialogues = []
    while index < len(lines):
        line = _preprocess_line(lines[index])
        if line.startswith('['):
            break     # Events ended.
        elif not line.startswith('Dialogue:'):
            index += 1
            continue
        try:
            dialogue = formater.format(line)
        except:
            index += 1
            continue
        if dialogue['end'] - dialogue['start'] < 0.5 or dialogue['end'] - dialogue['start'] > 10.0:
            index += 1          # 跳过持续时间小于0.5s或大于10s的对白
            continue
        if no_effect:
            if dialogue.get('effect', ''):
                index += 1
                continue
        if dialogue['text'].endswith('{\p0}'):  # TODO: Exact match drawing commands.
            index += 1
            continue
        text = ''.join(_REG_CMD.split(dialogue['text']))      # Remove commands.
        text = text.replace(r'\N', '\r\n')
        re_del_list = re.findall(r'({.*?}|<front .*?>|</front>)', text)
        for each_del_str in re_del_list:
            text = text.replace(each_del_str, '')
        if only_first_line:
            text = text.split('\r\n', 1)[0]
        if '' != text.replace('\n', '').replace('\r', '').replace(' ', ''):
            srt_dialogues.append(StrDialogue(dialogue['start'], dialogue['end'], text))
        index += 1
    if len(srt_dialogues) < 10:
        return 'Unable to get dialogues!'
    srt_dialogues.sort(key=lambda dialogue: dialogue.time_from.sort_key())
    srt_string = ''
    srt_set = set()      # 去重集合
    i = 1
    for index in range(len(srt_dialogues)):
        if (i in range(1, 12) or index in range(len(srt_dialogues)-20, len(srt_dialogues))) and \
                ('.tv' in str(srt_dialogues[index]).lower() or '.com' in str(srt_dialogues[index]).lower() or
                 '.org' in str(srt_dialogues[index]).lower() or ' by ' in str(srt_dialogues[index]).lower() or
                 '©' in str(srt_dialogues[index]) or 'www' in str(srt_dialogues[index]).lower() or
                 'http' in str(srt_dialogues[index]).lower() or '@' in str(srt_dialogues[index]) or
                 'subtitle' in str(srt_dialogues[index]).lower() or 'translation' in str(srt_dialogues[index]).lower()):
            continue
        if str(srt_dialogues[index]) in srt_set:      # 遇到重复则跳过
            continue
        srt_string += '{}\r\n{}\r\n'.format(i, str(srt_dialogues[index]))
        srt_set.add(str(srt_dialogues[index]))
        i += 1
    return srt_string.encode('utf-8')


# -------------------------------smi ---> srt------------------------------------------
class smiItem(object):
    def __init__(self):
        self.start_ms = 0
        self.start_ts = '00:00:00,000'
        self.end_ms = 0
        self.end_ts = '00:00:00,000'
        self.contents = None
        self.linecount = 0

    @staticmethod
    def ms2ts(ms):
        hours = ms // 3600000
        ms = ms - hours * 3600000
        minutes = ms // 60000
        ms = ms - minutes * 60000
        seconds = ms // 1000
        ms = ms - seconds * 1000
        s = '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, ms)
        return s

    def convertSrt(self):
        if self.linecount == 4:
            i = 1
        # 1) convert timestamp
        self.start_ts = smiItem.ms2ts(self.start_ms)
        self.end_ts = smiItem.ms2ts(self.end_ms - 10)
        # 2) remove new-line
        self.contents = re.sub(r'\s+', ' ', self.contents)
        # 3) remove web string like "&nbsp";
        self.contents = re.sub(r'&[a-z]{2,5};', '', self.contents)
        # 4) replace "<br>" with '\r\n';
        self.contents = re.compile(r'(<br>)+', re.IGNORECASE).sub('\r\n', self.contents)
        # 5) find all tags
        fndx = self.contents.find('<')
        if fndx >= 0:
            contents = self.contents
            sb = self.contents[0:fndx]
            contents = contents[fndx:]
            while True:
                m = re.compile(r'</?([a-z]+)[^>]*>([^<>]*)', re.IGNORECASE).match(contents)
                if m is None:
                    break
                contents = contents[m.end(2):]
                if m.group(1).lower() in ['b', 'i', 'u']:
                    sb += m.string[0:m.start(2)]
                sb += m.group(2)
            self.contents = sb
        self.contents = self.contents.strip()
        self.contents = self.contents.strip('\r\n')

    def __repr__(self):
        s = '%d:%d:<%s>:%d' % (self.start_ms, self.end_ms, self.contents, self.linecount)
        return s


def convertSMI(smi_data):
    # smi_sgml is a string object
    smi_sgml = smi_data.decode('utf-8')
    try:
        fndx = smi_sgml.upper().find('<SYNC')
    except Exception as e:
        # print(e)
        return 'unable find <SYNC ' + str(e)
    if fndx < 0:
        return 'Unable to find <SYNC'
    smi_sgml = smi_sgml[fndx:]
    lines = smi_sgml.split('\n')

    srt_list = []
    incorrect_count = 0
    sync_cont = ''
    si = None
    last_si = None
    linecnt = 0
    for line in lines:
        linecnt += 1
        sndx = line.upper().find('<SYNC')
        if sndx >= 0:
            m = re.compile(r'<sync\s+start\s*=\s*(\d+)(\s+end\s*=\s*(\d+)|)\s*>(.*)$', re.IGNORECASE).search(line)
            if not m:
                m = re.compile(r'<sync\s+start\s*="(\d+)"(\s+end\s*=\s*(\d+)|)\s*>(.*)$', re.IGNORECASE).search(line)
                if not m:
                    incorrect_count += 1
                    continue
                    # return 'Invalid format tag of <Sync start=nnnn [end=nnnn]> with "%s"' % line
            sync_cont += line[0:sndx]
            last_si = si
            if last_si is not None:
                if last_si.end_ms == 0:
                    last_si.end_ms = int(m.group(1))  # fill end_ms with the current sync start time if no end tag was found in the last_si.
                last_si.contents = sync_cont
                srt_list.append(last_si)
                last_si.linecount = linecnt
            sync_cont = m.group(4)
            si = smiItem()
            si.start_ms = int(m.group(1))
            if m.group(3) is not None:
                si.end_ms = int(m.group(3))  # end tag has been found in the current_si
        else:
            sync_cont += line
    if len(srt_list) == 0:
        return "unable find formats string: <SYNC Start=nnnn [end=nnnn]>"
    elif incorrect_count > len(srt_list) * 0.5:
        return "too many incorrect formats string in the file!!!"
    result = []
    ndx = 1
    for index in range(len(srt_list)):
        srt_list[index].convertSrt()
        if srt_list[index].contents is None or '' == srt_list[index].contents.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace(' ', ''):
            continue
        if ndx in range(1, 12) or index in range(len(srt_list) - 15, len(srt_list)):
            if '.com' in srt_list[index].contents.lower() or '.org' in srt_list[index].contents.lower() or \
                    '.tv' in srt_list[index].contents.lower() or ' by ' in srt_list[index].contents.lower() or \
                    '©' in srt_list[index].contents or 'www' in srt_list[index].contents.lower() or \
                    'http' in srt_list[index].contents.lower() or '@' in srt_list[index].contents or \
                    'subtitle' in srt_list[index].contents.lower() or 'translation' in srt_list[index].contents.lower():
                continue
        if srt_list[index].end_ms - srt_list[index].start_ms < 500 or srt_list[index].end_ms - srt_list[index].start_ms > 10000:  # 跳过持续时间小于0.5s或大于10s的对白
            continue
        sistr = '%d\r\n%s --> %s\r\n%s\r\n\r\n' % (ndx, srt_list[index].start_ts, srt_list[index].end_ts, srt_list[index].contents)
        result.append(sistr)
        ndx += 1
    return ''.join(result).encode('utf-8')


# ----------------------------------sub ---> srt----------------------------------------------
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
def convertSUB(sub_data, span=0):
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
        if ('24' in str_tmp and 'fps' in str_tmp.lower()) or '24' == str_tmp:
            frame_rate = 24.0
            break
        if ('25' in str_tmp and 'fps' in str_tmp.lower()) or '25' == str_tmp:
            frame_rate = 25.0
            break
        index += 1
    if frame_rate == 0.0:                   # 若sub文件中没有指定帧速率，则返回23.976、24和25三种帧速率的srt二进制文件
        for i in range(len(lines)):
            if (line_count in range(1, 12) or i in range(len(lines) - 20, len(lines))) and \
                    ('.com' in lines[i].lower() or '.org' in lines[i].lower() or '.tv' in lines[i].lower() or
                     ' by ' in lines[i].lower() or '©' in lines[i] or 'www' in lines[i].lower() or
                     'http' in lines[i].lower() or '@' in lines[i] or 'subtitle' in lines[i].lower() or
                     'translation' in lines[i].lower()):
                # line_count = max(0, line_count - 1)
                continue
            # line_count += 1
            try:
                start_frame, end_frame, text = re.findall("\{.*?(\d+).*?\}\{.*?(\d+).*?\}(.*)$", lines[i])[0]
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
                srt_string_23 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_23, end_time_23, text.strip().replace("|", "\r\n"))
                srt_string_24 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_24, end_time_24, text.strip().replace("|", "\r\n"))
                srt_string_25 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_25, end_time_25, text.strip().replace("|", "\r\n"))
                line_count += 1
        return [srt_string_23.encode('utf-8'), srt_string_24.encode('utf-8'), srt_string_25.encode('utf-8')]
    else:                                                   # 若sub文件中指定帧速率，返回指定帧速率的srt二进制文件
        # print(index)
        for i in range(index + 1, len(lines)):
            if (line_count in range(1, 12) or i in range(len(lines) - 20, len(lines))) and \
                    ('.com' in lines[i].lower() or '.org' in lines[i].lower() or '.tv' in lines[i].lower() or
                     ' by ' in lines[i].lower() or '©' in lines[i] or 'www' in lines[i].lower() or
                     'http' in lines[i].lower() or '@' in lines[i] or 'subtitle' in lines[i].lower() or
                     'translation' in lines[i].lower()):
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
                srt_string += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time, end_time, text.strip().replace("|", "\r\n"))
                line_count += 1
        return srt_string.encode('utf-8')


def convertSRT(srt_data):    # 标准化srt文件格式
    lines = srt_data.decode('utf-8').split('\n')
    time_start_list = []
    content_dict = dict()
    dialogues = ''
    is_success = False    # 是否成功获取对白显示时间
    start_time = 0.0
    time_start_end = ''
    for line in lines:
        if len(re.findall('^(\d+ {0,1}\r)$', line)) == 1:  # 跳过索引
            continue
        if len(re.findall('^(\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d {0,2}\-{1,3}> {0,2}\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d).*?\r$', line)) == 1:
            if is_success:
                is_success = False
                if not dialogues.endswith('\r\n'):
                    dialogues += '\r\n'
                content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', ''))})
                dialogues = ''
            time_start = re.findall('^(\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d).*?\r$', line)
            time_end = re.findall('.*\-{1,3}> {0,2}(\d\d[\:\.] {0,1}\d\d[\:\.] {0,1}\d\d[\,\.\،] {0,1}\d\d\d).*?\r$', line)
            if len(time_start) == 1 or len(time_end) == 1:
                time_start = time_start[0].replace(' ', '').replace(':', '$').replace('.', '$').replace(',', '$').replace('،', '$')
                time_end = time_end[0].replace(' ', '').replace(':', '$').replace('.', '$').replace(',', '$').replace('،', '$')
                hms_s = time_start.split('$')
                if len(hms_s[3]) > 3:
                    hms_s[3] = hms_s[3][:3]
                else:
                    hms_s[3] = hms_s[3] + '0' * (3 - len(hms_s[3]))
                hms_e = time_end.split('$')
                if len(hms_e[3]) > 3:
                    hms_e[3] = hms_e[3][:3]
                else:
                    hms_e[3] = hms_e[3] + '0' * (3 - len(hms_e[3]))
                if len(hms_s) == 4 and len(hms_e) == 4:
                    start_time = float(hms_s[0])*3600 + float(hms_s[1])*60 + float(hms_s[2]) + float(hms_s[3])/1000  # 转换为秒数
                    end_time = float(hms_e[0])*3600 + float(hms_e[1])*60 + float(hms_e[2]) + float(hms_e[3])/1000
                    if end_time - start_time < 0.5 or end_time - start_time > 10.0:    # 跳过持续时间小于0.5s或大于10s的对白
                        continue
                    if start_time not in time_start_list:
                        time_start_list.append(start_time)
                    else:      # 起始时间重复则跳过
                        continue
                    time_start_end = hms_s[0]+':'+hms_s[1]+':'+hms_s[2]+','+hms_s[3]+' --> '+hms_e[0]+':'+hms_e[1]+':'+hms_e[2]+','+hms_e[3]+'\r\n'  # 时间转srt格式
                    is_success = True
                    continue
        if is_success:
            if line.endswith('\r\n'):
                pass
            elif line.endswith('\r'):
                dialogues += line+'\n'
            elif line.endswith('\n'):
                dialogues += line.replace('\n', '\r\n')
            else:
                dialogues += line+'\r\n'
    if is_success:
        if not dialogues.endswith('\r\n'):
            dialogues += '\r\n'
        content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', ''))})
    if len(time_start_list) < 35 or len(content_dict) < 35:  # 内容太少
        return 'too little srt file content!!!'
    time_start_list.sort()
    content_srt = ''
    index = 1
    m = min(len(time_start_list), len(content_dict))
    for i in range(m):
        content_tmp = content_dict[time_start_list[i]]
        if content_tmp is not None:
            if (index in range(1, 12) or i in range(m-20, m)) and \
                    ('.com' in content_tmp.lower() or '.org' in content_tmp.lower() or '.tv' in content_tmp.lower() or
                     ' by ' in content_tmp.lower() or '©' in content_tmp or 'www' in content_tmp.lower() or
                     'http' in content_tmp.lower() or '@' in content_tmp or 'subtitle' in content_tmp.lower() or
                     'translation' in content_tmp.lower()):
                continue
            content_srt += "%d\r\n%s" % (index, content_tmp)
            index += 1
    return content_srt.encode('utf-8')


def convertSUB1(data):
    lines = data.decode('utf-8').split('\n')
    time_start_list = []
    content_dict = dict()
    dialogues = ''
    is_success = False  # 是否成功获取对白显示时间
    start_time = 0.0
    time_start_end = ''
    i = 0
    while i < len(lines):
        if len(re.findall('(\d\d\:\d\d\:\d\d\.\d\d\,\d\d\:\d\d\:\d\d\.\d\d)', lines[i])) == 1:   # 定位到第一个时间
            break
        else:
            i += 1
    for j in range(i, len(lines)):
        if len(re.findall('(\d\d\:\d\d\:\d\d\.\d\d\,\d\d\:\d\d\:\d\d\.\d\d)', lines[j])) == 1:
            if is_success:
                is_success = False
                if not dialogues.endswith('\r\n'):
                    dialogues += '\r\n'
                content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', '').replace('[br]', '\r\n'))})
                dialogues = ''
            re_list = re.findall('(\d\d\:\d\d\:\d\d\.\d\d)', lines[j])
            if len(re_list) != 2:
                continue
            time_start = re_list[0]
            time_end = re_list[1]
            time_start = time_start.replace(' ', '').replace(':', '$').replace('.', '$')
            time_end = time_end.replace(' ', '').replace(':', '$').replace('.', '$')
            hms_s = time_start.split('$')
            if len(hms_s[3]) > 3:
                hms_s[3] = hms_s[3][:3]
            else:
                hms_s[3] = hms_s[3] + '0' * (3 - len(hms_s[3]))
            hms_e = time_end.split('$')
            if len(hms_e[3]) > 3:
                hms_e[3] = hms_e[3][:3]
            else:
                hms_e[3] = hms_e[3] + '0' * (3 - len(hms_e[3]))
            if len(hms_s) == 4 and len(hms_e) == 4:
                start_time = float(hms_s[0]) * 3600 + float(hms_s[1]) * 60 + float(hms_s[2]) + float(
                    hms_s[3]) / 1000  # 转换为秒数
                end_time = float(hms_e[0]) * 3600 + float(hms_e[1]) * 60 + float(hms_e[2]) + float(hms_e[3]) / 1000
                if end_time - start_time < 0.5 or end_time - start_time > 10.0:  # 跳过持续时间小于0.5s或大于10s的对白
                    continue
                if start_time not in time_start_list:
                    time_start_list.append(start_time)
                else:  # 起始时间重复则跳过
                    continue
                time_start_end = hms_s[0]+':'+hms_s[1]+':'+hms_s[2]+','+hms_s[3]+' --> '+hms_e[0]+':'+hms_e[1]+':'+hms_e[2]+','+hms_e[3]+'\r\n'    # 时间转srt格式
                is_success = True
                continue
        if is_success:
            if lines[j].endswith('\r\n'):
                pass
            elif lines[j].endswith('\r'):
                dialogues += lines[j]+'\n'
            elif lines[j].endswith('\n'):
                dialogues += lines[j].replace('\n', '\r\n')
            else:
                dialogues += lines[j]+'\r\n'
    if is_success:
        if not dialogues.endswith('\r\n'):
            dialogues += '\r\n'
        content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', '').replace('[br]', '\r\n').replace('\r\n\r\n', '\r\n'))})
    if len(time_start_list) < 35 or len(content_dict) < 35:  # 内容太少
        print(len(time_start_list), len(content_dict))
        return 'too little sub1 file content!!!'
    time_start_list.sort()
    content_srt = ''
    index = 1
    m = min(len(time_start_list), len(content_dict))
    for i in range(m):
        content_tmp = content_dict[time_start_list[i]]
        if content_tmp is not None:
            if (index in range(1, 12) or i in range(m - 20, m)) and \
                    ('.com' in content_tmp.lower() or '.org' in content_tmp.lower() or '.tv' in content_tmp.lower() or
                     ' by ' in content_tmp.lower() or '©' in content_tmp or 'www' in content_tmp.lower() or
                     'http' in content_tmp.lower() or '@' in content_tmp or 'subtitle' in content_tmp.lower() or
                     'translation' in content_tmp.lower()):
                continue
            content_srt += "%d\r\n%s" % (index, content_tmp)
            index += 1
    return content_srt.encode('utf-8')
