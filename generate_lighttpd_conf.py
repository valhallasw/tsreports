import os,glob

fcgis = [os.path.split(f)[1] for f in glob.glob(os.path.expanduser("~/public_html/*.fcgi"))]

fcgi_server_template = """fastcgi.server += ( "/tsreports/%(fn)s" =>
    ((
        "socket" => "/tmp/tsreports-%(fn)s.sock",
        "bin-environment" => ("PATH" => "/data/project/tsreports/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"),
        "bin-path" => "/data/project/tsreports/public_html/%(fn)s",
        "check-local" => "disable",
        "max-procs" => 1,
    ))
)

"""

for fcgi in fcgis:
	print fcgi_server_template % {'fn': fcgi}

print """
url.rewrite-once += ( "/tsreports/?$" => "/tsreports/index.fcgi",
                      "/tsreports/\?" => "/tsreports/index.fcgi")

debug.log-request-handling = "enable"
fastcgi.debug = 1 """
