settings.json
=============

First things first, you'll need to set up your ``settings.json`` file. This is the base file that chr will pull settings from.
Without it, chr will have no legs to stand on (metaphorically).

Creating the file is easy, you simply call ``chru --make-config``, and pipe it into a file of your choice. Then it's just a small step to edit.

.. code-block:: sh

    $ chru --make-config > ~/settings.json
    $ <text editor> ~/settings.json

What's inside of the file and what does it mean? Let's delve deep into the inner configuration file of chr.

``sql_path``
  This is an **absolute** path to the sqlite3 database file we're going to store stuff in.

  Keep it somewhere which makes sense, ``/var/chr/chr.db`` or something.

  This should be a ``string``, default: ``/path/to/chr.db``

``soft_url_cap``
  This is the limit for URLs that we'll shorten. There is no hard limit (the database will store any amount of text),
  this is only a soft limit, mainly to filter out excessively long, space wasting URLs.
  
  This should be an ``int``, default: ``512``

``flask_host``
  This is the IP address we're going to bind the Flask process to. ``127.0.0.1``, ``0.0.0.0``, etc.

  This should be a ``string``, default: ``127.0.0.1``

``flask_port``
  The port that we're going to bind the Flask process to. ``8080``, ``1234``, etc. It has to be higher than ``1024``,
  as chr doesn't run with root privilege, so we're not allowed to bind to low ports.

  This should be an ``int``, default: ``8080``

``flask_base``
  .. note::
    This hasn't been implemented yet.

  In theory, this should be the URL base that Flask binds to. The Blueprint, if you're familiar with Flask.

  This should be a ``string``, default: ``/``

``flask_url``
  .. deprecated:: 2.1.0
    ``web.s.flask_url.format(...)`` was replaced by routing's ``url_for(..., _external=True)``.

  This is the displayed URL of the app. This is the output when new URLs are shrunk, we access stats about one, etc.

  It uses the formatting piece ``{slug}`` to represent the shortened URL slug.

  It's set to ``http://chr.so/{slug}`` on the official chr.so shrinking service.
  This leads to URLs like ``http://chr.so/ABCDE1``

  This should be a ``string``, default: ``http://change.this/{slug}``

``flask_secret_key``
  .. warning::
    Keep this a secret. If it falls into the wrong hands, they could use it
    to execute arbitrary code in the app, since Flask serializes cookies (wtf?).

  The secret key that Flask uses to encrypt all cookies and anything related to Flask.

  This should be a long, random ``string``, default: ``UNIQUE_KEY``

``reserved``
  .. versionadded:: 2.1.0

  This is a square bracket, string and comma delimited list of reserved keywords,
  which you can disallow for usage as a custom URL.

  This should be a ``list`` (``["foo", "bar", "baz"]``), default: ``["lots", "of", "naughty", "words"]``.

``captcha_public_key``
  This is your reCAPTCHA API public key. You can get one from the `reCAPTCHA site <https://recaptcha.com>`_.

  This should be a ``string``, default: ``YOUR_PUBLIC_API_KEY``

``captcha_private_key``
  .. warning::
    Keep this a secret. If it falls into the wrong hands, they could possibly bypass captchas. Who knows!
    If you think this has been compromised, generate a new pair.

  This is similar to ``captcha_public_key``, but it is the secret key used to verify captchas.

  This should be a ``string``, default: ``YOUR_PRIVATE_API_KEY``

``salt_password``
  .. note::
    This hasn't been implemented yet.

  .. warning::
    Keep this a secret. We don't want people to be able to try and crack your password hashes.

    If you ever change this once set, it could cause all sorts of hell to users.

  When/if user accounts are added, this will be used to salt the password strings;
  hopefully keeping them secure.

  Once this has been set, if you ever change it, it will cause all sorts of hell,
  and every user would have to reset their password.

  This should be a long, random ``string``, default: ``UNIQUE_KEY``

``validate_urls``
  The ``validate_`` settings are explained more thoroughly below.

  This will decide whether or not to bother validating URLs.
  Why should you waste space on fake or invalid URLs?

  This should be a ``boolean``, default: ``true``

``validate_requests``
  Should we use the requests module to validate URLs?

  This could be a security breach if you're hiding your service behind a caching
  network, on a secret box, or if you're in your parent's house hiding from the feds.

  This should be a ``boolean``, default: ``true``

``validate_regex``
  This is the regex that URLs are validated against if we're not using requests.

  This should only be changed if you understand what a regex is, and how they work.
  Incorrectly editing the regex can and will lead to problems down the road, including instability.

  This should be a ``string``, default: ``^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.!&()=:;?,\-%]*)\/?$``

``validate_fallback``
  Should we fall back to using the regex if requests bails on us? Keeping this on is a good idea.

  This should be a ``boolean``, default: ``true``

``api_enabled``
  .. versionchanged:: 2.1.0

  This decides whether or not your chr API is available to the outside world.

  The API provides a nice developer interface for shortening URLs.

  This should be a ``boolean``, default: ``false``

``_`` *(underscore variables)*
  .. warning::
    If you touch these, it could cause instability in the app.

    For safety, don't touch them at all.

  These are used by chr's internal structures. Modifying these will **definitely** lead to problems. Don't do it!

  The type and default varies based on the variable, you can find the default in ``chru --make-config``
