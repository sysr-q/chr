# -*- coding: utf-8 -*-

"""
    This module just stores various functions which don't
    really fit anywhere else in the app.
"""

import pysqlw

import chru.web as web

import requests
import re
import logging

def sql():
    """ Opens an sqlite connection, returning it for usage.
    """
    return pysqlw.pysqlw(db_type="sqlite", db_path=web.s.sql_path)

def date_strip_day(date_):
    """ Strips the day out of a date.. I think.
    """
    if not "/" in date_:
        return date_
    return date_.split("/")[1]

def verify_sql():
    """ Ensure the database file is made, and if not,
        create it and populate it with the schema.
    """
    import os
    if os.path.isfile(web.s.sql_path):
        return True
    with sql() as s:
        s.wrapper.cursor.executescript(web.schema)
    add_first = web.slug.url_to_slug("https://github.com/plausibility/chr", slug=web.s._CUSTOM_CHAR + "source")
    if add_first:
        return True
    else:
        return False

def constant(f):
    """ Simple decorator for const class variables.

        For example:

        .. code-block:: python

            >>> class A:
            ...    @constant
            ...    foo = 9001
            ...
            >>> a = A()
            >>> a.foo
            9001
            >>> a.foo = 7
            (...)
            Some SyntaxError
            (...)

        :raises: SyntaxError
    """
    def fset(self, value):
        raise SyntaxError("this is a constant variable")
    def fget(self):
        return f()
    return property(fget, fset)

def validate_url(url, timeout=1, fallback=True, regex=None, use_requests=True):
    """ Checks whether or not a URL is valid.
        The URL can go through two stages, depending
        on the settings passed in.

        1. The URL can be validated by sending a HEAD request
           with the requests module, and verifying that the reply
           code (if any), is in a list of valid replies.
        2. The URL gets run against a regex, to verify that,
           structurally, the URL is atleast valid.

        If fallback is on, the URL will go through both steps (if
        the first fails), to verify the validity.

        Failure of both tests results in a validity failure, obviously.

        :param url: the URL we're testing the validity of.
        :type url: str
        :param timeout: the timeout to pass to the HEAD request. this can stop exploits
        :type timeout: int
        :param fallback: should we fallback to the regex if the request fails?
        :type fallback: bool
        :param regex: the regex we'll compare against
        :type regex: str
        :param use_requests: should we use requests first?
        :type use_requests: bool
        :return: whether or not the URL is valid
        :rtype: bool
    """
    if use_requests:
        try:
            logging.debug("Sending HEAD req to: %s", url)
            head = requests.head(url, timeout=timeout)
            logging.debug("Reply: %s", head.status_code)
            # These are some codes we're 200 OK with. (geddit?)
            valid_codes = [
                200, # OK
                204, # No Content
                301, # Moved Permanently
                302, # Found
                304, # Not Modified
                307, # Temporary Redirect (HTTP/1.1)
                308, # Permanent Redirect (HTTP/1.1)
                418, # I'm a teapot
            ]
            if head.status_code not in valid_codes:
                raise requests.exceptions.HTTPError
            return True
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            if fallback:
                return validate_url(url, timeout=timeout, fallback=False, regex=regex, use_requests=False)
            else:
                return False
    else:
        if regex is None:
            regex = web.s.validate_regex
        logging.debug("Matching '%s' against '%s'", url, regex)
        return re.match(regex, url, flags=re.I)