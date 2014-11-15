# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id$

import re, cgi, codecs
import requests

class LanguageFormatter(object):
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
        if length < 0:
            return "an unknown period of time"
        length = int(round(length))
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
            r += ", %d week" % weeks + ("s" if weeks != 1 else "")
        if days > 0:
            r += ", %d day" % days + ("s" if days != 1  else "")
        if hours > 0:
            r += ", %d hour" % hours + ("s" if hours != 1  else "")
        if minutes > 0:
            r += ", %d minute" % minutes + ("s" if minutes != 1  else "")
        r += ", %d second" % seconds + ("s" if seconds != 1 else "")

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
    
class I18nLoader(object):
    def __init__(self, context):
        self.session = requests.Session()
        self.context = context

    def get_language(self, lang):
        obj = LanguageFormatter()
        obj.msgs = self.load_messages(self.context, lang)
        obj.lang = lang
        return obj

    def load_messages(self, context, lang):
        domains = ['general', 'tsreports']
        translatedata = self.session.get(context.intuition, params={'domains': '|'.join(domains), 'lang': lang}).json()
        messages = {}

        for domain in domains:
            messages.update(translatedata['messages'][domain])
        return messages
