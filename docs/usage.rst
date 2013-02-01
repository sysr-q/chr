Usage
=====

.. _mattdaemon: http://github.com/plausibility/mattdaemon
.. _pypi: http://pypi.python.org/pypi/chr

What good is a URL shortener if it's not shortening URLs? None, I say. **NONE!**

Due to the usage of the `mattdaemon`_ daemonization methods, chr can run in the background; start it up, let it run!

Installation
------------
Installing chr is easy, as it is on `pypi`_; all you have to do is ``pip install chr``, or ``easy_install chr`` (if you absolutely have to),
and pip will take care of the rest of the installation for you.

Running it
----------
chr is accessible via the ``chru`` shell command (short for chr url shortener), so you don't have to do any fancy Python programming to set it up.

You'll need to create and edit the ``settings.json`` file, more info over at the :doc:`settings` page.

TL;DR
^^^^^
Do you just want the gist of this entire page? For the most part, this will be easy to grasp.

The hardest part is the settings file, but the majority of that is easy to figure out (just don't touch the underscore settings!)

Here are a few commands you can run to get chr running quickly.

.. code-block:: sh

    # Create the settings file
    $ chru --make-config > /home/user/chr-settings.json
    # Edit it with your editor of choice (I use vim)
    $ vi /home/user/chr-settings.json
    # Run the server!
    $ chru -s /home/user/chr-settings.json start
    # Make sure it ran
    $ chru status
    chr currently running! :D

In the event that chr didn't run for whatever reason, you can simply check the log file, which defaults to ``/tmp/chr-daemon.log``.

.. code-block:: sh

    $ tail /tmp/chr-daemon.log
    Given settings file (v: 2.0.0rc_X) is not supported!
    Supported: 2.0.0rc1
    Please make a new one (--make-config > settings.json) and start again.
    $

This just tells me that my settings file was an invalid/unsupported version (``2.0.0rc_X``).

The error might vary, but the log file should give you the gist, or at the very least a stack trace you can submit to the `git repo <https://github.com/plausibility/chr/issues>`_ issues.

If you do submit an issue, please paste the last few hundred lines (not all 50,000,000,001) of your log file to a paste service like `pastie <http://pastie.org>`_, or `pastebin <http://pastebin.com>`_, and link to it in your issue comment.


Start, stop, status
^^^^^^^^^^^^^^^^^^^
These are the three S's of chr. ``start``, ``stop`` and ``status``.

These are actions you pass to the ``chru`` command to control the daemon.
But what do they do?

start
  This will obviously start the daemon (if it's not already running),
  and bind the Flask server, make sure the database is set up correctly, among other things.

stop
  This will send SIGTERM to the server, forcing it to stop, then ending the process.

status
  This will print a message depending on whether or not the server is currently running.

You use these commands like such:

.. code-block:: sh

    # We need to pass the settings file to the "start" action
    $ chru -s ~/settings.json start

    # If the server is running, stop it.
    $ chru stop

    # Print the status (server not running)
    $ chru status
    chr not running! D:

    # Print the status (server running)
    $ chru status
    chr currently running! :D

Running multiple instances
^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, all chr instances will attempt to use ``/tmp/chr-daemon.pid`` as the pid (process id) file.

If you want to run multiple instances, this just won't do, so you'll have to change it to run another.
You can do this with the ``-p <file>`` or ``--pid <file>`` flags.

For example:

.. code-block:: sh

    # Run the first server
    $ chru -s ~/settings_1.json start

    # Start the second
    $ chru -s ~/settings_2.json -p /tmp/chr-daemon-2.pid start


    # Check the first server's status.
    $ chru status
    chr not running! D:

    # Check the second server's status.
    $ chru -p /tmp/chr-daemon-2.pid status
    chr currently running! :D

    # Stop the first server
    $ chru stop

    # Stop the second server
    $ chru -p /tmp/chr-daemon-2.pid stop

Validation
^^^^^^^^^^
When users submit a URL to be shrunk, they go through a series of validation phases (if enabled), before being shrunk.

These steps are as follows:

1. Ensure validation is enabled
2. Pass the URL through to :func:`chru.utility.funcs.validate_url`
3. If we're allowed to use requests, send a HEAD request, ensuring the reply is ``200 OK``.
4. If this fails for varying reasons (not ``200 OK``, or the request times out, etc),
   or we're not allowed to use requests, pass the URL through to our regex.
5. The regex will make sure the URL at least *looks* valid.
6. If all of these checks fail, the user is simply given an error message.

Logging
^^^^^^^
By default, everything is logged using the python :mod:`logging` module.
This means that nothing is actually sent to stdout (after initialization), so you'll have to check the log file.

The default log file is ``/tmp/chr-daemon.log``, which obviously isn't the ideal log file location, so it's easy to change.

If you want to change the log file, you can specify it at launch with the ``-l <file>`` and ``--log <file>`` params.

.. code-block:: sh

    $ chru -l /home/user/chr.log -s /home/user/settings.json start

This will start chr, sending all logs to ``/home/user/chr.log``.

Since things are sent directly to the log file, there isn't really a clean built-in way to view the logs live.
However, an easy way is to use the unix ``tail`` command (available on Windows with cygwin), with the ``-f`` flag.

.. code-block:: sh

    $ tail -f /home/user/chr.log

This will make tail *follow* the log file, updating it live as it's logged to.

I know, this isn't the optimal solution, but it's what you have to do due to the use of the logging module.

.. note::
    Logs are printed in the format of ``D/M/Y H:M:S(AM|PM) [LEVEL] Message here``.

    ``31/1/2013 08:52:45PM [INFO] Successfully setup app and settings!``

Moderation
^^^^^^^^^^
At the current time of writing, there is currently no way to moderate the shortened URLs built into chr.

If you're serious about removing links, or you need to remove a link which has been reported to you,
you can install the sqlite3 binary, and just:

.. code-block:: sh

    $ sqlite3 /path/to/chr.db
    sqlite> SELECT * FROM ...;
    (...)
    sqlite> DELETE FROM `redirects` WHERE ...;
    (...)
    sqlite> .exit
    $ 
