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
    
class UserField(Field):
    """A field that returns a username.  Takes one param: the field
       name containing the username.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.userfield = params[1]
    
    def format(self, keys, lang):
        ns = keys['__namespaces__'][2]
        user = keys[self.userfield]
        title = "%s:%s" % (ns, user)
        domain = keys['__domain__']
        return """<a href="http://%s/wiki/%s">%s</a>""" % (domain, urllib.quote(title.encode('utf-8'), safe='/:'), cgi.escape(user))

class PageField(Field):
    """A field that returns a formatted page name.  Takes two params:
       the namespace field name and the title field name.
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.nsfield = params[1]
        self.titlefield = params[2]
    
    def format(self, keys, lang):
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
        return """<a href="http://%s/wiki/%s">%s</a>""" % (
            domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))

class ImageField(Field):
    """Like PageField, except it links to an image page given just the img_name.
       Takes an optional extra parameter 
    """
    def __init__(self, params):
        Field.__init__(self, params)
        self.titlefield = params[1]
    
    def format(self, keys, lang):
        nslist = keys['__namespaces__']
        nsname = nslist[6]
        title = nsname + ":" + keys[self.titlefield]
        domain = keys['__domain__']
        return """<a href="http://%s/wiki/%s">%s</a>""" % (
            domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))

class OtherImageField(Field):
    """An ImageField that links to an image on a different wiki"""
    def __init__(self, params):
        Field.__init__(self, params)
        self.titlefield = params[1]
        self.domain = params[2]
    
    def format(self, keys, lang):
        title = "Image:" + keys[self.titlefield]
        return """<a href="http://%s/wiki/%s">%s</a>""" % (
            self.domain, 
            urllib.quote(title.encode('utf-8'), safe='/:'), 
            cgi.escape(title.replace('_', ' ')))

class TextField(Field):
    """A field that just returns its value unchanged."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def format(self, keys, lang):
        return cgi.escape(keys[self.field], True)

class TimestampField(Field):
    """Format an MW timestamp."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def format(self, keys, lang):
        x = keys[self.field]
        dt = datetime.datetime(int(x[0:4]), int(x[4:6]), int(x[6:8]), int(x[8:10]), int(x[10:12]), int(x[12:14]))
        return cgi.escape(lang.format_datetime(dt), True)


class NumberField(Field):
    """A field that formats its value as a number."""
    def __init__(self, params):
        Field.__init__(self, params)
        self.field = params[1]
    
    def format(self, keys, lang):
        return cgi.escape(lang.format_number(int(keys[self.field])), True)
