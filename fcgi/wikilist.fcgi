#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: wikilist.fcgi 42 2008-09-17 15:05:31Z river $

import pwd, posix
homedir = pwd.getpwuid(posix.getuid())[5]
cfgfile = homedir + "/.reports.cfg"
cfg = dict()
execfile(cfgfile, cfg)
cfg['homedir'] = homedir

import sys
sys.path.append(cfg['base'] + "/python")
sys.path.append('/opt/ts/lib/python2.4/site-packages')

import repdb
from flup.server.fcgi import WSGIServer
import SelectWikiPage, SelectReportPage, DoReportPage
from Reports import Report, ReportContext
import locale

def split_query_string(str):
	params = {}
	vals = str.split('&')
	if len(vals) > 0:
		for val in vals:
			if len(val) == 0:
				continue
			(k, v) = val.split('=', 1)
			params[k] = v
	return params

class WikiLister:
	context = None

	def __init__(self, context):
		self.context = context

	def __call__(self, environ, start_response):
		params = dict()
		if (environ.has_key("QUERY_STRING")):
			params = split_query_string(environ["QUERY_STRING"])

		prefix = ''
		if params.has_key('q'):
			prefix = params['q']

		db = repdb.connect_toolserver(self.context)
		c = db.cursor()

		# First try a match on domain.  If that doesn't work (no matches),
		# assume they typed a database name instead.
		c.execute("SELECT domain, dbname FROM wiki WHERE domain LIKE %s ORDER BY domain ASC LIMIT 20",
				prefix + '%')
		x = c.fetchall()

		if len(x) == 0:	# no matches
			c.execute("SELECT domain, dbname FROM wiki WHERE dbname LIKE %s ORDER BY domain ASC LIMIT 20",
					prefix + '%')
			x = c.fetchall()

		list = "\n".join(["%s|%s" % (d[0], d[1]) for d in x])

		start_response('200 OK', 
			[('Content-Type', 'text/plain; charset=UTF-8')])
		yield list

context = ReportContext(cfg)
app = WikiLister(context)
wsgi = WSGIServer(app)
wsgi.run()
