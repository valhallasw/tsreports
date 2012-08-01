Basic types
===========

variables.py
------------
Defines variable types. `UsernameVariable` and `TextVariable` both extend `Variable`.

.. automodule:: variables
   :members:
   :undoc-members:

fields.py
---------
Defines output field types. All fields extend `Field`.

.. automodule:: fields
   :members:
   :undoc-members:

Reports.py
----------
Defines `Report` s, which are loaded from report files.

.. automodule:: Reports
   :members:
   :undoc-members:

It uses `queryreader` as data source.

.. automodule:: QueryReader
   :members:
   :undoc-members:

I18nLoader.py
-------------
Defines `LanguageEnglish`, which is the basic language type. `LanguageSpanish` and `LanguageGerman` extend from `LanguageEnglish`. All languages are loaded by `I18nLoader`.

.. automodule:: I18nLoader
   :members:
   :undoc-members:
