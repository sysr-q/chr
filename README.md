chr
===
__chr__ is a python based url shortening service which uses sqlite and Flask.  
We wanted to make a clean, simplistic url shortener, that wasn't written in a horrific language like PHP. What else but Python could come to mind?

Dependencies
---
+ [Python 2.7](http://python.org)
+ [Flask](http://flask.pocoo.org/) (`pip install flask`)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession) (`pip install flask-kvsession`)
+ [recaptcha-client](http://pypi.python.org/pypi/recaptcha-client) (`pip install recaptcha-client`)
+ sqlite3 (part of python)

Notes
---
+ It's __highly__ recommended by the chr developers that if you're putting this in a production environment (read: _any computer with a public IP_) that you look at the various [Flask deployment](http://flask.pocoo.org/docs/deploying/) options, such as putting it behind nginx, lighttpd, or something.
+ This will take a while to get fully featured, but we have a lot planned.

Running
---
1. Clone the repo.
2. `python chrf.py` (for now)