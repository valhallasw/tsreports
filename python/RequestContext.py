# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id$

import traceback, urllib
from I18nLoader import I18nLoader
from templates.Error import Error
from beaker.middleware import SessionMiddleware

class RequestContext:
    @staticmethod
    def split_query_string(str):
        params = {}
        vals = str.split('&')
        if len(vals) > 0:
            for val in vals:
                if len(val) == 0:
                    continue
                (k, v) = val.split('=', 1)
                params[k] = urllib.unquote(v)
        return params

    @staticmethod
    def wrap_wsgi(app, cfg):
        return SessionMiddleware(app, 
            {
                'session.type': 'ext:database',
                'cookie_expires': False,
            },
            url = 'mysql://%(host)s/%(database)s' % {
                    'host': cfg['dbserver'],
                    'database': cfg['database']
                },
            data_dir = cfg['sessiondir'],
            sa_opts = {
                'sa.connect_args': { 'read_default_file': "%s/.my.cnf" % cfg['homedir'] },
            })


    def __init__(self, context, environ, start_response):
        self.context = context
        self.environ = environ
        self.start_response = start_response

        self.params = {}
        if environ.has_key("QUERY_STRING"):
            self.params = self.split_query_string(environ["QUERY_STRING"])

        self.lang = 'en'
        session = environ['beaker.session']
        if session.has_key('lang'):
            self.lang = session['lang'].value

        # uselang from URL overrides session language
        if self.params.has_key('uselang'):
            self.lang = self.params['uselang']

        self.i18n = self.context.i18nloader.get_language(self.lang)

    def prepare_template(self, template):
        t = template()
        t.i18n = self.i18n
        t.context = self.context
        t.trace = traceback.format_exc()
        return t

    def error(self, msg):
        t = self.prepare_template(Error)
        t.msg = msg
        t.trace = traceback.format_exc()
        output = str(t)
        self.start_response('500 Internal server error', [('Content-Type', 'text/html; charset=UTF-8')])
        return output

