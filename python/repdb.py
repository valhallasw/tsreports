# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: repdb.py 81 2010-02-06 21:11:57Z river $

import MySQLdb

def connect_toolserver(context):
    """Return a connection to the toolserver database."""
    db = MySQLdb.connect(db = 'toolserver', host = 'sql',
        read_default_file = context.mycnf)
    return db

def connect_wiki(context, wiki):
    """Return a connection to the given wiki database, e.g. enwiki_p"""
    host = "%s.db.toolserver.org" % wiki.replace('_p', '-p')
    db = MySQLdb.connect(db = wiki, host = host,
        read_default_file = context.mycnf)
    c = db.cursor()
    c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
    db.commit()
    return db

def wiki_list(context):
    """Return a list of wikis"""
    list = []
    db = connect_toolserver(context)
    try:
        c = db.cursor()
        c.execute("SELECT dbname, domain FROM wiki")
        for row in c.fetchall():
            list.append({'dbname': row[0], 'domain': row[1]})
    finally:
        db.close()
    return list

def find_wiki(context, wiki):
    """Return information on a single wiki, given its dbname"""
    db = connect_toolserver(context)
    c = db.cursor()
    c.execute("SELECT dbname, domain FROM wiki WHERE dbname=%s", wiki)
    r = c.fetchall()
    if len(r) == 0:
        raise ValueError('no such wiki')
    return { 'dbname': r[0][0], 'domain': r[0][1] }

def find_wiki_domain(context, wiki):
    """Return information on a single wiki, given its domain"""
    db = connect_toolserver(context)
    c = db.cursor()
    c.execute("SELECT dbname, domain FROM wiki WHERE domain=%s", wiki)
    r = c.fetchall()
    if len(r) == 0:
        raise ValueError('no such wiki')
    return { 'dbname': r[0][0], 'domain': r[0][1] }
    
def get_namespaces(context, wiki):
    """Return the namespace list for a wiki"""
    db = connect_toolserver(context)
    c = db.cursor()
    c.execute("SELECT ns_id, ns_name FROM namespace WHERE dbname=%s", wiki)
    ns = {}
    for f in c.fetchall():
        ns[f[0]] = unicode(f[1], 'utf-8')
    return ns

def connect_cache(context):
    db = MySQLdb.connect(db = context.database, host = context.dbserver, read_default_file = context.mycnf)
    return db
