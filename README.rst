chr url shortener
=================

NB!
---
As of the v3 refactor how you interact with chr (as a sysadmin) has changed significantly. You still install it via PyPI (TODO, updated version not up yet), but you'll have to run it with something like gunicorn rather than via a command line script explicity for chr.  

For now:

- Clone the repo
- ``python setup.py install``
- Check ``example.py`` (and the `docs <http://chr.rtfd.org>`_!) for more info on how to run it.
- Use a command like: ``gunicorn -b 127.0.0.1:5000 -p /tmp/chr.pid example:app``

JSON in v3 and beyond
---------------------
If you want to get the statistics of a given URL in JSON format, you can simply smack `.json` on the end of the stats url (``http://example.org/x/stats.json``) and get back some lovely JSON.

If the URL doesn't exist you'll get back something with ``error: true``, and a ``message`` field - check it and you're good.

**TODO:**

- [ ] add an API endpoint to shorten/expand URLs (check out ``wtforms-json`` or something)

  - [ ] rather than half-baked ``@app.route`` calls, make an API blueprint
  - [ ] add API keys so even if reCAPTCHA is enabled you can use it

- [x] update the docs to the new chrso tree
- [ ] update the screenshots in the repo
- [ ] update `chrw <https://github.com/plausibility/chrw>`_ (oooold) so that it works with chrso tree
- [x] remove some base62 crud
- [x] write a decent install/running guide (new docs)
- [ ] write a migration script for chru -> chrso trees

  - [ ] move chr.so over to the latest chrso tree and link back there
  - [ ] put this code tree on PyPI and explain changes in big bold font

- [ ] provide example nginx (+ Apache/lighttpd?) configs
- [ ] make ``url.stats()`` cache the results at redis for a few (5?) minutes

  - alternatively, we could implement ``If-Modified-Since``, but that'd be tougher.


****

**chr** (found in the package ``chrso``) is a Python based URL shortening service which uses Flask as a front end, and redis as the backend.

It can shrink billions of unique URLs with less than 6 characters, run in the background with no human interaction, and it can fly like a bird -- or is that Super Man?

Features
--------

- Can shorten several billion (yes!) unique urls to a less than 6 character slug.
- Can use reCAPTCHA to stop spammers from using the service for evil. (but it's optional!)
- A live chr instance is located at `uguu.us <http://uguu.us>`_. (NB: ``chr.so`` is the old source tree)

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
- `aki--aki <https://github.com/aki--aki>`_ convinced me to add JSON-y API stuff
