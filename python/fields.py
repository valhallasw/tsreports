# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: fields.py 81 2010-02-06 21:11:57Z river $

import urllib, cgi, locale, datetime

class Field:
    """A field in a report result.  Knows how to format itself
       given the required keys.  A field is used like this:
       
       >>>  f = PageField(['page_title', 'page_namespace'])
       >>>  str = f.format({'page_title': 'Foo', 'page_namespace': 2})
    """
    def __init__(self, params):
        self.params = params
        self.title = params[0]
    
    def format(self, keys, lang):
        return "Unknown field type"
        
    def wikiformat(self, keys, lang):
        return "Unknown field type"
        
    def APIformat(self, key, lang):
        return {'error': 'unknown field type'}
    
class UserField(Field):
    """A field that returns a username.  Takes one param: the field
       name containing the username.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.userfield = params[1]
    
    def mktitle(self, keys, lang):
        ns = keys['__namespaces__'][2]
        user = keys[self.userfield]
        if ns in [6, 13]:
            user = ":" + user
        return "%s:%s" % (ns, user)

    def format(self, keys, lang):
        title = self.mktitle(keys, lang)
        domain = keys['__domain__']
        return """<a href="%s/wiki/%s">%s</a>""" % (domain, urllib.quote(title.encode('utf-8'), safe='/:'), cgi.escape(title))
        
    def wikiformat(self, keys, lang):
        title = self.mktitle(keys, lang)
        return """[[%s]]""" % (title,)
        
    def APIformat(self, keys, lang):
        title = self.mktitle(keys, lang)
        return {'namespace': 2,
                'title': keys[self.userfield],
                'fulltitle': self.mktitle(keys, lang),
                'url': "%s/wiki/%s" % (keys['__domain__'], urllib.quote(title.encode('utf-8'), safe='/:'))}

class PageField(Field):
    """A field that returns a formatted page name.  Takes two params:
       the namespace field name and the title field name.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.nsfield = params[1]
        self.titlefield = params[2]
    
    def mktitle(self, keys, lang):
        ns = keys[self.nsfield]

        title = ''
        if ns != 0:
            nslist = keys['__namespaces__']

            if nslist.has_key(ns):
                nsname = nslist[ns]
            else:
                nsname = str(ns)
            title = nsname + ":" + keys[self.titlefield]
        else:
            title = keys[self.titlefield]
            
        if ns in [6, 13]:
            title = ":" + title
        return title
        
    def format(self, keys, lang):
        title = self.mktitle(keys,lang)
        domain = keys['__domain__'].replace('http://', '//')
        return """<a href="%s/wiki/%s">%s</a>""" % (
            domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))
            
    def wikiformat(self, keys, lang):
        return "[[%s]]" % self.mktitle(keys,lang)
        
    def APIformat(self, keys, lang):
        title = self.mktitle(keys,lang)
        return {'namespace': keys[self.nsfield],
                'title': keys[self.titlefield],
                'fulltitle': title,
                'url': "%s/wiki/%s" % (keys['__domain__'], urllib.quote(title.encode('utf-8'), safe='/:'))}

class ImageField(Field):
    """Like PageField, except it links to an image page given just the img_name.
       Takes an optional extra parameter 
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.titlefield = params[1]
    
    def mktitle(self, keys, lang):
        nslist = keys['__namespaces__']
        nsname = nslist[6]
        return ":" + nsname + ":" + keys[self.titlefield]
        
    def format(self, keys, lang):
        title = self.mktitle(keys, lang)
        domain = keys['__domain__'].replace('http://', '//')
        return """<a href="%s/wiki/%s">%s</a>""" % (
            domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))
            
    def wikiformat(self, keys, lang):
        return "[%s]]" % self.mktitle(keys, lang)
        
    def APIformat(self, keys, lang):
        title = self.mktitle(keys,lang)
        return {'namespace': 2,
                'title': keys[self.titlefield],
                'fulltitle': title,
                'url': "%s/wiki/%s" % (keys['__domain__'], urllib.quote(title.encode('utf-8'), safe='/:'))}

class OtherImageField(Field):
    """An ImageField that links to an image on a different wiki"""
    def __init__(self, params):
        Field.__init__(self, params)
        self.titlefield = params[1]
        self.domain = params[2]
    
    def mktitle(self, keys, lang):
        return ":Image:" + keys[self.titlefield]
    
    def format(self, keys, lang):
        title = self.mktitle(keys, lang)
        return """<a href="//%s/wiki/%s">%s</a>""" % (
            self.domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))
    
    def APIformat(self, keys, lang):
        title = self.mktitle(keys,lang)
        return {'url': "%s/wiki/%s" % (self.domain, urllib.quote(title.encode('utf-8'), safe='/:'))}
            
class TextField(Field):
    """A field that just returns its value unchanged."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def format(self, keys, lang):
        return cgi.escape(keys[self.field], True)
        
    def wikiformat(self, keys, lang):
        return keys[self.field]
        
    def APIformat(self, keys, lang):
        return keys[self.field]

class TimestampField(Field):
    """Format an MW timestamp."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def getdatetime(self, keys, lang):
        x = keys[self.field]
        return datetime.datetime(int(x[0:4]), int(x[4:6]), int(x[6:8]), int(x[8:10]), int(x[10:12]), int(x[12:14]))
    
    def wikiformat(self, keys, lang):
        dt = self.getdatetime(keys, lang)
        return lang.format_datetime(dt)
        
    def format(self, keys, lang):
        return cgi.escape(self.wikiformat(keys, lang), True)
        
    def APIformat(self, keys, lang):
        return self.getdatetime(keys, lang)
        


class NumberField(Field):
    """A field that formats its value as a number."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def value(self, keys, lang):
        return int(keys[self.field])
    
    def wikiformat(self, keys, lang):
        return lang.format_number(self.value(keys, lang))

    def format(self, keys, lang):
        return cgi.escape(self.wikiformat(keys, lang), True)
        
    def APIformat(self, keys, lang):
        return self.value(keys, lang)

class WikiData_SearchField(Field):
    """A field that returns a search on WikiData for a formatted page name.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.nsfield = params[1]
        self.titlefield = params[2]
    
    def mkurl(self, keys, lang):
        ns = keys[self.nsfield]

        title = ''
        if ns != 0:
            nslist = keys['__namespaces__']

            if nslist.has_key(ns):
                nsname = nslist[ns]
            else:
                nsname = str(ns)
            title = nsname + ":" + keys[self.titlefield]
        else:
            title = keys[self.titlefield]

        return """//www.wikidata.org/w/index.php?search=%s""" % (
            urllib.quote(title.replace("_", " ").encode('utf-8'), safe='/:'),)
            
    def format(self, keys, lang):
        return """<a href="%s">(search)</a>""" % self.mkurl(keys, lang)
        
    def wikiformat(self, keys, lang):
        return """[%s (search)]""" % self.mkurl(keys, lang)
        
    def APIformat(self, keys, lang):
        return self.mkurl(keys, lang)

class WikiData_CreateField(Field):
    """A field that returns a formatted page name.  Takes two params:
       the namespace field name and the title field name.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.nsfield = params[1]
        self.titlefield = params[2]
    
    def mkurl(self, keys, lang):
        ns = keys[self.nsfield]

        title = ''
        if ns != 0:
            nslist = keys['__namespaces__']

            if nslist.has_key(ns):
                nsname = nslist[ns]
            else:
                nsname = str(ns)
            title = nsname + ":" + keys[self.titlefield]
        else:
            title = keys[self.titlefield]

        domain = keys['__domain__']
        return """//www.wikidata.org/w/index.php?title=Special:NewItem&site=%s&page=%s""" % (
            cgi.escape(keys["__dbname__"]),
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            )
            
    def format(self, keys, lang):
        return """<a href="%s">(create item)</a>""" % self.mkurl(keys, lang)
        
    def wikiformat(self, keys, lang):
        return """[%s (create item)]""" % self.mkurl(keys, lang)
        
    def APIformat(self, keys, lang):
        return self.mkurl(keys, lang)
