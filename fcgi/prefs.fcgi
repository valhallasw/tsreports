#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: index.fcgi 9 2008-09-15 20:07:32Z river $

import pwd, posix
homedir = pwd.getpwuid(posix.getuid())[5]
cfgfile = homedir + "/.reports.cfg"
cfg = dict()
execfile(cfgfile, cfg)
cfg['homedir'] = homedir

import sys
sys.path.append(cfg['base'] + "/python")
sys.path.append('/opt/ts/lib/python2.4/site-packages')

import cgi
import requests
import json

from beaker.middleware import SessionMiddleware

from flup.server.fcgi import WSGIServer
from templates.PrefsForm import PrefsForm
from templates.PrefsSetDone import PrefsSetDone
from Reports import ReportContext
from RequestContext import RequestContext

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

# The main report application.  This is given the context at startup
# and holds it throughout the entire life of the application.
#
# WSGI invokes __call__() to handle a request.
class ReportApplication:
	context = None

	def __init__(self, context):
		self.context = context

	def __call__(self, environ, start_response):
		req = RequestContext(self.context, environ, start_response)

		method = "GET"
		method = environ['REQUEST_METHOD']

		if method == "GET":
			t = PrefsForm()
			t.context = context
                        t.langs = json.loads(requests.get('https://tools.wmflabs.org/intuition/wpAvailableLanguages.js.php').text.split("=")[1][:-1])
			t.i18n = req.i18n
                        t.lang = req.lang
			out = t.respond().encode('utf-8')
			start_response('200 OK', 
				[('Content-Type', 'text/html; charset=UTF-8')])
			yield out
		elif method == "POST":
			data = cgi.FieldStorage(fp=environ['wsgi.input'], environ = environ)
			if data.has_key('lang'):
				session = environ['beaker.session']
				session['lang'] = data['lang']
				session.save()

			t = PrefsSetDone()
			t.context = context
			t.i18n = req.i18n
			out = t.respond().encode('utf-8')
			start_response('200 OK', 
				[('Content-Type', 'text/html; charset=UTF-8')])
			yield out
		else:
			raise ValueError('unknown request method')

context = ReportContext(cfg)
app = ReportApplication(context)
app = RequestContext.wrap_wsgi(app, cfg)
wsgi = WSGIServer(app)
wsgi.run()
