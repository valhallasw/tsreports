#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: userlist.fcgi 17 2008-09-16 15:56:26Z river $

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
import json

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

class UserLister:
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
		dbname = params['dbname'];

		db = repdb.connect_wiki(context, dbname)
		c = db.cursor()
		c.execute("SELECT user_name FROM user WHERE user_name LIKE %s ORDER BY user_name ASC LIMIT 20",
				prefix + '%')
		x = c.fetchall()

		start_response('200 OK', 
			[('Content-Type', 'text/plain; charset=UTF-8')])
		yield json.dumps([d[0] for d in x])

context = ReportContext(cfg)
app = UserLister(context)
wsgi = WSGIServer(app)
wsgi.run()
