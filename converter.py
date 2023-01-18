# -*- coding: utf-8 -*-
import re
import copy

# -----------------------------------ass --->  srt------------------------------------
TEMPLATE = '%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\r\n'
TEMPLATE_WITH_INDEX = '%d\r\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\r\n'


def sec_to_time(sec):
    hours = sec // 3600
    minutes = (sec - hours * 3600) // 60
    seconds = int(sec - hours * 3600 - minutes * 60)
    milli = int((sec - int(sec)) * 1000)
    return hours, minutes, seconds, milli


def check_dialogue(dialogue_raw):
    dialogue = dialogue_raw.replace('\r', '').replace('\n', '')
    if ('.com' in dialogue or '.org' in dialogue or '.tv' in dialogue or '©' in dialogue or '.net' in dialogue or
            'www' in dialogue or 'http' in dialogue or '@' in dialogue or 'subtitle' in dialogue or
            len(re.findall('^by| by |translation|fackbook|NETFLIX|translate', dialogue, re.IGNORECASE)) > 0 or
            'oOo' in dialogue or ' BONUS ' in dialogue or '. N E T' in dialogue):
        return True
    else:
        return False


def delete_all_tags(raw_text):
    text = copy.deepcopy(raw_text)
    tags = re.findall('<.*?>', text.replace('<<<', '').replace('>>>', '').replace('<<', '').replace('>>', ''))        # 找出所有的标签并去除
    for tag in tags:
        text = text.replace(tag, '').strip()
    commands = re.findall('{.*?}', text)          # 找出所有的{}内的内容
    for command in commands:
        if len(re.findall(r'\\', command)) > 2:   # {}内是否是命令
            text = text.replace(command, '').strip()     # 去掉命令
    return text


class SimpleTime(object):
    def __init__(self, string):
        """The string is like 01:43:06.04"""
        h, m, s = string.replace(' ', '').split(':', 2)
        s, cs = s.split('.')
        self.hour = int(h)
        self.minute = int(m)
        self.second = int(s)
        # It's centisec in ASS
        self.microsecond = int(cs) * (10**(3-len(cs)))
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
    formater = AssDialogueFormater("Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\r")
    srt_dialogues = []
    time_list = []
    while index < len(lines):
        line = _preprocess_line(lines[index])
        if not line.startswith('Dialogue:'):
            index += 1
            continue
        try:
            dialogue = formater.format(line)
        except:
            index += 1
            continue
        if dialogue['end'] - dialogue['start'] < 0.015 or dialogue['end'] - dialogue['start'] > 60:
            index += 1          # 跳过持续时间小于0.015s或大于60s的对白
            continue
        if no_effect:
            if dialogue.get('effect', ''):
                index += 1
                continue
        if dialogue['text'].endswith('{\p0}'):  # TODO: Exact match drawing commands.
            index += 1
            continue
        text = dialogue['text']
        text = text.replace(r'\N', '\r\n').replace(r'\ N', '\r\n').replace('\\n', '\r\n').replace('&nbsp', ' ').replace('&nbsp;', ' ').replace('&lrm;', '').replace('&lrm', '')
        flag = False
        re_del_list = re.findall(r'({.*?}|<.*?>$|</.*?>)|(<.*?>)[^>]', text)
        for each_del_str in re_del_list:
            if each_del_str[0] != '':
                if len(re.findall(r'\\[a-z]', each_del_str[0])) > 4:
                    flag = True
                text = text.replace(each_del_str[0], '').strip()
            if each_del_str[1] != '':
                if len(re.findall(r'\\[a-z]', each_del_str[1])) > 4:
                    flag = True
                text = text.replace(each_del_str[1], '').strip()
        if flag is True:
            index += 1
            continue
        if only_first_line:
            text = text.split('\r\n', 1)[0]
        text_split = text.strip().strip('\r\n').strip('\r').strip('\n').split(' ')
        tmp = []
        for each in text_split:
            if each.isalpha() and len(each) == 1:
                tmp.append(each)
            elif each.replace('.', '').replace('-', '').isdigit():
                tmp.append(each)
        if len(tmp) > 0.7 * len(text_split):     # 该行含有m 0 6.2 -3 l 28.46 18.14 28.38 -8 11.86 0.11 0 0 6.2这种字符串则跳过
            index += 1
            continue
        if len(re.findall('\w+', text.replace('_', ''))) > 0:        # 如果text内容都是非数字字母文字则跳过
            # srt_dialogues.append(StrDialogue(dialogue['start'], dialogue['end'], text))
            time_tmp = f"{dialogue['start']}"
            if time_tmp in time_list:      # 对对白时间去重
                index += 1
                continue
            else:
                time_list.append(time_tmp)
            srt_dialogues.append(f"{time_tmp} --> {dialogue['end']}\r\n{text}\r\n")
        index += 1
    if len(srt_dialogues) < 35:
        return 'too little dialogue in this file!  ' + str(len(srt_dialogues))
    # srt_dialogues.sort(key=lambda dialogue: dialogue.time_from.sort_key())
    srt_dialogues.sort()     # 对白按时间升序排序
    srt_string = ''
    i = 1
    for index in range(len(srt_dialogues)):
        if (i in range(1, 12) or index in range(len(srt_dialogues)-20, len(srt_dialogues))) and \
                check_dialogue(str(srt_dialogues[index])):
            continue
        srt_string += '{}\r\n{}\r\n'.format(i, str(srt_dialogues[index]))
        i += 1
    if srt_string == '':
        return 'no dialogue content!!!'
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
        if self.end_ms - self.start_ms > 10000:    # 对白持续时间超过10s，仅显示10s
            self.end_ms = self.start_ms + 10000
        self.start_ts = smiItem.ms2ts(self.start_ms)
        self.end_ts = smiItem.ms2ts(self.end_ms - 10)
        # 2) remove new-line
        self.contents = re.sub(r'\s+', ' ', self.contents)
        # 3) remove web string like "&nbsp";
        self.contents = re.sub(r'&[a-z]{2,5};', '', self.contents)
        # 4) replace "<br>" with '\r\n';
        self.contents = re.compile(r'(<br>)+', re.IGNORECASE).sub('\r\n', self.contents)
        # 5) find all tags
        """
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
            self.contents = sb"""
        self.contents = self.contents.strip().strip('\r\n').replace('&nbsp', ' ')
        self.contents = delete_all_tags(self.contents)

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
    is_first = True
    first_start = 0
    linecnt = 0
    for line in lines:
        linecnt += 1
        sndx = line.upper().find('<SYNC')
        if sndx >= 0:
            m = re.compile(r'<sync {1,2}start {0,2}=[ "]{0,2}(-?\d+).*?(end {0,2}=[ "]{0,2}(-?\d+)).*?>(.*)$', re.IGNORECASE).search(line)     # r'<sync\s+start\s*=\s*(\d+)(\s+end\s*=\s*(\d+)|)\s*>(.*)$'
            if m is None:   # 没有带end，只有start
                m = re.compile(r'<sync {1,2}start {0,2}=[ "]{0,2}(-?\d+).*?(end {0,2}=[ "]{0,2}(-?\d+)|).*?>(.*)$', re.IGNORECASE).search(line)   # r'<sync\s+start\s*="(\d+)"(\s+end\s*=\s*(\d+)|)\s*>(.*)$'
                if m is None:   # 格式错误
                    incorrect_count += 1
                    continue
            sync_cont += line[0:sndx]
            last_si = si
            if last_si is not None:
                if last_si.end_ms == 0:
                    if first_start > 0:
                        last_si.end_ms = first_start + int(m.group(1))  # group下标从1开始
                    else:
                        last_si.end_ms = int(m.group(1))  # group下标从1开始
                last_si.contents = sync_cont
                srt_list.append(last_si)
                last_si.linecount = linecnt
            sync_cont = m.group(4)
            si = smiItem()
            if is_first and int(m.group(1)) < 0:
                is_first = False
                first_start = -int(m.group(1))
                si.start_ms = first_start + int(m.group(1))
            elif first_start > 0:
                si.start_ms = first_start + int(m.group(1))
            else:
                si.start_ms = int(m.group(1))
            if m.group(3) is not None:
                if first_start > 0:
                    si.end_ms = first_start + int(m.group(3))  # end tag has been found in the current_si
                else:
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
        content = srt_list[index].contents
        if content is None or len(re.findall('\w+', content.replace('_', ''))) == 0:    # '' == content.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace('-', '').replace('&nbsp', ' ').replace(';', ' ').strip()
            continue
        if (ndx in range(1, 12) or index in range(len(srt_list) - 15, len(srt_list))) and check_dialogue(content):
            continue
        if srt_list[index].end_ms - srt_list[index].start_ms < 15:  # 跳过持续时间小于0.015s的对白
            continue
        sistr = '%d\r\n%s --> %s\r\n%s\r\n\r\n' % (ndx, srt_list[index].start_ts, srt_list[index].end_ts, content)
        result.append(sistr)
        ndx += 1
    if len(result) == 0:
        return 'no dialogue content!!!'
    return ''.join(result).encode('utf-8')


# ----------------------------------sub ---> srt----------------------------------------------
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
    if frame_rate == 0.0:                   # 若sub文件中没有指定帧速率，则返回23.976、24和25三种帧速率的srt文件
        for i in range(len(lines)):         # 遍历每一行
            if (line_count in range(1, 12) or i in range(len(lines) - 20, len(lines))) and check_dialogue(lines[i]):
                # line_count = max(0, line_count - 1)
                continue
            result = re.findall("[\{\[].*?(\d+).*?[\}\]] {0,2}[\{\[].*?(\d+).*?[\}\]](.*)$", lines[i])
            if len(result) != 1:
                continue
            start_frame, end_frame, text = result[0]
            if (int(end_frame)-int(start_frame))/25.0 < 0.015:   # 跳过持续时间小于0.015s对白
                continue
            elif (int(end_frame)-int(start_frame))/25.0 > 10.0:  # 持续时间大于10s，仅显示10s
                end_frame = int(start_frame) + 10 * 25
            start_time_23 = frame_to_time(start_frame, 23.976, span)
            end_time_23 = frame_to_time(end_frame, 23.976, span)
            start_time_24 = frame_to_time(start_frame, 24.0, span)
            end_time_24 = frame_to_time(end_frame, 24.0, span)
            start_time_25 = frame_to_time(start_frame, 25.0, span)
            end_time_25 = frame_to_time(end_frame, 25.0, span)
            text = text.replace("|", "\r\n").replace('&nbsp', ' ').strip()
            text = delete_all_tags(text)
            if len(re.findall('\w+', text.replace('_', ''))) > 0:   # '' != text.replace('\n', '').replace('\r', '').replace('\t', '').replace('\xa0', '').replace('-', '').replace('&nbsp', ' ').replace(' ', '')
                srt_string_23 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_23, end_time_23, text)
                srt_string_24 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_24, end_time_24, text)
                srt_string_25 += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time_25, end_time_25, text)
                line_count += 1
        if srt_string_23 == '':
            return 'no dialogue content!!!'
        return [srt_string_23.encode('utf-8'), srt_string_24.encode('utf-8'), srt_string_25.encode('utf-8')]
    else:                                                   # 若sub文件中指定帧速率，返回指定帧速率的srt二进制文件
        # print(index)
        for i in range(index + 1, len(lines)):
            if (line_count in range(1, 12) or i in range(len(lines) - 20, len(lines))) and check_dialogue(lines[i]):
                # line_count = max(0, line_count - 1)
                continue
            result = re.findall("[\{\[].*?(\d+).*?[\}\]] {0,2}[\{\[].*?(\d+).*?[\}\]](.*)$", lines[i])
            if len(result) != 1:
                continue
            start_frame, end_frame, text = result[0]
            if (int(end_frame)-int(start_frame))/frame_rate < 0.015:   # 跳过持续时间小于0.015s的对白
                continue
            elif (int(end_frame)-int(start_frame))/frame_rate > 10.0:    # 持续时间大于10s，仅显示10s
                end_frame = int(int(start_frame) + 10 * frame_rate)
            start_time = frame_to_time(start_frame, frame_rate, span)
            end_time = frame_to_time(end_frame, frame_rate, span)
            text = text.replace("|", "\r\n").replace('&nbsp', ' ').strip()
            text = delete_all_tags(text)
            if len(re.findall('\w+', text.replace('_', ''))) > 0:
                srt_string += "%d\r\n%s --> %s\r\n%s\r\n\r\n" % (line_count, start_time, end_time, text)
                line_count += 1
        if srt_string == '':
            return 'no dialogue content!!!'
        return srt_string.encode('utf-8')


def convertSRT(srt_data):    # 标准化srt文件格式
    lines = srt_data.decode('utf-8').split('\n')
    time_start_list = []
    content_dict = {}
    dialogues = ''
    is_success = False    # 是否成功获取对白显示时间
    start_time = 0.0
    time_start_end = ''
    for line in lines:
        if len(re.findall('^( *?\d+ ?\r)$', line)) == 1:  # 跳过索引
            continue
        g = re.search('^ *?(\d{1,3})[\:\.] ?(\d\d)[\:\.] ?(\d\d)[\,\.\، ] ?(\d{1,3})[^\d\:\,\.\،]+(\d{1,3})[\:\.] ?(\d\d)[\:\.] ?(\d\d)[\,\.\، ] ?(\d{1,3}).*?\r$', line)  # 匹配00:00:00,225 --> 00:00:01,538
        if g is None:
            g = re.search('^ *?(\d{1,3})[\:\.] ?(\d\d)[\:\.] ?(\d\d)(\d{3})[^\d\:\,\.\،]+(\d{1,3})[\:\.] ?(\d\d)[\:\.] ?(\d\d)(\d{3}).*?\r$', line)    # 匹配00:00:00225 --> 00:00:01538
        if g is not None:
            if is_success:
                is_success = False
                if dialogues == '':
                    dialogues = '\r\n'
                elif not dialogues.endswith('\r\n'):
                    dialogues += '\r\n'
                dialogues = delete_all_tags(dialogues)
                if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:       # dialogues不能是非数字字母字符串
                    content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', '').strip()+'\r\n')})
                dialogues = ''
            if not g.group(4):    # 毫秒g.group(4)值为''或None
                start_time = int(g.group(1)[-2:]) * 3600 + int(g.group(2)) * 60 + int(g.group(3))
            else:
                start_time = int(g.group(1)[-2:]) * 3600 + int(g.group(2)) * 60 + int(g.group(3)) + int(g.group(4)) / 10**(len(g.group(4)))
            time_start_list.append(start_time)
            if not g.group(8):   # 毫秒g.group(8)值为''或None
                end_time = int(g.group(5)[-2:]) * 3600 + int(g.group(6)) * 60 + int(g.group(7))
            else:
                end_time = int(g.group(5)[-2:]) * 3600 + int(g.group(6)) * 60 + int(g.group(7)) + int(g.group(8)) / 10**(len(g.group(8)))
            if end_time - start_time < 0.015:
                continue
            elif end_time - start_time > 10:
                end_time = start_time + 10
            s_h, s_m, s_s, s_ms = sec_to_time(start_time)
            e_h, e_m, e_s, e_ms = sec_to_time(end_time)
            time_start_end = TEMPLATE % (s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms)
            is_success = True
            continue
        if is_success:
            if len(re.findall('\w+', line.replace('_', ''))) == 0:   # line.replace('\r', '').replace('\n', '').replace('\t', '').replace('-', '').replace(' ', '') == ''
                continue
            if line.endswith('\r\n'):
                pass
            elif line.endswith('\r'):
                dialogues += line+'\n'
            elif line.endswith('\n'):
                dialogues += line.replace('\n', '\r\n')
            else:
                dialogues += line+'\r\n'
    if is_success:
        if dialogues == '':
            dialogues = '\r\n'
        elif not dialogues.endswith('\r\n'):
            dialogues += '\r\n'
        dialogues = delete_all_tags(dialogues)
        if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:  # dialogues不能是非数字字母字符串
            content_dict.update({start_time: (time_start_end + dialogues.replace('\t', '').replace('    ', '').strip() + '\r\n')})
    if len(time_start_list) < 60 or len(content_dict) < 60:  # 内容太少
        print(len(time_start_list), len(content_dict))
        return 'too little srt file content!!!'
    time_start_list = list(set(time_start_list))
    time_start_list.sort()
    content_srt = ''
    index = 1
    m = len(time_start_list)
    for i in range(m):
        if time_start_list[i] not in content_dict:
            continue
        content_tmp = content_dict[time_start_list[i]]
        if content_tmp is not None:
            if (index in range(1, 12) or i in range(m-20, m)) and check_dialogue(content_tmp):
                continue
            content_srt += "%d\r\n%s\r\n" % (index, content_tmp)
            index += 1
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF4(data):                         # 转换00:00:16,.:44,00:00:18,.:72\r\n XXXXXX \r\n格式到srt
    lines = data.decode('utf-8').split('\n')
    time_start_list = []
    content_dict = {}
    dialogues = ''
    is_success = False  # 是否成功获取对白显示时间
    start_time = 0.0
    time_start_end = ''
    i = 0
    while i < len(lines):
        if len(re.findall('(\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3}\,\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3})', lines[i])) == 1:   # 定位到第一个时间
            break
        else:
            i += 1
    for j in range(i, len(lines)):
        g = re.search('(\d{1,2})\:(\d\d)\:(\d\d)[\.\:\,](\d{1,3})\,(\d{1,2})\:(\d\d)\:(\d\d)[\.\:\,](\d{1,3})', lines[j])
        if g is not None:
            if is_success:
                is_success = False
                if dialogues == '':
                    dialogues = '\r\n'
                elif not dialogues.endswith('\r\n'):
                    dialogues += '\r\n'
                dialogues = delete_all_tags(dialogues)
                if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:  # dialogues不能是非数字字母字符串
                    content_dict.update({start_time: (time_start_end+dialogues.replace('\t', '').replace('    ', '').replace('[br]', '\r\n')+'\r\n')})
                dialogues = ''
            if not g.group(4):    # 毫秒g.group(4)值为''或None
                start_time = int(g.group(1)) * 3600 + int(g.group(2)) * 60 + int(g.group(3))
            else:
                start_time = int(g.group(1)) * 3600 + int(g.group(2)) * 60 + int(g.group(3)) + int(g.group(4)) / 10**(len(g.group(4)))
            time_start_list.append(start_time)
            if not g.group(8):   # 毫秒g.group(8)值为''或None
                end_time = int(g.group(5)) * 3600 + int(g.group(6)) * 60 + int(g.group(7))
            else:
                end_time = int(g.group(5)) * 3600 + int(g.group(6)) * 60 + int(g.group(7)) + int(g.group(8)) / 10**(len(g.group(8)))
            if end_time - start_time < 0.015:
                continue
            elif end_time - start_time > 10:
                end_time = start_time + 10
            s_h, s_m, s_s, s_ms = sec_to_time(start_time)
            e_h, e_m, e_s, e_ms = sec_to_time(end_time)
            time_start_end = TEMPLATE % (s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms)
            is_success = True
            continue
        if is_success:
            if len(re.findall('\w+', lines[j].replace('_', ''))) == 0:   # lines[j].replace('\r', '').replace('\n', '').replace('\t', '').replace('-', '').replace(' ', '') == ''
                continue
            if lines[j].endswith('\r\n'):
                pass
            elif lines[j].endswith('\r'):
                dialogues += lines[j]+'\n'
            elif lines[j].endswith('\n'):
                dialogues += lines[j].replace('\n', '\r\n')
            else:
                dialogues += lines[j]+'\r\n'
    if is_success:
        if dialogues == '':
            dialogues = '\r\n'
        elif not dialogues.endswith('\r\n'):
            dialogues += '\r\n'
        dialogues = delete_all_tags(dialogues)
        if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:  # dialogues不能是非数字字母字符串
            content_dict.update({start_time: (time_start_end + dialogues.replace('\t', '').replace('    ', '').replace('[br]', '\r\n') + '\r\n')})
    if len(time_start_list) < 60 or len(content_dict) < 60:  # 内容太少
        print(len(time_start_list), len(content_dict))
        return 'too little content in F4!!!'
    time_start_list = list(set(time_start_list))
    time_start_list.sort()
    content_srt = ''
    index = 1
    m = len(time_start_list)
    for i in range(m):
        if time_start_list[i] not in content_dict:
            continue
        content_tmp = content_dict[time_start_list[i]]
        if content_tmp is not None:
            if (index in range(1, 12) or i in range(m - 20, m)) and check_dialogue(content_tmp):
                continue
            content_srt += "%d\r\n%s" % (index, content_tmp)
            index += 1
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF1(data):                               # 转换例如00:00:17:Vamos, espere um minuto.这种格式到srt
    lines = data.decode('utf-8').split('\n')
    last_start = -1.0
    last_content = None
    start_time_list = []
    content_dict = {}
    for line in lines:
        g = re.search('^(\d{1,2})\:(\d\d)\:(\d{1,2})[\:\.\,](\d{0,3})[\: ]?(.*?)$', line)
        if g is None:
            continue
        if not g.group(4):     # 毫秒g.group(4)值为''或None
            this_start = int(g.group(1))*3600 + int(g.group(2))*60 + int(g.group(3))
            start_time_list.append(this_start)
        else:
            this_start = int(g.group(1)) * 3600 + int(g.group(2)) * 60 + int(g.group(3)) + int(g.group(4)) / 10**len(g.group(4))
            start_time_list.append(this_start)
        this_start_copy = copy.deepcopy(this_start)
        if last_start != -1.0 and last_content is not None and this_start - last_start > 0.015:  # 仅保留持续时间大于0.015s的对白
            time_len = this_start - last_start
            if time_len > 10:
                this_start = last_start + 10          # 长度大于10s的对白仅显示10s
            else:
                this_start = this_start - time_len * 0.3                   # 结束点前移30%，避免卡点换字幕
            start_h, start_m, start_s, start_ms = sec_to_time(last_start)
            end_h, end_m, end_s, end_ms = sec_to_time(this_start)
            content_dict.update({last_start: TEMPLATE % (start_h, start_m, start_s, start_ms, end_h, end_m, end_s, end_ms) + last_content + '\r\n'})
        last_content = g.group(5).replace('\r', '').replace('\t', '').replace('|', '\r\n')
        last_content = delete_all_tags(last_content)
        if len(re.findall('\w+', last_content.replace('_', ''))) == 0:   # last_content.replace('-', '').strip() == '' or last_content == '\r\n' or last_content == '\r\n\r\n'
            last_content = None
        last_start = this_start_copy
    if last_content is not None:
        this_start = last_start + 3        # 最后一个对白默认为持续3s
        start_h, start_m, start_s, start_ms = sec_to_time(last_start)
        end_h, end_m, end_s, end_ms = sec_to_time(this_start)
        content_dict.update({last_start: TEMPLATE % (start_h, start_m, start_s, start_ms, end_h, end_m, end_s, end_ms) + last_content + '\r\n'})
    start_time_list = list(set(start_time_list))
    start_time_list.sort()
    index = 1
    content_srt = ''
    m = len(start_time_list)
    if m < 60:
        return 'too little dialogue content in F1!!!  ' + str(m)
    for i in range(m):
        if start_time_list[i] not in content_dict:
            continue
        content_tmp = content_dict[start_time_list[i]]
        if (index in range(1, 12) or i in range(m - 20, m)) and check_dialogue(content_tmp):
            continue
        content_srt += "%d\r\n%s\r\n" % (index, content_tmp)
        index += 1
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF2(data):                          # 转换[02:14:06]\r\n XXXXXX \r\n [02:15:06]格式到srt
    raw_str = data.decode('utf-8')
    content_srt = ''
    index = 1
    dialogue_list = re.findall('(\[\d{1,2}\:\d\d\:\d{1,2}\])\r\n.*?\r\n', raw_str)
    m = len(dialogue_list)
    if m < 60:
        return 'too little dialogue content in F2!!!   ' + str(len(dialogue_list))
    for i in range(m):
        tmp = dialogue_list[i].replace('[', '\[').replace(']', '\]').replace(':', '\:')
        g = re.search(tmp + '\r\n(.*?)\r\n\[(\d{1,2})\:(\d\d)\:(\d{1,2})\]', raw_str)
        if g is None and i != m-1:
            continue
        elif g is None and i == m-1:
            g = re.search(tmp + '\r\n(.*?)\r\n', raw_str)
        if g is None:
            continue
        content = g.group(1).replace('\r', '').replace('\n', '').replace('\t', '').replace('|', '\r\n')
        content = delete_all_tags(content)
        if len(re.findall('\w+', content.replace('_', ''))) == 0:   # content.replace('-', '').strip() == '' or content == '\r\n' or content == '\r\n\r\n'
            continue
        elif (index in range(1, 12) or i in range(m - 30, m)) and check_dialogue(content):
            continue
        gs = re.search('\[(\d{1,2})\:(\d\d)\:(\d{1,2})\]', dialogue_list[i])
        if gs is None:
            continue
        start_s = int(gs.group(1)) * 3600 + int(gs.group(2)) * 60 + int(gs.group(3))
        if len(g.groups()) == 4:
            end_s = int(g.group(2)) * 3600 + int(g.group(3)) * 60 + int(g.group(4))
        else:      # 最后一个对白无end time
            end_s = start_s + 2    # 默认最后一个对白持续2s
        if end_s - start_s < 0.015:
            continue
        elif end_s - start_s > 10:
            end_s = start_s + 10
        s_h, s_m, s_s, s_ms = sec_to_time(start_s)
        e_h, e_m, e_s, e_ms = sec_to_time(end_s)
        content_srt += TEMPLATE_WITH_INDEX % (index, s_h, s_m, s_s, 0, e_h, e_m, e_s, 0) + content + '\r\n\r\n'
        index += 1
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF3(data):                            # 转换{T 00:00:08:13\r\n XXXXXX \r\n}格式到srt
    raw_str = data.decode('utf-8')
    content_srt = ''
    last_time = -1.0
    last_dialogue = None
    index = 1
    dialogue_list = re.findall('(\{T {1,3}\d{1,2}\:\d\d\:\d{1,2}[\:\.\, ]?\d{0,3}(?:.|\n)*?\})', raw_str)
    m = len(dialogue_list)
    if m < 60:
        return 'too little dialogue content in F3!!!   ' + str(len(dialogue_list))
    for i in range(m):
        g = re.search('(T {1,3}(\d{1,2})\:(\d\d)\:(\d{1,2})[\:\.\, ]?(\d{0,3}).*?\r\n)', dialogue_list[i])
        if g is None:
            continue
        content = dialogue_list[i].replace(g.group(1), '').replace('\t', '').replace('{', '').replace('}', '')
        content = delete_all_tags(content)
        if len(re.findall('\w+', content.replace('_', ''))) == 0:   # content.replace('\r', '').replace('\n', '').replace('-', '').replace(' ', '') == ''
            continue
        elif (index in range(1, 12) or i in range(m - 30, m)) and check_dialogue(content):
            continue
        if not g.group(5):
            this_time = int(g.group(2)) * 3600 + int(g.group(3)) * 60 + int(g.group(4))
        else:
            this_time = int(g.group(2)) * 3600 + int(g.group(3)) * 60 + int(g.group(4)) + int(g.group(5)) / 10**(len(g.group(5)))
        this_time_copy = copy.deepcopy(this_time)
        if last_time != -1.0 and last_dialogue is not None:
            if this_time - last_time < 0.015:
                continue
            elif this_time - last_time > 10:        # 长度大于10s的对白仅显示10s
                this_time = last_time + 10
            else:
                this_time -= (this_time - last_time) * 0.3       # 结束点前移30%，避免卡点换字幕
            s_h, s_m, s_s, s_ms = sec_to_time(last_time)
            e_h, e_m, e_s, e_ms = sec_to_time(this_time)
            content_srt += TEMPLATE_WITH_INDEX % (index, s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms) + last_dialogue + '\r\n'
            index += 1
        last_time = this_time_copy
        last_dialogue = content
    this_time = last_time + 2
    s_h, s_m, s_s, s_ms = sec_to_time(last_time)
    e_h, e_m, e_s, e_ms = sec_to_time(this_time)
    content_srt += TEMPLATE_WITH_INDEX % (index, s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms) + last_dialogue + '\r\n'
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF5(data):                        # 将<p begin="00:00:54.221" end="00:00:55.973" XXX> XXXXXXX </p>格式转为srt
    lines = re.findall('\<p\r?\n? *?begin="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}"\r?\n? *?end="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}".*?\<\/p\>', data.decode('utf-8'), re.DOTALL)  # re.DOTALL表示使.也匹配换行符
    index = 1
    content_srt = ''
    m = len(lines)
    for i in range(m):
        g = re.search('\<p\r?\n? *?begin="(\d{1,2})\:(\d{2})\:(\d{2})[\.\:\,](\d{1,3})"\r?\n? *?end="(\d{1,2})\:(\d{2})\:(\d{2})[\.\:\,](\d{1,3})".*?\>\r?\n? *?(.*?)\r?\n? *?\<\/p\>', lines[i], re.DOTALL)  # re.DOTALL表示使.也匹配换行符
        if g is None:
            continue
        content = g.group(9)
        if content is None:
            continue
        content = content.replace('\r', '').replace('\n', '').replace('\t', '').replace('<br />', '\r\n').replace('<br/>', '\r\n').replace('<br>', '\r\n').replace('<br >', '\r\n').replace('&nbsp', ' ').strip()
        if len(re.findall('\w+', content.replace('_', ''))) == 0:   # content.replace('-', '').strip() == '' or content == '\r\n' or content == '\r\n\r\n'
            continue
        elif (index in range(1, 12) or i in range(m - 20, m)) and check_dialogue(content):
            continue
        tag_element = re.findall('<.*?>', content, re.DOTALL)
        for each_tag in tag_element:
            content = content.replace(each_tag, '')   # 去掉标签，例如<span>
        if not g.group(4):     # 毫秒g.group(4)值为''或None
            start_time = int(g.group(1)) * 3600 + int(g.group(2)) * 60 + int(g.group(3))
        else:
            start_time = int(g.group(1)) * 3600 + int(g.group(2)) * 60 + int(g.group(3)) + int(g.group(4)) / 10**(len(g.group(4)))
        if not g.group(8):     # 毫秒g.group(8)值为''或None
            end_time = int(g.group(5)) * 3600 + int(g.group(6)) * 60 + int(g.group(7))
        else:
            end_time = int(g.group(5)) * 3600 + int(g.group(6)) * 60 + int(g.group(7)) + int(g.group(8)) / 10**(len(g.group(8)))
        if end_time - start_time < 0.015:
            continue
        elif end_time - start_time > 10:
            end_time = start_time + 10
        s_h, s_m, s_s, s_ms = sec_to_time(start_time)
        e_h, e_m, e_s, e_ms = sec_to_time(end_time)
        content_srt += TEMPLATE_WITH_INDEX % (index, s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms) + content + '\r\n\r\n'
        index += 1
    if index < 60:
        return 'too little dialogue content in F5!!!   ' + str(index)
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def convertF6(srt_data):    # 转换00:14.800 --> 00:18.840\n XXXXXX 到srt
    lines = srt_data.decode('utf-8').split('\n')
    time_start_list = []
    content_dict = {}
    dialogues = ''
    is_success = False    # 是否成功获取对白显示时间
    start_time = 0.0
    time_start_end = ''
    for line in lines:
        if len(re.findall('^( {0,2}\d+ ?\r)$', line)) == 1:  # 跳过索引
            continue
        g = re.search('^ {0,2}(\d{1,2})[\:\.] ?(\d\d)[\,\.\،] ?(\d{1,3}) {0,2}[\-\*]{1,3} ?> {0,2}(\d{1,2})[\:\.] ?(\d\d)[\,\.\،] ?(\d{1,3}).*?\r$', line)
        if g is not None:
            if is_success:
                is_success = False
                if dialogues == '':
                    dialogues = '\r\n'
                elif not dialogues.endswith('\r\n'):
                    dialogues += '\r\n'
                dialogues = delete_all_tags(dialogues)
                if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:
                    content_dict.update({start_time: (time_start_end + dialogues.replace('\t', '').replace('    ', '')+'\r\n')})
                dialogues = ''
            if not g.group(3):    # 毫秒g.group(3)值为''或None
                start_time = int(g.group(1)) * 60 + int(g.group(2))
            else:
                start_time = int(g.group(1)) * 60 + int(g.group(2)) + int(g.group(3)) / 10**(len(g.group(3)))
            time_start_list.append(start_time)
            if not g.group(6):   # 毫秒g.group(6)值为''或None
                end_time = int(g.group(4)) * 60 + int(g.group(5))
            else:
                end_time = int(g.group(4)) * 60 + int(g.group(5)) + int(g.group(6)) / 10**(len(g.group(6)))
            if end_time - start_time < 0.015:
                continue
            elif end_time - start_time > 10:
                end_time = start_time + 10
            s_h, s_m, s_s, s_ms = sec_to_time(start_time)
            e_h, e_m, e_s, e_ms = sec_to_time(end_time)
            time_start_end = TEMPLATE % (s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms)
            is_success = True
            continue
        if is_success:
            if len(re.findall('\w+', line.replace('_', ''))) == 0:  # line.replace('\r', '').replace('\n', '').replace('\t', '').replace('-', '').replace(' ', '') == ''
                continue
            if line.endswith('\r\n'):
                pass
            elif line.endswith('\r'):
                dialogues += line+'\n'
            elif line.endswith('\n'):
                dialogues += line.replace('\n', '\r\n')
            else:
                dialogues += line+'\r\n'
    if is_success:
        if dialogues == '':
            dialogues = '\r\n'
        elif not dialogues.endswith('\r\n'):
            dialogues += '\r\n'
        dialogues = delete_all_tags(dialogues)
        if len(re.findall('\w+', dialogues.replace('_', ''))) > 0:
            content_dict.update({start_time: (time_start_end + dialogues.replace('\t', '').replace('    ', '')+'\r\n')})
    if len(time_start_list) < 60 or len(content_dict) < 60:  # 内容太少
        print(len(time_start_list), len(content_dict))
        return 'too little srt file content!!!'
    time_start_list = list(set(time_start_list))
    time_start_list.sort()
    content_srt = ''
    index = 1
    m = len(time_start_list)
    for i in range(m):
        if time_start_list[i] not in content_dict:
            continue
        content_tmp = content_dict[time_start_list[i]]
        if content_tmp is not None:
            if (index in range(1, 12) or i in range(m-20, m)) and check_dialogue(content_tmp):
                continue
            content_srt += "%d\r\n%s" % (index, content_tmp)
            index += 1
    if content_srt == '':
        return 'no dialogue content!!!'
    return content_srt.encode('utf-8')


def check(data):
    raw_str = data.decode('utf-8')
    if len(re.findall(r'(\d{1,2}\:\d\d\:\d{1,2}[\:\.\,]\d{0,3})\D', raw_str)) > len(raw_str.split('\n')) * 0.9:   # 转换00:00:17:Vamos, espere um minuto.格式到srt
        return convertF1(data)
    elif '[BEGIN]' in raw_str.upper() and 'START SCRIPT' in raw_str.upper() and '[END]' in raw_str.upper() and \
            'end script' in raw_str.lower():               # 转换[02:14:06]\r\n XXXXXX \r\n [02:15:06]格式到srt
        return convertF2(data)
    elif len(re.findall('(\{T(?:.|\n)*?\})', raw_str)) > 60:    # 转换{T 00:00:08:13\r\n XXXXXX \r\n}格式到srt
        return convertF3(data)
    elif ('[INFORMATION]' in raw_str and '[TITLE]' in raw_str and '[END INFORMATION]' in raw_str) or \
            (len(re.findall('(\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3}\,\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3})\r', raw_str)) > 60):   # 转换00:00:16,.:44,00:00:18,.:72\r\n XXXXXX \r\n格式到srt
        return convertF4(data)
    elif len(re.findall('\<p\r?\n? *?begin="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}"\r?\n? *?end="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}".*?\<\/p\>', raw_str, re.DOTALL)) > 60:  # 将<p begin="00:00:54.221" end="00:00:55.973" XXX> XXXXXXX </p>格式转为srt
        return convertF5(data)
    elif len(re.findall(r'(\n {0,2}\d{1,2}[\:\.] ?\d\d[\,\.\،] ?\d{1,3} {0,2}[\*\-]{1,3} ?> {0,2}\d{1,2}[\:\.] ?\d\d[\,\.\،] ?\d{1,3} ?.*?\r?\n.*?\r?\n)', raw_str)) > 60:
        return convertF6(data)
    else:
        return 'format unknown!!!'


def check_file_format(data):
    raw_str = data.decode('utf-8')
    if len(re.findall(r'(Dialogue\:.*?\, ?\d{1,2}\: ?\d{2}\: ?\d{2}\. ?\d{1,3}\, ?\d{1,2}\: ?\d{2}\: ?\d{2}\. ?\d{1,3}\,.*?\,.*?\,.*?\,.*?\,.*?\,.*?\,.*?)\r', raw_str)) > 60:
        return 'ass'
    elif len(re.findall('(\<[Ss][Yy][Nn][Cc].*?\>)', raw_str)) > 120:
        return 'smi'
    elif len(re.findall(r'([\{\[].*?\d+.*?[\}\]] {0,2}[\{\[].*?\d+.*?[\}\]])', raw_str)) > len(raw_str.split('\n')) * 0.9:
        return 'sub'
    re_list = re.findall(r'(\n *?\d{1,3}[\:\.] ?\d\d[\:\.] ?\d\d[\,\.\، ] ?\d{1,3}[^\d\:\,\.\،]+\d{1,3}[\:\.] ?\d\d[\:\.] ?\d\d[\,\.\، ] ?\d{1,3} ?.*?\r?\n.*?\r?\n)', raw_str)  # 匹配00:00:00,225 --> 00:00:01,538
    if len(re_list) > 60:
        return 'srt'
    elif len(re.findall(r'(\n *?\d{1,3}[\:\.] ?\d\d[\:\.] ?\d{5}[^\d\:\,\.\،]+\d{1,3}[\:\.] ?\d\d[\:\.] ?\d{5} ?.*?\r?\n.*?\r?\n)', raw_str)) > 60:   # 匹配00:00:00225 --> 00:00:01538
        return 'srt'
    elif len(re.findall(r'(\d{1,2}\:\d\d\:\d{1,2}[\:\.\,]\d{0,3})\D', raw_str)) > len(raw_str.split('\n')) * 0.9:
        return 'other'
    elif '[BEGIN]' in raw_str.upper() and 'START SCRIPT' in raw_str.upper() and '[END]' in raw_str.upper() and \
            'end script' in raw_str.lower():
        return 'other'
    elif len(re.findall('(\{T(?:.|\n)*?\})', raw_str)) > 60:
        return 'other'
    elif ('[INFORMATION]' in raw_str and '[TITLE]' in raw_str and '[END INFORMATION]' in raw_str) or \
            (len(re.findall('(\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3}\,\d{1,2}\:\d\d\:\d\d[\.\:\,]\d{1,3})\r', raw_str)) > 60):
        return 'other'
    elif len(re.findall('\<p\r?\n? *?begin="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}"\r?\n? *?end="\d{1,2}\:\d{2}\:\d{2}[\.\:\,]\d{1,3}".*?\<\/p\>', raw_str, re.DOTALL)) > 60:   # re.DOTALL表示使.也匹配换行符
        return 'other'
    elif len(re.findall(r'(\n {0,2}\d{1,2}[\:\.] ?\d\d[\,\.\،] ?\d{1,3} {0,2}[\*\-]{1,3} ?> {0,2}\d{1,2}[\:\.] ?\d\d[\,\.\،] ?\d{1,3} ?.*?\r?\n.*?\r?\n)', raw_str)) > 60:
        return 'other'
    else:
        return 'unknown'
