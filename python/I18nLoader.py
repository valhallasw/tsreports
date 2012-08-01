# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id$

import re, cgi, codecs

class LanguageEnglish:
	"""English is the base class for all languages."""
	def __init__(self):
		pass

	def format_number(self, num):
		"""Format a number"""
		return re.sub(r"(.{3})(?=.)", r'\1,', str(num)[::-1])[::-1]

	def format_datetime(self, dt):
		"""Format a datetime"""
		return str(dt)

	def format_duration(self, length):
		"""Format a duration in seconds as a human-readable string."""
		weeks = length / (7 * 24 * 60 * 60)
		length %= (7 * 24 * 60 * 60)
		days = length / (24 * 60 * 60)
		length %= (24 * 60 * 60)
		hours = length / (60 * 60)
		length %= (60 * 60)
		minutes = length / 60
		length %= 60
		seconds = length

		r = ''
		if weeks > 0:
			r += ", %d week(s)" % weeks
		if days > 0:
			r += ", %d day(s)" % days
		if hours > 0:
			r += ", %d hour(s)" % hours
		if minutes > 0:
			r += ", %d minute(s)" % minutes 
		r += ", %d second(s)" % seconds

		return r[2:]

	def fmt(self, msg, args = {}):
		escaped = {}
		for arg, value in args.items():
			escaped[arg] = cgi.escape(str(value), True)
		try:
			return self.msgs[msg] % escaped
		except KeyError, err:
			return "&lt;%s&gt;" % msg

	def fmthtml(self, msg, args = {}):
		try:
			return self.msgs[msg] % args
		except KeyError, err:
			return "&lt;%s&gt;" % msg

	def report_name(self, report):
		if self.lang in report.name_i18n:
			return report.name_i18n[self.lang]
		return report.name

	def report_description(self, report):
		if self.lang in report.description_i18n:
			return report.description_i18n[self.lang]
		return report.description
	
	def report_category(self, report):
		key = "category_%s" % report.category
		if key in self.msgs:
			return self.msgs[key]
		return report.category
	
class LanguageGerman(LanguageEnglish):
	pass

class LanguageSpanish(LanguageEnglish):
	pass

class I18nLoader:
	languages = {
		'en': LanguageEnglish,
		'de': LanguageGerman,
		'es': LanguageSpanish
	};

	def __init__(self, context):
		self.classes = {}
		for lang in self.languages.keys():
			l = self.languages[lang]()
			l.msgs = self.load_messages(context, 'en')
			l.msgs.update(self.load_messages(context, lang))
			l.lang = lang
			self.classes[lang] = l

	def get_language(self, lang):
		if lang in self.classes:
			return self.classes[lang]
		return self.classes['en']

	def load_messages(self, context, lang):
		if re.compile("^[a-z_-]+$", re.IGNORECASE).match(lang) == None:
			return

		filename = "%s/i18n/%s.msgs" % (context.htmldir, lang)
		msgs = {}
		with codecs.open(filename, 'r', 'UTF-8') as handle:
			for line in handle:
				line = line.rstrip()
				if len(line) == 0 or line[0] == '#':
					continue
				bits = line.split(' ', 1)

				if len(bits) == 2:
					msgs[bits[0]] = bits[1]
				else:
					msgs[bits[0]] = ""
		return msgs

