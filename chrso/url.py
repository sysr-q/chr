# -*- coding: utf-8 -*-
import time
import argparse
import string
import random

import redis

import chrso.base62

red = redis.StrictRedis()

rand_string = lambda n: "".join(
        random.choice(string.letters + string.digits)
        for _ in xrange(n)
    )

def partial_format(part):
    """ This is just a convenience function so rather than putting
        schema.thing.format(blah) everywhere, we just schema.thing(blah)
    """
    def form(*args, **kwargs):
        return part.format(*args, **kwargs)
    return form

schema = argparse.Namespace(**{
    "last": "chr:last",  # INCR this, yo
    "id_map": "chr:id_map",  # k/v map of short -> id

    # format in id from `id_map`
    "url_long": partial_format("chr:url:{0}:long"),
    "url_stats": partial_format("chr:url:{0}:stats"),  # {0,1} only pls
    "url_burn": partial_format("chr:url:{0}:burn"),  # {0,1} only pls
    "url_short": partial_format("chr:url:{0}:short"),
    "url_useragent": partial_format("chr:url:{0}:useragent"),
    "url_ip": partial_format("chr:url:{0}:ip"),
    "url_time": partial_format("chr:url:{0}:time"),
    "url_delete": partial_format("chr:url:{0}:delete"),  # deletion key
    "url_hits": partial_format("chr:url:{0}:hits"),  # list of hit ids

    # format in hit ids from `url_hits`, yo
    "hit_useragent": partial_format("chr:hit:{0}:useragent"),  # UA string
    "hit_os": partial_format("chr:hit:{0}:os"),  # Flask reported operating system
    "hit_time": partial_format("chr:hit:{0}:time"),  # int(time.time())
    "hit_ip": partial_format("chr:hit:{0}:ip"),
})

def add(long_, statistics, burn, short=None, ua=None, ip=None, ptime=None, delete=None):
    """ Shorten a long URL and add it to our database.

        :param long_: the long URL we're wishing to shorten
        :param statistics: should we bother enabling statistics
            for the shortened URL? {0,1} or {True,False} please
        :param burn: should this be a "burn after reading" URL?
        :param short: an optional custom URL
        :param ua: the user-agent of the person the URL was shortened by.
        :param ip: the IP address the URL was shortened by
        :param ptime: the time of the shorten (time.time() is
            used if omitted)
        :param delete: the deletion key that can be used to remove the
            url by the user.
        :return: True/False, depending on if the URL was added.
    """
    if short is not None and exists(short):
        return False
    last = red.incr(schema.last)
    if short is None:
        short = chrso.base62.dehydrate(last)
    if ua is None:
        ua = ""
    if ip is None:
        ip = ""
    if ptime is None:
        ptime = int(time.time())
    if delete is None:
        delete = rand_string(32)
    # put this in our key map
    red.hset(schema.id_map, short, last)
    # add the relevant bits for this url
    red.set(schema.url_long(last), long_)
    red.set(schema.url_stats(last), int(statistics))
    red.set(schema.url_burn(last), int(burn))
    red.set(schema.url_short(last), short)
    red.set(schema.url_useragent(last), ua)
    red.set(schema.url_ip(last), ip)
    red.set(schema.url_time(last), ptime)
    red.set(schema.url_delete(last), delete)
    # url_hits is created on lpush()
    return True


def remove(ident, ident_is_short=False):
    """ Remove a shortened URL from our database.

        :param ident: an identifier for the URL we want to remove.
        :param ident_is_short: if this is True, the given :ident: is
            actually a shortened URL which we want to remove, rather
            than a row ID.
    """
    if not exists(ident, ident_is_short):
        return False
    if ident_is_short:
        ident = from_short(ident)
    short = red.get(schema.url_short(ident))
    hits = red.lrange(schema.url_hits(ident), 0, -1)
    fmts = [schema.hit_useragent,schema.hit_os,schema.hit_time,schema.hit_ip]
    # shoutouts to: akiaki
    hits = reduce(lambda x, y: x+y, [[f.format(i) for f in fmts] for i in hits])
    red.hdel(schema.id_map, short)  # remove the short from our id_map
    red.delete(
        schema.url_long(ident),
        schema.url_stats(ident),
        schema.url_burn(ident),
        schema.url_short(ident),
        schema.url_useragent(ident),
        schema.url_ip(ident),
        schema.url_time(ident),
        schema.url_delete(ident),
        *hits  # kill all the hits too
    )
    return True


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
