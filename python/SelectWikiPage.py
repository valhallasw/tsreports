# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: SelectWikiPage.py 14 2008-09-16 14:48:12Z river $

import traceback
from templates.Error import Error
from templates.SelectWiki import SelectWiki
import repdb

def response(context, req):
    """Display a list of wikis, and allow the user to select one."""
    try:
        wikis = repdb.wiki_list(context)

        t = req.prepare_template(SelectWiki)
        t.wikis = wikis

        output = str(t)
        req.start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8')])
        yield output

    except Exception, value:
        yield req.error(str(value))
    return

