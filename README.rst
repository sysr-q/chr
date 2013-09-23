chr url shortener
=================

NB!
---
As of the `v3 refactor <https://github.com/plausibility/chr/tree/v3-refactor>`_ how you interact with chr (as a sysadmin) has changed significantly. You still install it via PyPI (probably), but you'll have to run it with something like gunicorn rather than via a command line script explicity for chr.  
More info on this later into the refactor.

JSON in v3 and beyond
---------------------
If you want to get the statistics of a given URL in JSON format, you can simply smack `.json` on the end of the stats url (``http://blah.tld/x/stats.json``) and get back some lovely JSON.

If the URL doesn't exist you'll get back something with ``error: true``, so just check the ``message`` field and you're good.

****

.. _docs: http://chr.rtfd.org

**chr** (coded under the name ``chrso``) is a Python based URL shortening service which uses Flask as a front end, and pysqlw as the SQL backend, to interface with sqlite3.

It can shrink billions of unique URLs with less than 6 characters, run in the background with no human interaction, and it can fly like a bird -- or is that Super Man?

Features
--------

- Can shorten several billion (yes!) unique urls to a less than 6 character slug.
- Optionally verifies the shrunk URLs are legitimate, to stop abuse.
- Can use reCAPTCHA to stop spammers from using the service for evil. (but it's optional!)
- A live chr instance is located at `chr.so <http://chr.so>`_.

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

Running
-------

Visit the `docs`_ page, and click **Usage** for information on how to run chr.

Recaptcha
---------
To use reCAPTCHA, you have to set two fields in the Flask app's config before you run it:

- ``RECAPTCHA_PUBLIC_KEY`` - what it says on the tin
- ``RECAPTCHA_PRIVATE_KEY`` - also what it says on the tin

More on this when v3-refactor is merged and documented.

Author
------

- `plausibility <https://github.com/plausibility>`_

Contributors
------------
- huey
- `Chris Leonello <http://www.jqplot.com>`_ (made jqPlot)
- jaz303 (made tipsy)