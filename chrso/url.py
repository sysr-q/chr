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
    "last_hit": "chr:last_hit",  # INCR this as well
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
    "hit_ip": partial_format("chr:hit:{0}:ip"),
    "hit_time": partial_format("chr:hit:{0}:time"),  # int(time.time())
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
        :return: False if url add failed, (slug, delete) otherwise
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
    return (short, delete)


def remove(ident):
    """ Remove a shortened URL from our database.

        :param ident: an identifier for the URL we want to remove.
    """
    if not exists(ident):
        return False
    id_ = row_id(ident)
    short = red.get(schema.url_short(id_))
    hits = red.lrange(schema.url_hits(id_), 0, -1)
    fmts = [schema.hit_useragent, schema.hit_time, schema.hit_ip]
    # shoutouts to: akiaki
    if hits:
        hits = reduce(lambda x, y: x+y, [[f(i) for f in fmts] for i in hits])
    red.hdel(schema.id_map, short)  # remove the short from our id_map
    red.delete(
        schema.url_long(id_),
        schema.url_stats(id_),
        schema.url_burn(id_),
        schema.url_short(id_),
        schema.url_useragent(id_),
        schema.url_ip(id_),
        schema.url_time(id_),
        schema.url_delete(id_),
        *hits  # kill all the hits too
    )
    return True


def hit(ident, ua=None, ip=None, ptime=None):
    """ Add a 'hit' to the database for a given URL.
        If the given URL is a "burn after reading" url, it will be
        expunged by this function.
        If the given URL has statistics turned *off*, this won't do anything
        unless we're removing a burn after reading URL.

        :param ident: an identifier for the URL we want to add a hit to.
        :param ua: the user-agent of the user
        :param ip: the IP of the user
        :param ptime: the time the hit occured (None means current time)
    """
    if not exists(ident):
        return False
    if should_burn(ident):
        return remove(ident)
    id_ = row_id(ident)
    has_stats = bool(int(red.get(schema.url_stats(id_))))
    if not has_stats:
        # We're intentionally doing nothing.
        return True
    last = red.incr(schema.last_hit)
    if ua is None:
        ua = ""
    if ip is None:
        ip = ""
    if ptime is None:
        ptime = int(time.time())
    red.set(schema.hit_useragent(last), ua)
    red.set(schema.hit_ip(last), ip)
    red.set(schema.hit_time(last), ptime)
    red.lpush(schema.url_hits(id_), last)  # push this to the url hits
    return True


def hits(ident):
    if not exists(ident):
        return
    id_ = row_id(ident)
    hits = []
    hit_ids = red.lrange(schema.url_hits(id_), 0, -1)
    for hit in hit_ids:
        hits.append({
            "useragent": red.get(schema.hit_useragent(hit)),
            "time": int(red.get(schema.hit_time(hit))),
            "ip": red.get(schema.hit_ip(hit))
        })
    return hits


def should_burn(ident):
    """ Find out whether or not the given URL is a burn after reading URL.

        :param ident: an identifier for the URL we want info about.
    """
    if not exists(ident):
        return False
    id_ = row_id(ident)
    burn = int(red.get(schema.url_burn(id_)))
    return bool(burn)


def delete_key(ident):
    if not exists(ident):
        return
    id_ = row_id(ident)
    return red.get(schema.url_delete(id_))


def exists(ident):
    """ Find out whether the given ident (URL, usually) exists.

        :param ident: an identifier for the URL we want info about.
    """
    return red.hexists(schema.id_map, ident)


def long(ident):
    if not exists(ident):
        return
    id_ = row_id(ident)
    return red.get(schema.url_long(id_))

def row_id(ident):
    if not exists(ident):
        return
    return red.hget(schema.id_map, ident)
