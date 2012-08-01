# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: SelectReportPage.py 56 2008-09-18 02:03:25Z river $

import traceback
from templates.Error import Error
from templates.SelectReport import SelectReport
from QueryCache import QueryCache
import repdb

def response(context, req):
    """The user selected a wiki.  Display a list of reports that can be
       run on this wiki.
    """
    try:
        wiki = req.params['wiki']
        t = req.prepare_template(SelectReport)

        # The user can input either a domain or a dbname
        # in the wiki selection box; we accept either.
        try:
            t.wiki = repdb.find_wiki_domain(context, wiki)
        except ValueError:
            if wiki[-2:] != "_p":
                wiki += "_p"
            t.wiki = repdb.find_wiki(context, wiki)
            wiki = t.wiki['domain']

        cats = {}
        for k in context.reports.keys():
            r = context.reports[k]
            if not r.runs_on(t.wiki['domain']):
                continue
            catname = req.i18n.report_category(r)
            if not cats.has_key(catname):
                cats[catname] = []
            cats[catname].append(r)
        t.categories = cats
        cache = QueryCache(context)
        t.uncached = [r.key for r in cache.check_cache(t.wiki['dbname'], context.reports.values())]
        output = str(t)

        req.start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
        yield output
    except Exception, value:
        yield req.error(str(value))

    return

