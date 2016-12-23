Changelog
=========

1.3.0 (2016-12-23)

* Added a normal function import for `imgix.get_imgix_url` that has the same signature as `get_imgix` template tag
* Added `IMGIX_SOURCES` setting to specify multiple sources
* Added optional `source` keyword argument to `get_imgix` template tag and `get_imgix_url` function.
* Keyword arguments passed in addition to an alias will override the alias values. Previously they were ignored in the presence of an alias.
* URLs are now correctly escaped in the template output
* Support and tests for Django 1.9 and 1.10

1.2.0 (2016-11-22)
------------------

* Added support for a Web Proxy Source
