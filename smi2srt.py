# -*- coding: UTF-8 -*-
import re


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
		self.end_ts = smiItem.ms2ts(self.end_ms-10)
		# 2) remove new-line
		self.contents = re.sub(r'\s+', ' ', self.contents)
		# 3) remove web string like "&nbsp";
		self.contents = re.sub(r'&[a-z]{2,5};', '', self.contents)
		# 4) replace "<br>" with '\n';
		self.contents = re.compile(r'(<br>)+', re.IGNORECASE).sub('\n', self.contents)
		# 5) find all tags
		fndx = self.contents.find('<')
		if fndx >= 0:
			contents = self.contents
			sb = self.contents[0:fndx]
			contents = contents[fndx:]
			while True:
				m = re.compile(r'</?([a-z]+)[^>]*>([^<>]*)', re.IGNORECASE).match(contents)
				if m == None: break
				contents = contents[m.end(2):]
				if m.group(1).lower() in ['b', 'i', 'u']:
					sb += m.string[0:m.start(2)]
				sb += m.group(2)
			self.contents = sb
		self.contents = self.contents.strip()
		self.contents = self.contents.strip('\n')

	def __repr__(self):
		s = '%d:%d:<%s>:%d' % (self.start_ms, self.end_ms, self.contents, self.linecount)
		return s


def convertSMI(smi_data):
	# smi_sgml is a string object
	smi_sgml = smi_data.decode('utf-8')
	try:
		fndx = smi_sgml.upper().find('<SYNC')
	except Exception as e:
		#print(e)
		return str(e)
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
		if ndx in range(0, 12) or index in range(len(srt_list)-15, len(srt_list)):
			if '.com' in srt_list[index].contents.lower() or '.org' in srt_list[index].contents.lower() or\
					'.tv' in srt_list[index].contents.lower() or ' by ' in srt_list[index].contents.lower() or\
					'©' in srt_list[index].contents or 'www' in srt_list[index].contents.lower() or\
					'http' in srt_list[index].contents.lower() or '@' in srt_list[index].contents:
				continue
		if srt_list[index].end_ms - srt_list[index].start_ms < 500 or srt_list[index].end_ms - srt_list[index].start_ms > 10000:   # 跳过持续时间小于0.5s或大于10s的对白
			continue
		sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, srt_list[index].start_ts, srt_list[index].end_ts, srt_list[index].contents)
		result.append(sistr)
		ndx += 1
	return ''.join(result).encode('utf-8')
