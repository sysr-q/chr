# -*- coding: utf-8 -*-

"""
    chru.web.slug provides an easy to use interface to the
    shortened URL slugs, allowing creation, removal, editing, and more.

    These functions depend on the SQL database, so without it they're useless.
"""

import time
import re
import logging

import chru.utility as utility
import chru.utility.base62 as base62
import chru.web as web


def url_to_slug(url, ip=False, slug=False):
    """ Shrinks a URL to the slug equivalent.

        No URL length limits are imposed, these should
        be done **before** calling.

        :param url: the long URL to shrink
        :type url: str
        :param ip: the IP address of the creator
        :type ip: str or False
        :param slug: the custom slug (if any) to use. If not given, one is created.
        :type slug: str or False
        :return: tuple with (shortened slug, row id, deletion key, long url, old or new url)
        :rtype: tuple
    """
    old_slug = utility.funcs.sql().where("long", url).get(web.s._SCHEMA_REDIRECTS)
    if len(old_slug) > 0:
        # url already shortened, give that.
        old_slug = old_slug[0]
        return (old_slug["short"], old_slug["id"], old_slug["delete"], old_slug["long"], True,)
    data = {
        "long": url,
        "short": "",
        "delete": make_delete_slug(),
        "ip": ip if ip else ""
    }
    sq = utility.funcs.sql()
    row = sq.insert(web.s._SCHEMA_REDIRECTS, data)
    if not row:
        logging.debug("Unable to insert: %s", data)
        return False
    id = sq.wrapper.cursor.lastrowid
    if not slug:
        logging.debug("Got %s from slug add: %s", id, url)
        slug = id_to_slug(id)
    update = {
        "short": slug
    }
    if utility.funcs.sql().where("id", id).update(web.s._SCHEMA_REDIRECTS, update):
        slug = utility.funcs.sql().where("id", id).get(web.s._SCHEMA_REDIRECTS)[0]
        return (slug["short"], slug["id"], slug["delete"], slug["long"], False,)
    else:
        return False

### conversions

def slug_to_id(slug):
    """ Turns a short slug into the row ID equivalent, using base62.

        For custom slugs, this is simply done by querying the database.

        :param slug: the shortened slug to convert
        :type slug: str
        :return: the slug's ID, if any.
        :rtype: int
        :raises: ValueError
    """
    if slug[:len(web.s._CUSTOM_CHAR)] == web.s._CUSTOM_CHAR:
        rows = utility.funcs.sql().where("short", slug).get(web.s._SCHEMA_REDIRECTS)
        if len(rows) != 1:
            return False
        return rows[0]["id"]

    if not is_valid(slug):
        return False
    if not isinstance(slug, basestring):
        raise ValueError("Wanted str, got " + str(type(slug)))
    return base62.saturate(slug)

def id_to_slug(id):
    """ Dehydrates an integer into the string equivalent.

        :param id: the id to saturate
        :type id: int
        :return: the saturated slug, if any
        :rtype: int
        :raises: ValueError
    """
    if not isinstance(id, int):
        raise ValueError("Wanted int, got " + str(type(id)))
    return base62.dehydrate(id)

def to_row(slug):
    """ Returns all database row information relating to a slug.

        Custom slug info is found by querying the database.

        :param slug: the slug to pull the data for
        :type slug: str
        :return: the slug's database row (False if not found)
        :rtype: dict or False
    """
    if not is_valid(slug):
        return False

    if slug[:len(web.s._CUSTOM_CHAR)] == web.s._CUSTOM_CHAR:
        rows = utility.funcs.sql().where("short", slug).get(web.s._SCHEMA_REDIRECTS)
    else:
        rows = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._SCHEMA_REDIRECTS)
    return rows[0] if len(rows) == 1 else False

### info

def hits(slug):
    """ Return the number of clicks a slug has had.
        This is done by pulling all the clicks from the database,
        then counting them.

        :param slug: the slug to count clicks for
        :type slug: str
        :return: the number of clicks the slug has
        :rtype: int
    """
    if not is_valid(slug):
        return 0
    id = slug_to_id(slug)
    rows = utility.funcs.sql().where("url", id).get(web.s._SCHEMA_CLICKS)
    return len(rows)

def exists(slug):
    """ Check if a given slug actually exists.
        This will just query the database and verify that there is only one row.

        :param slug: the slug to check the existance of
        :type slug: str
        :return: if the slug exists
        :rtype: bool
    """
    if not is_valid(slug):
        return False
    if slug[:len(web.s._CUSTOM_CHAR)] == web.s._CUSTOM_CHAR:
        rows = utility.funcs.sql().where("short", slug).get(web.s._SCHEMA_REDIRECTS)
    else:
        rows = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._SCHEMA_REDIRECTS)
    return len(rows) == 1

def is_valid(slug):
    """ Attempts to saturate a slug, to check validity.
        Custom slugs are assumed to be valid, unless otherwise shown.

        :param slug: the slug to check the validity of
        :type slug: str
        :return: whether the slug is valid
        :rtype: bool
    """
    if slug[:len(web.s._CUSTOM_CHAR)] == web.s._CUSTOM_CHAR:
        return True

    try:
        base62.saturate(slug)
        return True
    except (TypeError, ValueError) as e:
        logging.debug(e)
        return False

def url_from_slug(slug):
    """ Find the long URL a slug is hiding.
        This is simply found by querying the database for the data.

        :param slug: the slug to expand to a long url
        :type slug: str
        :return: the expanded URL (or False if invalid)
        :rtype: str or bool
    """
    if not is_valid(slug):
        return False
    if not exists(slug):
        return False
    if slug[:len(web.s._CUSTOM_CHAR)] == web.s._CUSTOM_CHAR:
        row = utility.funcs.sql().where("short", slug).get(web.s._SCHEMA_REDIRECTS)[0]
    else:
        row = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._SCHEMA_REDIRECTS)[0]
    return row["long"]

### modification

def add_hit(slug, ip, ua, time_=None):
    """ Add a click for the given slug to the database.
        Stores the user agent info, as well as IP address and timestamp.

        :param slug: the slug to add a click for
        :type slug: str
        :param ip: the IP address of the clicking user
        :type ip: str
        :param ua: the Flask useragent object for the clicking user
        :type ua: Flask useragent object
        :param time\_: an optional unix timestamp to attach to the click (defaults to now)
        :type time\_: int or None
        :return: whether or not the insertation was successful
        :rtype: bool
    """
    if not is_valid(slug):
        return False
    if time_ is None:
        time_ = int(time.time())
    id = slug_to_id(slug)
    data = {
        "url": id,
        "ip": ip,
        "time": time_,
        # agent is max of 256 characters, for brevity.
        "agent": ua.string[:256] if not ua.string == None else "",
        "agent_platform": ua.platform if not ua.platform == None else "",
        "agent_browser": ua.browser if not ua.browser == None else "",
        "agent_version": ua.version if not ua.version == None else "",
        "agent_language": ua.language if not ua.language == None else ""
    }
    return utility.funcs.sql().insert(web.s._SCHEMA_CLICKS, data)

def delete(slug):
    """ Delete the given slug entirely from the database.
        This will also delete any clicks attached to this slug, to save (a little) space.

        :param slug: the slug to delete
        :type slug: str
        :return: whether or not the deletions were successful
        :rtype: bool
    """
    if not is_valid(slug) or not exists(slug):
        return False
    id = slug_to_id(slug)
    rem_slug = utility.funcs.sql().where("id", id).delete(web.s._SCHEMA_REDIRECTS)
    rem_click = utility.funcs.sql().where("url", id).delete(web.s._SCHEMA_CLICKS)
    return rem_slug and rem_click

### generators

def make_delete_slug(length=64):
    """ Generate a deletion key for a slug.
        This is used incase the user wants to delete their URL.

        :param length: the length of the key
        :type length: int
        :return: a deletion key
        :rtype: str
    """
    import string, random
    parts = string.uppercase + string.lowercase + string.digits
    return "".join(random.choice(parts) for x in range(length))