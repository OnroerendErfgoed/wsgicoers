Changes
=======

Version 0.11.0
--------------

- remove install_requires=["backports.functools_lru_cache >= 1.0"] (#3)

Version 0.10.0
--------------

- Set Vary: Accept header on all responses (#2)

Version 0.9.0
-------------

- Set Vary: Accept header on all responses (#1)

Version 0.8.0
-------------

- Add Access-Control-Allow-Origin header on non CORS GET's. (https://github.com/may-day/wsgicors/issues/17)

Version 0.7.0
-------------
- ``verbmulti`` matching strategy, that matches the first listed policy that also matches the requested METHOD
- relaxed dependency on lru_cache version
  
Version 0.6.0
-------------
- support for multiple policies
- caching of matching results

Version 0.5.1
-------------
- check for request being preflight
- reworked tests

Version 0.5.0
-------------

- support for Access-Control-Expose-Headers
- Header ``Vary`` is set to ``Origin`` if origin policy differs from ``*``

Version 0.4.1
-------------

-  py3 utf-8 related setup fixes

Version 0.4
-----------

-  python3 compatibility

Version 0.3
-----------

-  ``origin`` now takes space separated list of hostnames. They can be
   filename patterns like \*.domain.tld

Version 0.2
-----------

-  Access-Control-Allow-Credentials is now returned in the actual
   reponse if specified by policy

