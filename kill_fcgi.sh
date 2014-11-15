#!/usr/bin/env bash
PROJECTNAME=`echo $USER | sed -e 's/tools.//'`
ps aux | grep $PROJECTNAME | grep python | grep fcgi | awk '{print $2}' | xargs kill
