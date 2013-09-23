chr url shortener
=================

NB!
---
As of the v3 refactor how you interact with chr (as a sysadmin) has changed significantly. You still install it via PyPI (TODO, updated version not up yet), but you'll have to run it with something like gunicorn rather than via a command line script explicity for chr.  

For now:

- Clone the repo
- ``python setup.py install``
- Check ``example.py`` for more info on how to run it.
- Use a command like: ``gunicorn -b 127.0.0.1:5000 -p /tmp/chr.pid example:app``

JSON in v3 and beyond
---------------------
If you want to get the statistics of a given URL in JSON format, you can simply smack `.json` on the end of the stats url (``http://blah.tld/x/stats.json``) and get back some lovely JSON.

If the URL doesn't exist you'll get back something with ``error: true``, so just check the ``message`` field and you're good.

**TODO:** add an API endpoint to shorten/expand URLs.

****

.. _docs: http://chr.rtfd.org

**chr** (coded under the name ``chrso``) is a Python based URL shortening service which uses Flask as a front end, and redis as the backend.

It can shrink billions of unique URLs with less than 6 characters, run in the background with no human interaction, and it can fly like a bird -- or is that Super Man?

Features
--------

- Can shorten several billion (yes!) unique urls to a less than 6 character slug.
- Can use reCAPTCHA to stop spammers from using the service for evil. (but it's optional!)
- A live chr instance is located at `chr.so <http://chr.so>`_. (NB: this isn't the latest version)

Dependencies
------------
These are varying at the moment! Check ``requirements.txt`` to see a list.

To install all of these: ``pip -r requirements.txt install``

Notes
-----

- It's **highly** recommended by the chr developers that if you're putting this in a production environment (read: *any computer with a public IP*) that you look at the various `Flask deployment <http://flask.pocoo.org/docs/deploying>`_ options, such as putting it behind nginx, lighttpd, or something.
- It's also recommended that you get your server (nginx, lighttpd, or hell, even Apache) serve out the static folder, rather than letting Flask do it.
- This will take a while to get fully featured, but we have a lot planned.
- `jqPlot <http://www.jqplot.com>`_ comes bundled with chr, which is alright as it's MIT licensed.
- `tipsy <http://onehackoranother.com/projects/jquery/tipsy/>`_ is also bundled, again, MIT licensed.

Recaptcha
---------
To use reCAPTCHA, you have to set two fields in the Flask app's config before you run it:

- ``RECAPTCHA_PUBLIC_KEY`` - what it says on the tin
- ``RECAPTCHA_PRIVATE_KEY`` - also what it says on the tin

Check ``example.py`` to see how.

Author
------

- `plausibility <https://github.com/plausibility>`_

Contributors
------------
- huey
- `Chris Leonello <http://www.jqplot.com>`_ (made jqPlot)
- jaz303 (made tipsy)
