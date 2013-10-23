Usage
=====

What good is a URL shortener if it's not shortening URLs? None, I say. **NONE!**

Installation
------------

Installing chr is as easy as following these simple steps:

- Clone the latest repo: ``git clone https://github.com/plausibility/chr.git`` (then ``cd chr``)
- Install the package: ``python setup.py install``
- Copy and modify the example script: ``cp example.py mychr.py && $EDITOR mychr.py``
- Run chrso: ``gunicorn -b 127.0.0.1:5000 -p /tmp/chr.pid mychr:app``

Want to configure your instance (hint: you probably do)? ``example.py`` has all the essentials.

Running multiple instances
--------------------------

Assuming you're using something like gunicorn (as suggested), you can simply specify a different pid file, and that will handle itself.

If you want to isolate the databases (let's be honest, you probably do), you'll have to specifically set ``chrso.redis_namespace`` to something specific to each.

Keep this in mind if you ever want to hit up the database to remove or modify URLs, also.

.. code-block:: python

    # In chr1.py (`gunicorn ... chr1:app`)
    import chrso
    chrso.redis_namespace = "chr1"
    from chrso.main import app
    other_app_setup()

    # In chr2.py (`gunicorn ... chr2:app`)
    import chrso
    chrso.redis_namespace = "chr2"
    from chrso.main import app
    other_app_setup()

Validation
----------

When users submit a URL to be shortened, they're pushed against a rough URL-like regex provided by WTForms.

There's no baked in checks for legitimate domains, ``200 OK`` replies or anything like that [open an issue on the repo if you're interested and I'll work on it].

Logging
-------

Logging is not implemented as of the ``3.x`` branch anymore - but there's not much that can happen, so don't fret.
(Gunicorn probably provides it, not 100%)

Moderation
----------

At the current time of writing [v3.0.8], there is currently no way to moderate the shortened URLs built into chr.

If you're serious about removing links, or you need to remove a link which has been reported to you,
you'll have to use redis-cli.

Say we want to remove ``url.example.org/foo`` because it's scum:

.. code-block:: sh

    $ redis-cli
    # Pull the row id
    redis 127.0.0.1:6379> hget chr:id_map foo
    "1"
    # Ensure it's the URL we're expecting
    redis 127.0.0.1:6379> get chr:url:1:long
    "https://mallory.example.com/some_scummy.exe"
    # Remove it from the id_map
    redis 127.0.0.1:6379> hdel chr:id_map 1
    (integer) 1
    redis 127.0.0.1:6379> exit
    $

Simply removing a URL from the ``id_map`` will mean it's not accessible for users, but you will still have the long/short url, related info (IP, useragent) about the submitter, etc.

Clean deployment
----------------
If you want to deploy chr somewhere in production (which you.. would if you're reading this) you'll want to look at one of the standard deployment options for Flask.

It's also a nice idea to bind to a unix socket rather than a port. Just tidier:

``gunicorn -b unix:/tmp/chr.sock -p /tmp/chr.pid example:app``

nginx
^^^^^

.. code-block::

    upstream chrso {
        server unix:/tmp/chr.sock;
    }

    server {
        server_name chr.so;

        location / {
            proxy_pass http://chrso;
        }

        # Let nginx serve static files
        location /static/ {
            # Wherever you installed `chrso`
            root /path/to/chrso;
        }
    }

lighttpd
^^^^^^^^

TODO!
