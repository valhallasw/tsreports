#! /usr/bin/env python
# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#

def get_homedir():
    import pwd, posix
    homedir = pwd.getpwuid(posix.getuid())[5]
    return homedir    

def get_context():
    homedir = get_homedir()
    cfgfile = homedir + "/.reports.cfg"
    cfg = dict()
    execfile(cfgfile, cfg)
    cfg['homedir'] = homedir

    import sys
    sys.path.append(cfg['base'] + "/python")

    from Reports import ReportContext
    return ReportContext(cfg)
        

def update_report(wiki, report, parameters):
    from QueryCache import QueryCache
    context = get_context()

    cache = QueryCache(context)
    cache.update_report(wiki, report, parameters)

def logging_update_report(wiki, report, parameters):
    try:
        update_report(wiki, report, parameters)
    except Exception, e:
        import os, traceback, time
        f = open(os.path.join(get_homedir(), 'reports.err'), 'a')
        f.write('='*80 + '\n')
        f.write("At %s, \n" % time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
        f.write("While executing update_report(%r, %r, %r):\n\n" % (wiki, report, parameters))
        traceback.print_exc(file=f)
        f.close()
	raise

def main(argv):
    if len(argv) != 4:
	print "Usage: %s <wiki> <report name> <parameters in json format>" % argv[0]
	print "e.g. %s nlwiki newpagevswikidata []" % argv[0]
	raise SystemExit()

    import pwd, posix
    homedir = pwd.getpwuid(posix.getuid())[5]
    cfgfile = homedir + "/.reports.cfg"
    cfg = dict()
    execfile(cfgfile, cfg)
    cfg['homedir'] = homedir

    from Reports import ReportContext
    rc = ReportContext(cfg)
    report = rc.reports[argv[2]]

    import json
    logging_update_report(argv[1], report, json.loads(argv[3]))

if __name__ == "__main__":
    import sys
    main(sys.argv)
