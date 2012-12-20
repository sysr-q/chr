chr
===
__chr__ is a python based url shortening service which uses sqlite and Flask.

Dependencies
---
+ [Python 2.7](http://python.org)
+ [Flask](http://flask.pocoo.org/)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession)
+ sqlite3 (part of python)

Notes
---
+ It's __highly__ recommended by the developers that if you're putting this in a production environment (read: _any computer with a public IP_) that you look at the varying [Flask deployment](http://flask.pocoo.org/docs/deploying/) options, such as putting it behind nginx, lighttpd, or something.
+ This will take a while to get fully featured, but we have a lot planned.

Running
---
1. Clone the repo.
2. `python chrf.py` (for now)