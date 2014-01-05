tsreports
=========

The reports tool is a way to provide commonly used database queries in a regularly updated, easy-to-use form.

See also:
  * http://toolserver.org/~reports
  * https://jira.toolserver.org/browse/REPORTS


## Contents

  * 1 For users
  * 2 For developers
    * 2.1 Deploying a new version of the live tool
    * 2.2 Guidelines for committing
  * 3 Developers
  * 4 For translators

## For users

The [reports tool](http://toolserver.org/~reports) is a way to provide
commonly used database queries in a regularly updated, easy-to-use form. It is
a companion to the SQL [Query service](/view/Query_service). If you would like
a new query added, open a request [in
JIRA](https://jira.toolserver.org/browse/REPORTS) (in the 'Reports'
component), describing what you want the query to do. If you can provide the
SQL as well, that's helpful, but not a requirement.

## For developers

This section describes how to develop the reports tool.

Generally, you should use your own copy of the tool for development. Check out
the source:

    
    $ git clone https://github.com/valhallasw/tsreports

Copy reports.cfg.example to $HOME/.reports.cfg and edit it appropriately. Note
that 'base' is where the tool will be installed to, **not** the directory you
checked it out in. They must be different.

Run ./deploy from the reports directory.


    $ ./deploy
    
The deploy script will automatically kill any running FastCGI processes, so
your changes should be visible immediately (but only if you run it on
wolfsbane).

Log in to MySQL and source the reports.sql file.


    $ sql u__username_
    $ mysql> \. /home/_username_/reports/reports.sql
    

Now navigate to
[http://toolserver.org/~](http://toolserver.org/~)_username_/reports/ and it
should be working.

### Deploying a new version of the live tool

Once you've committed changes and you want to deploy them, become the
**reports** user. The source is in $HOME/reports/. Run 'svn up', then
./deploy. Make sure
[http://stable.toolserver.org/reports/](http://stable.toolserver.org/reports/)
works properly.

**NOTE**: Do not commit as the **reports** user, because svn will save your password in the shared home directory. 

### Guidelines for committing

  * All commits (except i18n changes) need an associated JIRA issue. If there isn't one, just create it, and resolve it after you commit. If an i18n commit already has a JIRA issue, e.g. it was provided by a non-committer, use that issue and follow the process described here. 
  * i18n commits must only touch i18n/*.msgs, and should have a commit message beginning 'i18n:' 
  * Make sure to assign the issue to yourself before you start working on it (or at the very least, before you commit) 
  * Format your commit message like this: 
    
    REPORTS-1 When the user clicks quux, their computer explodes
    REPORTS-37 Need more mice to power slow queries
    

i.e., "<issue key> <issue title>". Don't put any additional information in the
commit message; put it in a JIRA comment.

  * All commits must be **tested**, even minor ones, even if you think it's so simple it couldn't possibly be wrong. 
  * If you revert a commit, re-open the associated issue(s) and explain why. 
  * If you make a mistake during a commit and need to fix it, use the same issue key as the original commit, and append the fix in brackets: 
    
    REPORTS-37 Need more mice to power slow queries (fixed OutOfCheeseError caused by typo)
    
## For translators

Follow the instructions above to check out the svn repository. i18n files are
in i18n/*.msgs. Just copy en.msgs to <yourlang>.msgs, translate it, and send
the result in a bug report to [https://jira.toolserver.org/browse/REPORTS](htt
ps://jira.toolserver.org/browse/REPORTS).

Please convert all characters that are not
[ASCII](http://en.wikipedia.org/wiki/ASCII) with [Convert
Characters](http://toolserver.org/~w/conchar.php) to make sure everyone can
read them.

Note: as the tool is still very much in development, messages are likely to
change frequently. If you plan to translate the tool, you should probably
request commit access instead of opening a bug for each change.


<sub><sup>This text was partially copied from the corresponding [page](https://wiki.toolserver.org/view/Report_tool) on the Toolserver Wiki. It was edited by River, W, MZMcBride, Dispenser, TeleComNasSprVen, 125.209.70.3 and 82.42.89.123, and was available under CC-BY-SA.</sup></sub> 


