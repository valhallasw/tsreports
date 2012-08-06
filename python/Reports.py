# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: Reports.py 81 2010-02-06 21:11:57Z river $

import glob, cgi, urllib, locale, re, codecs
import repdb
import QueryReader
#import fields, variables
from fields import *
from variables import *
from I18nLoader import *

class Report:
    """A single report.  Loads its description from the given file."""
    def __init__(self, key, file):
        self.when='immediately'
        self.name='No name'
        self.name_i18n = {}
        self.description='No description'
        self.description_i18n = {}
        self.cache=None
        self.query=None
        self.dynamiccache=False
        self.nightly = False
        self.category='Miscellaneous'
        self.wikis = None

        self.key = key
        self.file = file
        self.fields = []
        self.variables = []
        self.load()
   
    def __repr__(self):
        return 'Report(%r, %r)' % (self.key, self.file)

    def load(self):
        with codecs.open(self.file, 'r', 'UTF-8') as f:
            sections = QueryReader.read(f)

        # Some keywords, like %description and %category, support
        # a language parameter, e.g. %description:de
        for sec in sections:
            x = sec[0].split(':', 1)
            secname = x[0]
            seclang = None
            if len(x) == 2:
                seclang = x[1]

            if sec[0] == 'query':
                self.query = sec[1]

            elif sec[0] == 'when':
                self.when = sec[1]

            elif sec[0] == 'description':
                if seclang == None:
                    self.description = sec[1]
                else:
                    self.description_i18n[seclang] = sec[1]

            elif sec[0] == 'name':
                if seclang == None:
                    self.name = sec[1]
                else:
                    self.name_i18n[seclang] = sec[1]

            elif sec[0] == 'category':
                self.category = sec[1]

            elif sec[0] == 'cache':
                self.cache = int(sec[1])

            elif sec[0] == 'dynamiccache':
                self.dynamiccache = int(sec[1])
                if not self.cache:
                    self.cache = 3600*24*7 # one week

            elif sec[0] == 'nightly':
                self.nightly = True

            elif sec[0] == 'wikis':
                self.wikis = [x for x in re.compile(r'[ \t\n]+').split(sec[1]) if len(x) > 0]

            elif sec[0] == 'fields':
                for field in sec[1].split('\n'):
                    if len(field) == 0:
                        continue
                    fs = re.compile(r',[ \t]*').split(field)
                    cl = {  'user': UserField,
                        'timestamp': TimestampField,
                        'text': TextField,
                        'number': NumberField,
                        'page': PageField,
                        'image': ImageField,
                        'other_image': OtherImageField, } [fs[0]]
                    self.fields.append(cl(fs[1:]))

            elif sec[0] == "variable":
                fs = re.compile(r',[ \t]*').split(sec[1])
                varname = fs[0]
                cl = {  'username': UsernameVariable,
                    'text': TextVariable } [fs[1]]
                self.variables.append(cl(varname, fs[2:]))

    def cachable(self):
        if len(self.variables) > 0:
            return False
        if self.cache == None and not self.nightly:
            return False
        return True

    def runs_on(self, domain):
        if self.wikis == None:
            return True
        return domain in self.wikis

    def execute(self, context, dbname, variables):
        db = repdb.connect_wiki(context, dbname)
        c = db.cursor()
        import re
        esc_report_title = re.sub(r"[^A-Za-z0-9_@]", "_", "%s@%s" % (self.key, dbname))
        comment = "/* %s SLOW_OK LIMIT:86400 */" % esc_report_title
        c.execute(comment + self.query, variables)
        desc = c.description

        res = []
        for row in c.fetchall():
            i = 0
            d = {}
            for field in row:
                try:
                    d[desc[i][0]] = unicode(field, "utf-8")
                except TypeError:
                    d[desc[i][0]] = field
                i += 1
            res.append(d)
                
        return res

class ReportContext:
    """The context for the report system.  Mainly contains the list of reports."""
    reports = {}

    def __init__(self, cfg, lang = 'en'):
        self.docroot = cfg['docroot']
        self.homedir = cfg['homedir']
        self.database = cfg['database']
        self.htmldir = cfg['htmldir']
        self.mycnf = cfg['homedir'] + "/.my.cnf";
        self.dbserver = cfg['dbserver']
        if 'sitenotice' in cfg:
            self.sitenotice = cfg['sitenotice']
        else:
            self.sitenotice = None

        files = glob.glob("%s/reports/*.query" % cfg['base'])
        for f in files:
            tag=f[len(cfg['base']) + 9:len(f)-6]
            self.reports[tag] = Report(tag, f)
        self.i18nloader = I18nLoader(self)
