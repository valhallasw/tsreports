#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: index.fcgi 81 2010-02-06 21:11:57Z river $

import pwd, posix
homedir = pwd.getpwuid(posix.getuid())[5]
cfgfile = homedir + "/.reports.cfg"
cfg = dict()
execfile(cfgfile, cfg)
cfg['homedir'] = homedir

import sys
sys.path.append(cfg['base'] + "/python")

from beaker.middleware import SessionMiddleware

from flup.server.fcgi import WSGIServer
import SelectWikiPage, SelectReportPage, DoReportPage
from Reports import Report, ReportContext
import locale
from RequestContext import RequestContext

# Needs to be localised properly
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# The main report application.  This is given the context at startup
# and holds it throughout the entire life of the application.
#
# WSGI invokes __call__() to handle a request.
class ReportApplication:
	context = None

	def __init__(self, context):
		self.context = context

	def __call__(self, environ, start_response):
		params = dict()

		req = RequestContext(self.context, environ, start_response)
		params = req.params

		# There are three modes; the initial page, where the user has to select
		# a wiki; the report page, where the user has to select the report to run;
		# and the result page, where the result is displayed.  If neither 'wiki'
		# nor 'report' are set, we show the initial page.  If 'wiki' is set but
		# 'report' isn't, we show the report page.  If both are set, we run the
		# query and show the result page.
		wiki = None
		report = None
		try:
			if not params.has_key('wiki'):
				m = SelectWikiPage
			elif not params.has_key('report'):
				m = SelectReportPage
			else:
				m = DoReportPage

			return list(m.response(self.context, req))
		except Exception, value:
			return [req.error(str(value))]

context = ReportContext(cfg)
app = ReportApplication(context)
app = RequestContext.wrap_wsgi(app, cfg)
wsgi = WSGIServer(app)
wsgi.run()
