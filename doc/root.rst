Files in the root folder
========================

jsmin.{,c}
----------
See http://www.crockford.com/javascript/jsmin.html

clean
-----
Cleans up the python/templates/ folder. Removes all .py, .pyc and .bak files, except __init__.py.

deploy
------
Deploys all scripts to the correct folders. This should be run on all web servers, as it kills FCGI processes.
During testing, it's best to choose one server (for instance wolfsbane). Run the script on wolfsbane, then access the scripts via http://wolfsbane.toolserver.org.

* To $WWW (htmldir):
 * fcgi/*.fcgi
 * js/*. These are minified.
 * css/*
 * i18n/*
* To $INSTALLDIR (base)
 * python/*
 * reports/*. These are compiled with cheetah
 * nightly. This script is copied to $INSTALLDIR/bin

nightly
-------
This script can be called from a cron job (in its installed location, $INSTALLDIR/bin). It will execute all queries marked as 'nightly'.

purge
-----
::
  usage: ./purge key [domain]

Purges the cache of the report 'key' for one or all domains.

reports.cfg.example
-------------------
An example configuration file to use as ~/.reports.cfg
.. literalinclude:: ../reports.cfg.example

reports.sql
-----------
Creates the database table to store the query cache:
.. literalinclude:: ../reports.sql
