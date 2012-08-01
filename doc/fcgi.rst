fcgi
====
The fcgi folder contains all fastcgi scripts. These are:

index.fcgi
----------
The dispatcher for the application. Dispatches requests to `SelectWikiPage`, `SelectReportPage`, or `DoReportPage`.

prefs.fcgi
----------
Allows users to set their language preference.

userlist.fcgi
-------------
AJAX helper script to show user name suggestions.

wikilist.fcgi
-------------
AJAX helper script to show wiki suggestions.