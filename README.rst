===============
Website Monitor
===============


.. image:: https://img.shields.io/pypi/v/website_monitor.svg
        :target: https://pypi.python.org/pypi/website_monitor

.. image:: https://img.shields.io/travis/an0o0nym/website_monitor.svg
        :target: https://travis-ci.org/an0o0nym/website_monitor




Website Monitor is a program used for monitoring web sites and reporting their availability.

This tool is intended as a monitoring program for detecting problems on websites.
A perfect tool for web site administrators!


Usage
------

* Use :code:`website_monitor` to run the application
* Use (:code:`-i time_in_seconds` or :code:`--i=time_in_seconds`)
  flags to set custom interval time between website status checks.
* Use :code:`website_monitor_web_app` to run flask web server.
  Then you can simply view logs in your browser at :code:`localhost:5000`

License
-------

* Free software: MIT license


TODO
----

* Create a way to simply view logfile via CLI


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
