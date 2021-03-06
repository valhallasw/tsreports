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
from multiprocessing import Process

class QueryCache:
    def __init__(self, context):
        self.context = context
    
    def load(self, dbname, report):
        """Return a cached query result"""
        db = repdb.connect_cache(self.context)
        c = db.cursor()
    
        c.execute("""SELECT (UNIX_TIMESTAMP() - last_run), result, last_run_duration
                    FROM report_cache 
                    WHERE report_key=%s AND dbname=%s""", (report.key, dbname))
       
        r = c.fetchone()
        if r == None:
            return None, None, None

        try:
            data = pickle.loads(r[1])
        except Exception:
            return None, None, None

        return (r[0], data, r[2])

    def check_create_row(self, cursor, dbname, report_key):
         cursor.execute("""INSERT IGNORE INTO report_cache (dbname, report_key)
                     VALUES(%s, %s)""",
                  (dbname, report_key))
    
    def save(self, dbname, report, data):
        """Save the result of a query to the cache"""
        db = repdb.connect_cache(self.context)
        c = db.cursor()
        self.check_create_row(c, dbname, report.key)
    
        data = pickle.dumps(data)

        c.execute("""UPDATE report_cache
                     SET last_run=UNIX_TIMESTAMP()+1, last_run_duration=GREATEST(1,UNIX_TIMESTAMP()-last_start), result=%s
                     WHERE dbname=%s AND report_key=%s""",
                     (data, dbname, report.key)
                 )
       
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

    def expired(self, report, age, last_duration):
        if report.dynamiccache and last_duration:
            return (age > report.dynamiccache * last_duration)
        if report.cache:
            return (age > report.cache)
        return True

    def execute(self, report, dbname, variables, force = False):
        """Like Report.execute(), except load/save from the cache as appropriate"""
        if not report.cachable():
            return {'status': 'fresh',
                    'age': 0,
                    'result': report.execute(self.context, dbname, variables)}

        # Try cache load
        if not force:
            age, result, last_run_duration = self.load(dbname, report)
            if (result != None):
                if not self.expired(report, age, last_run_duration):
                    return {'status': 'hot', 'age': age, 'result': result, 'last_run_duration': last_run_duration}
                else:
                    query_runtime = self.run_background_update(dbname, report, variables)
                    return {'status': 'cold', 'query runtime': query_runtime, 
                            'age': age, 'result': result, 'last_run_duration': last_run_duration}

            # No cached value exists; if it's a nightly query, return failure
            if report.nightly:
                return {'status': 'unavailable'}
            else:
                query_runtime = self.run_background_update(dbname, report, variables)
                return {'status': 'first', 'query runtime': query_runtime, 
                        'age': age, 'result': result}



        result = self.update_report(dbname, report, variables)
        return {'status': 'fresh', 'age': 0, 'result': result}

    def get_report_state(self, report, now, last_run, last_start, last_run_duration):
        age = (now - last_run) if last_run is not None else None
        query_runtime = (now - last_start) if last_start is not None else None
        if not report.cachable():
            return {'status': 'not cached'}
        if last_start is None:
            # no cached report, and no report started
            if report.nightly:
                return {'status': 'unavailable'}
            return {'status': 'not cached'}

        if last_run is None: # initial run
            return {'status': 'first', 'running': True, 'query runtime': query_runtime}
        elif last_start > last_run: # could also be a manual run, after all.
            return {'status': 'cold', 'running': True, 'query runtime': query_runtime, 
                    'age': age, 'last_run_duration': last_run_duration}
        elif not self.expired(report, age, last_run_duration):
            return {'status': 'hot', 'age': age, 'last_run_duration': last_run_duration}
        else:
            return {'status': 'cold', 'running': False, 
                    'age': age, 'last_run_duration': last_run_duration}
        
    def check_cache(self, dbname, reports):
        """Given a database name and a list of Report objects, return a dict
           Report: {'status': '..', 'query runtime', etc}
        """
        db = repdb.connect_cache(self.context)
        c = db.cursor()
        c.execute("""SELECT report_key, UNIX_TIMESTAMP() as now, last_run, last_start, last_run_duration
                     FROM report_cache
                     WHERE dbname=%s""",
                  (dbname,))

        results = {report_key: (now, last_run, last_start, last_run_duration) for \
                   (report_key, now, last_run, last_start, last_run_duration) in c.fetchall()}
        
        return {report: self.get_report_state(report, *results.get(report.key, (None, None, None, None))) for report in reports}
        
    def run_background_update(self, dbname, report, variables):
        import QueryWorker

        db = repdb.connect_cache(self.context)
        c = db.cursor()
        self.check_create_row(c, dbname, report.key)
        c.execute("""SELECT UNIX_TIMESTAMP() - last_run, UNIX_TIMESTAMP() - last_start
                     FROM report_cache
                     WHERE dbname=%s AND report_key=%s""",
                     (dbname, report.key))
        time_since_last_finish, time_since_last_start = c.fetchone()
       
        # This function is called when the caller determined a query should be
        # running. To do this, we start a query worker if
        # a) the query has never been run, or
        # b) the query has started before, but probably never finished (determined by the cache time), or
        # c) the query has finished successfully

        if time_since_last_start is None or \
           time_since_last_start > report.cache or \
           (time_since_last_finish is not None and time_since_last_finish <= time_since_last_start):
            import subprocess, json, os
	    qwpy = os.path.join(os.path.split(__file__)[0], 'QueryWorker.py')

            db = repdb.connect_cache(self.context)
            c = db.cursor()
            self.check_create_row(c, dbname, report.key)
	    c.execute("""UPDATE report_cache
                         SET last_start=UNIX_TIMESTAMP()
                         WHERE dbname=%s AND report_key=%s""",
                         (dbname, report.key))
            db.commit()

	    subprocess.Popen(['jsub', '-N', '%s-%s' % (dbname, report.key), qwpy, dbname, report.key, json.dumps(variables)])
            return 0
        else:
            return time_since_last_start


    def update_report(self, dbname, report, variables):
        db = repdb.connect_cache(self.context)
        c = db.cursor()
        self.check_create_row(c, dbname, report.key)
        c.execute("""UPDATE report_cache
                     SET last_start=UNIX_TIMESTAMP()
                     WHERE dbname=%s AND report_key=%s""",
                     (dbname, report.key))
        db.commit()

        result = report.execute(self.context, dbname, variables)
        self.save(dbname, report, result)
        return result