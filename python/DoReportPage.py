# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: DoReportPage.py 81 2010-02-06 21:11:57Z river $

import cgi, pickle
import repdb
from QueryCache import *
from templates.QueryVariables import QueryVariables
from templates.Report import Report
from templates.WikitextReport import WikitextReport
from templates.CachedReportUnavailable import CachedReportUnavailable

import json
class JSONReport(object):
    def respond(self):
        return json.dumps( {'result': [ {f.formatter.title: f.APIformat() for f in row } for row in self.rows ] } )

class Field:
    def __init__(self, formatter, vars, lang):
        self.vars = vars
        self.formatter = formatter
        self.lang = lang

    def format(self):
        return self.formatter.format(self.vars, self.lang)
        
    def wikiformat(self):
        return self.formatter.wikiformat(self.vars, self.lang)
        
    def APIformat(self):
        return self.formatter.APIformat(self.vars, self.lang)

def response(context, req):
    try:
        key = req.params['report']
        report = context.reports[key]
    except ValueError:
        raise ValueError('no such report')
    
    dbname = req.params['wiki']
    try:
        format = req.params['format']
    except KeyError:
        format = 'html'
    
    Reporter = {'html': Report, 'wikitable': WikitextReport, 'wikilist': WikitextReport, 'json': JSONReport}[format]

    wiki = repdb.find_wiki(context, dbname)
    namespaces = repdb.get_namespaces(context, dbname)
    
    try:
        columns = [x.lower() for x in req.params['columns'].split("|")]
    except KeyError:
        columns = None

    # Extract all variables from the request.  Make sure all the
    # required variables were specified; if not, emit a form
    # where the user can specify them.
    variables = {}
    for k in req.params.keys():
        if k[0:4] != "var_":
            continue
        varname = k[4:]
        value = req.params[k]
        variables[varname] = value
    
    for v in report.variables:
        if not variables.has_key(v.name):
            # missing a variable
            t = req.prepare_template(QueryVariables)
            t.variables = report.variables
            t.wiki = wiki
            t.report = report

            output = str(t)
            req.start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
            yield output
            return

    cache = QueryCache(context)
    cache_result = cache.execute(report, dbname, variables)
    status = cache_result['status']
    if status == 'unavailable' or status == 'first':
        t = req.prepare_template(CachedReportUnavailable)
        t.status = status
        if status == 'first':
            t.query_runtime = cache_result['query runtime']

        t.report = report
        output = str(t)
        req.start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
        yield output
        return

    age = cache_result['age']
    result = cache_result['result']
    fields = report.fields

    t = req.prepare_template(Reporter)
    contenttype = {Report: 'text/html', WikitextReport: 'text/plain', JSONReport: 'application/json'}[Reporter] + '; charset=UTF-8'
    t.last_run_duration = cache_result.get('last_run_duration', None)
    t.age = age
    t.report = report
    t.wiki = wiki
    t.status = status
    t.format = format
    t.intro = "nointro" not in req.params

    if status == 'cold':
        t.query_runtime = cache_result['query runtime']

    # Generate a list of variables + values for the report page
    t.variables = {}
    for v in report.variables:
        t.variables[v.title] = variables[v.name]

    t.headers = []
    for f in fields:
        t.headers.append(f.title)
        
    t.rows = []
    for r in result:
        row = []
        for f in fields:
            if columns is None or f.title.lower() in columns:
                r['__namespaces__'] = namespaces
                r['__dbname__'] = dbname
                r['__domain__'] = wiki['domain']
                row.append(Field(f, r, req.i18n))
        t.rows.append(row)

    output = t.respond().encode('utf-8')
    req.start_response('200 OK', [('Content-Type', contenttype)])
    yield output
