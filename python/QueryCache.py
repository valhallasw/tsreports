# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: QueryCache.py 58 2008-09-18 18:54:21Z river $

import pickle, MySQLdb
import repdb

class QueryCache:
	def __init__(self, context):
		self.context = context
	
	def load(self, dbname, report):
		"""Return a cached query result"""
		db = repdb.connect_cache(self.context)
		c = db.cursor()
	
		if report.nightly:
			c.execute("""SELECT (UNIX_TIMESTAMP() - last_run), result 
					FROM report_cache 
					WHERE report_key=%s AND dbname=%s""", (report.key, dbname))
		else:
			c.execute("""SELECT (UNIX_TIMESTAMP() - last_run), result 
					FROM report_cache 
					WHERE (UNIX_TIMESTAMP() - last_run) <= %s AND report_key=%s AND dbname=%s""",
					(report.cache, report.key, dbname))
		r = c.fetchone()
		if r == None:
			return None
		return (r[0], r[1])

	def save(self, dbname, report, data):
		"""Save the result of a query to the cache"""
		db = repdb.connect_cache(self.context)
		c = db.cursor()
		c.execute("""REPLACE INTO report_cache (dbname, report_key, last_run, result) 
				VALUES(%s, %s, UNIX_TIMESTAMP(), %s)""",
				(dbname, report.key, data))
		db.commit()
	
	def purge(self, dbname, report):
		"""Remove a query from the cache"""
		db = repdb.connect_cache(self.context)
		c = db.cursor()
		c.execute("DELETE FROM report_cache WHERE dbname = %s AND report_key = %s",
				(dbname, report.key));
		db.commit()
	
	def purge_all(self, report):
		"""Remove a query from the cache for all wikis"""
		db = repdb.connect_cache(self.context)
		c = db.cursor()
		c.execute("DELETE FROM report_cache WHERE report_key = %s", report.key)
		db.commit()

	def execute(self, report, dbname, variables, force = False):
		"""Like Report.execute(), except load/save from the cache as appropriate"""
		if not report.cachable():
			return (0, report.execute(self.context, dbname, variables))
			
		# Try cache load
		if not force:
			result = self.load(dbname, report)
			if result != None:
				data = pickle.loads(result[1])
				return (result[0], data)
		
			# Not cached; if it's a nightly query, return failure
			if report.nightly:
				return None

		result = report.execute(self.context, dbname, variables)
		self.save(dbname, report, pickle.dumps(result))
		return (0, result)
	
	def check_cache(self, dbname, reports):
		"""Given a list of reports, return a list of those which are uncached
		   %nightly queries."""
		db = repdb.connect_cache(self.context)
		c = db.cursor()
		ret = []
		for r in reports:
			if not r.nightly: continue
			c.execute("SELECT 1 FROM report_cache WHERE dbname=%s AND report_key=%s",
				(dbname, r.key))
			if len(c.fetchall()) == 0:
				ret.append(r)
		return ret