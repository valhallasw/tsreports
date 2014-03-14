import os,glob
username = os.environ["USER"].replace('tools.', '')
venv = os.environ["VIRTUAL_ENV"]

fcgis = [os.path.split(f)[1] for f in glob.glob(os.path.expanduser("~/public_html/*.fcgi"))]

fcgi_server_template = """fastcgi.server += ( "/{username}/{fn}" =>
    ((
        "socket" => "/tmp/{username}-{fn}.sock",
        "bin-environment" => ("PATH" => "{venv}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"),
        "bin-path" => "/data/project/{username}/public_html/{fn}",
        "check-local" => "disable",
        "max-procs" => 1,
    ))
)

"""

for fcgi in fcgis:
	print fcgi_server_template.format(username=username, fn=fcgi, venv=venv)

print """
url.rewrite-once += ( "/{username}/?$" => "/{username}/index.fcgi",
                      "/{username}/\?" => "/{username}/index.fcgi")

debug.log-request-handling = "enable"
fastcgi.debug = 1 """.format(username=username)
