# -*- coding: utf-8 -*-

"""
    chru.web.slug provides an easy to use interface to the
    shortened URL slugs, allowing creation, removal, editing, and more.

    These functions depend on the SQL database, so without it they're useless.
"""

from datetime import datetime
import time
import re
import logging

import chru.utility as utility
import chru.utility.base62 as base62
import chru.web as web

def pull_stats(slug, url_for):
    """ Cluster together the statistics for a
        given slug. This pulls out information
        such as:

        - Number of clicks
        - Info about the clicks
          - Browser
          - Platform
          - Clicks per day
        - Unique/return clicks

        :param slug: the slug we're gathering statistics for
        :type slug: str
        :param url_for: the url_for() function we can use to expand urls
        :type url_for: def
        :return: statistics about a url
        :rtype: dict
    """
    row = to_row(slug)
    clicks = utility.funcs.sql().where("url", row["id"]).get(web.s._schema["clicks"])

    click_info = {
        "platforms": {"unknown": 0},
        "browsers": {"unknown": 0},
        "pd": {} # clicks per day
    }
    month_ago = int(time.time()) - (60 * 60 * 24 * 30) # Last 30 days
    month_ago_copy = month_ago

    for x in xrange(1, 31):
        # Pre-populate the per day clicks dictionary.
        # This makes life much much easier for everything.
        month_ago_copy += (60 * 60 * 24) # one day
        strf = str(datetime.fromtimestamp(month_ago_copy).strftime("%m/%d"))
        click_info["pd"][strf] = 0

    for click in clicks:
        if click["time"] > month_ago:
            # If the click is less than a month old
            strf = str(datetime.fromtimestamp(click["time"]).strftime("%m/%d"))
            click_info["pd"][strf] += 1

        if len(click["agent"]) == 0 \
                or len(click["agent_platform"]) == 0 \
                or len(click["agent_browser"]) == 0:
            click_info["platforms"]["unknown"] += 1
            click_info["browsers"]["unknown"] += 1
            continue

        platform_ = click["agent_platform"]
        browser_ = click["agent_browser"]

        if not platform_ in click_info["platforms"]:
            click_info["platforms"][platform_] = 1
        else:
            click_info["platforms"][platform_] += 1

        if not browser_ in click_info["browsers"]:
            click_info["browsers"][browser_] = 1
        else:
            click_info["browsers"][browser_] += 1

    # Formatting in directly without escapes, how horrible am I!
    # But these are known to be *safe*, as they're set by us.
    unique = utility.funcs.sql().query("SELECT COUNT(DISTINCT `{0}`) AS \"{1}\" FROM `{2}`".format("ip", "unq", web.s._schema["clicks"]))
    unique = unique[0]["unq"]

    rpt = len(clicks) - unique
    if len(clicks) == 0:
        rpt = 0

    f_unique = unique
    f_clicks = len(clicks) if len(clicks) != 0 else 1

    hits = {
        "all": len(clicks),
        "unique": unique,
        "return": rpt,
        # (unique / all)% of visits only come once
        "ratio": str(round(float(f_unique) / float(f_clicks), 2))[2:]
    }

    stats = {
        "hits": hits,
        "clicks": click_info,
        "long": row["long"],
        "long_clip": row["long"],
        "short": row["short"],
        "short_url": url_for("slug_redirect", slug=row["short"], _external=True)
    }

    if len(row["long"]) > 30:
        stats["long_clip"] = row["long"][:30] + "..."

    return stats

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
    old_slug = utility.funcs.sql().where("long", url).get(web.s._schema["redirects"])
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
    row = sq.insert(web.s._schema["redirects"], data)
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
    if utility.funcs.sql().where("id", id).update(web.s._schema["redirects"], update):
        slug = utility.funcs.sql().where("id", id).get(web.s._schema["redirects"])[0]
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
    if slug[:len(web.s._schema["char"])] == web.s._schema["char"]:
        rows = utility.funcs.sql().where("short", slug).get(web.s._schema["redirects"])
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

    if slug[:len(web.s._schema["char"])] == web.s._schema["char"]:
        rows = utility.funcs.sql().where("short", slug).get(web.s._schema["redirects"])
    else:
        rows = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._schema["redirects"])
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
    rows = utility.funcs.sql().where("url", id).get(web.s._schema["clicks"])
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
    if slug[:len(web.s._schema["char"])] == web.s._schema["char"]:
        rows = utility.funcs.sql().where("short", slug).get(web.s._schema["redirects"])
    else:
        rows = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._schema["redirects"])
    return len(rows) == 1

def is_valid(slug):
    """ Attempts to saturate a slug, to check validity.
        Custom slugs are assumed to be valid, unless otherwise shown.

        :param slug: the slug to check the validity of
        :type slug: str
        :return: whether the slug is valid
        :rtype: bool
    """
    if slug[:len(web.s._schema["char"])] == web.s._schema["char"]:
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
    if slug[:len(web.s._schema["char"])] == web.s._schema["char"]:
        row = utility.funcs.sql().where("short", slug).get(web.s._schema["redirects"])[0]
    else:
        row = utility.funcs.sql().where("id", slug_to_id(slug)).get(web.s._schema["redirects"])[0]
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
    return utility.funcs.sql().insert(web.s._schema["clicks"], data)

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
    rem_slug = utility.funcs.sql().where("id", id).delete(web.s._schema["redirects"])
    rem_click = utility.funcs.sql().where("url", id).delete(web.s._schema["clicks"])
    if not rem_slug or not rem_click:
        logging.debug("Unable to fully delete: %s, rem_slug: %s, rem_click: %s", slug, rem_slug, rem_click)
    return rem_slug

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