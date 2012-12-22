chr
===
__chr__ is a python based url shortening service which uses sqlite and Flask.  
We wanted to make a clean, simplistic url shortener, that wasn't written in a horrific language like PHP. What else but Python could come to mind?

Features
---
+ Can shorten several billion (yes!) unique urls to a less than 6 character slug.
+ Verifies the shrunk URLs are legitimate, to stop abuse.
+ Uses reCAPTCHA to stop spammers from using the service for evil, not good.
+ Slugs are the base62 representation of their ID, so they'll work in all browsers.

Dependencies
---
+ [Python 2.7](http://python.org)
+ [python-requests](http://docs.python-requests.org/en/latest/) (`pip install requests`)
+ [Flask](http://flask.pocoo.org/) (`pip install flask`)
+ [Flask-KVSession](https://github.com/mbr/flask-kvsession) (`pip install flask-kvsession`)
+ [recaptcha-client](http://pypi.python.org/pypi/recaptcha-client) (`pip install recaptcha-client`)
+ sqlite3 (part of a regular python install)

Notes
---
+ It's __highly__ recommended by the chr developers that if you're putting this in a production environment (read: _any computer with a public IP_) that you look at the various [Flask deployment](http://flask.pocoo.org/docs/deploying/) options, such as putting it behind nginx, lighttpd, or something.
+ This will take a while to get fully featured, but we have a lot planned.

Running
---
1. Clone the repo.
2. Edit the `settings.py` file, adding in required info etc.
3. `python chrm.py start`
`chrm.py` has other launch params, so just `python chrm.py --help` to check them out.

Author
---
+ [PigBacon](https://github.com/PigBacon)

Contributors
---
+ [hueypeard](https://github.com/hueypeard)