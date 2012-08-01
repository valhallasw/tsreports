# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: variables.py 9 2008-09-15 20:07:32Z river $

class Variable:
    """A variable is an input to a report.  It knows how to print itself
       in an HTML form.
    """
    def __init__(self, name, params):
        self.params = params
        self.name = name
        self.title=params[0]
    
    def format(self):
        return "Unknown field type"
    
class UsernameVariable(Variable):
    """A field representing a username."""
    def __init__(self, name, params):
        Variable.__init__(self, name, params)
    
    def format(self):
        # Turn this into a template
        return """%s: <input class="username" type="text" name="var_%s" />""" % (self.title, self.name)

class TextVariable(Variable):
    """A generic text field."""
    def __init__(self, name, params):
        Variable.__init__(self, name, params)
    
    def format(self):
        # Turn this into a template
        return """%s: <input type="text" name="var_%s" />""" % (self.title, self.name)
