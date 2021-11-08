# -*- coding: utf-8 -*-
import re

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


def convert(ass_data, no_effect=True, only_first_line=False):
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
        text = text.replace(r'\N', '\r\n').replace(r'\n', '\r\n')
        re_del_list = re.findall(r'({.*?}|<front .*?>|</front>)', text)
        for each_del_str in re_del_list:
            text = text.replace(each_del_str, '')
        if only_first_line:
            text = text.split('\r\n', 1)[0]
        if '' != text.replace('\n', '').replace('\r', '').replace(' ', ''):
            srt_dialogues.append(StrDialogue(dialogue['start'], dialogue['end'], text))
        index += 1
    if len(srt_dialogues) < 10:
        return 'unable to get dialogues!'
    srt_dialogues.sort(key=lambda dialogue: dialogue.time_from.sort_key())
    srt_string = ''
    srt_set = set()      # 去重集合
    i = 1
    for index in range(len(srt_dialogues)):
        if (i in range(0, 12) or index in range(len(srt_dialogues)-20, len(srt_dialogues))) and \
                ('.tv' in str(srt_dialogues[index]).lower() or '.com' in str(srt_dialogues[index]).lower() or
                 '.org' in str(srt_dialogues[index]).lower() or ' by ' in str(srt_dialogues[index]).lower() or
                 '©' in str(srt_dialogues[index]) or 'www' in str(srt_dialogues[index]).lower() or
                 'http' in str(srt_dialogues[index]).lower() or '@' in str(srt_dialogues[index])):
            continue
        if str(srt_dialogues[index]) in srt_set:      # 遇到重复则跳过
            continue
        srt_string += '{}\r\n{}\r\n'.format(i, str(srt_dialogues[index]))
        srt_set.add(str(srt_dialogues[index]))
        i += 1
    return srt_string.encode('utf-8')


#if __name__ == '__main__':
#    srt = convert(open('C:/Users/Administrator/Downloads/[HorribleSubs] Mahou Shoujo Site - 02 [720p].ass',
#                       'r', encoding='utf-8'), None, True, False)
#    print(srt)
