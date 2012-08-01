Report files
============
All reports are defined in //report files// in the reports/ directory. They consist of a description, input parameters, the query and the output format.

fields
------

%name
~~~~~
Defines the name of the query

%description
~~~~~~~~~~~~
Gives a description of the query

%category
~~~~~~~~~
Defines the category the query should be places in. Legal categories are defined in i18n/en.msgs:

.. literalinclude:: ../i18n/en.msgs
  :start-after: # using it.
  :end-before: # SelectWiki messages

%query
~~~~~~
Defines the query. Variables are added using the python string substitution syntax, for example::
  %(username)s

%variable
~~~~~~~~~
Defines an input variable. The parameters are variable name, field type and field parameters (as required by field type).

%fields
~~~~~~~
Defines an output field. The parameters are field type, display name and sql fields (as required by field type)

Example
-------
.. literalinclude:: ../reports/README
