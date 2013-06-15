chr url shortener
=================

NOTE!
=====
As of the v3.0 refactor, chr is nolonger available to install via PyPI. This is mainly because the structure of the program and how it's used has/will change.

****

.. _docs: http://chr.rtfd.org

**chr** (coded under the name ``chrso``) is a Python based URL shortening service which uses Flask as a front end, and pysqlw as the SQL backend, to interface with sqlite3.

It can shrink billions of unique URLs with less than 6 characters, run in the background with no human interaction, and it can fly like a bird -- or is that Super Man?

Features
--------

- Can shorten several billion (yes!) unique urls to a less than 6 character slug.
- Optionally verifies the shrunk URLs are legitimate, to stop abuse.
- Can use reCAPTCHA to stop spammers from using the service for evil.
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

Author
------

- `plausibility <https://github.com/plausibility>`_

Contributors
------------
- huey
- `Chris Leonello <http://www.jqplot.com>`_ (made jqPlot)
- jaz303 (made tipsy)