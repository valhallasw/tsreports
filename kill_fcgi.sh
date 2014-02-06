#!/usr/bin/env bash
PROJECTNAME=`echo $USER | sed -e 's/local-//'`
ps aux | grep $PROJECTNAME | grep python | grep fcgi | awk '{print $2}' | xargs kill 2>/dev/null
