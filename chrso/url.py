# -*- coding: utf-8 -*-
import time

import redis

red = redis.StrictRedis()

def add(long, statistics, burn, short=None, ip=None, ptime=None):
    """ Shorten a long URL and add it to our database.

        :param long: the long URL we're wishing to shorten
        :param statistics: should we bother enabling statistics
            for the shortened URL?
        :param burn: should this be a "burn after reading" URL?
        :param short: an optional custom URL
        :param ip: the IP address the URL was shortened by
        :param ptime: the time of the shorten (time.time() is
            used if omitted)
    """
    pass

def remove(ident, ident_is_short=False):
    """ Remove a shortened URL from our database.

        :param ident: an identifier for the URL we want to remove.
        :param ident_is_short: if this is True, the given :ident: is
            actually a shortened URL which we want to remove, rather
            than a row ID.
    """
    pass

def hit(ident, ident_is_short=False, ip=None, ua=None, ptime=None):
    """ Add a 'hit' to the database for a given URL.
        If the given URL is a "burn after reading" url, it will be
        expunged by this function.
        If the given URL has statistics turned *off*, this won't do anything
        unless we're removing a burn after reading URL.

        :param ident: an identifier for the URL we want to add a hit to.
        :param ident_is_short: if this is True, the given :ident: is
            actually a shortened URL which we want to remove, rather
            than a row ID.
    """
    pass

def should_burn(ident, ident_is_short=False):
    """ Find out whether or not the given URL is a burn after reading URL.

        :param ident: an identifier for the URL we want info about.
        :param ident_is_short: if this is True, the given :ident: is
            actually a shortened URL which we want to remove, rather
            than a row ID.
    """
    pass

def exists(ident, ident_is_short=True):
    """ Find out whether the given ident (URL, usually) exists.

        :param ident: an identifier for the URL we want info about.
        :param ident_is_short: if this is True (the default), the given
            :ident is actually a shortened URL which we want to remove,
            rather than a row ID.
    """
    pass

def from_short(ident):
    """ Finds the given row identifer from the short (URL) identifier.

        :param ident: the shortened URL we're trying to find an ID for.
    """
    pass
