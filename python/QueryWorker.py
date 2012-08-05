#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#

def update_report(wiki, report, parameters):
    import pwd, posix
    homedir = pwd.getpwuid(posix.getuid())[5]
    cfgfile = homedir + "/.reports.cfg"
    cfg = dict()
    execfile(cfgfile, cfg)
    cfg['homedir'] = homedir

    import sys
    sys.path.append(cfg['base'] + "/python")

    from Reports import ReportContext, Report
    from QueryCache import *

    context = ReportContext(cfg)
    cache = QueryCache(context)
    cache.update_report(wiki, report, parameters)
