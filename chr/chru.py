# -*- coding: utf-8 -*-
# chr's class to convert slugs to urls, urls to slugs, delete slugs, etc.

import time
import re

import logger
import base62
import settings
import utility

#--------------------
# THE REAL DEAL (SRS)
#--------------------

def url_to_slug(url, slug=False):
	"""Turns a URL into a shortened slug.
		returns (slug, id, delete, url, old,) or False if failure.
		Doesn't impose any character length limits,
		those should be done before calling.
	"""
	old_slug = utility.sql().where('long', url).get(settings._SCHEMA_REDIRECTS)
	if len(old_slug) > 0:
		# url already shortened, give that.
		old_slug = old_slug[0]
		return (old_slug['short'], old_slug['id'], old_slug['delete'], old_slug['long'], True,)
	data = {
		"long": url,
		"short": "",
		"delete": make_delete_slug()
	}
	sq = utility.sql()
	row = sq.insert(settings._SCHEMA_REDIRECTS, data)
	if not row:
		logger.debug("Unable to insert:", data)
		return False
	id = sq.row()
	if not slug:
		logger.debug("Got", id, "from slug add:", url)
		slug = id_to_slug(id)
	update = {
		"short": slug
	}
	if utility.sql().where('id', id).update(settings._SCHEMA_REDIRECTS, update):
		slug = utility.sql().where('id', id).get(settings._SCHEMA_REDIRECTS)[0]
		return (slug['short'], slug['id'], slug['delete'], slug['long'], False,)
	else:
		return False

#------------------
# CONVERSIONS
#------------------

def slug_to_id(slug):
	"""Turns valid slugs into their integer equivalent.
		Custom slugs are found by searching the DB.
	"""
	if slug[0] == settings._CUSTOM_CHAR:
		rows = utility.sql().where('short', slug).get(settings._SCHEMA_REDIRECTS)
		if len(rows) != 1:
			return False
		return rows[0]['id']
	if not is_valid_slug(slug):
		return False
	if not isinstance(slug, basestring):
		raise ValueError('Wanted str, got ' + str(type(slug)))
	return base62.saturate(slug)

def id_to_slug(id):
	"""Turns an integer into its slug equivalent.
	"""
	if not isinstance(id, int):
		raise ValueError('Wanted int, got ' + str(type(id)))
	return base62.dehydrate(id)

#------------------
# INFO
#------------------

def slug_hits(slug):
	"""Return the number of clicks a slug has had.
	"""
	if not is_valid_slug(slug):
		return 0
	id = slug_to_id(slug)
	rows = utility.sql().where('url', id).get(settings._SCHEMA_CLICKS)
	return len(rows)

def slug_exists(slug):
	"""Check if a slug exists.
		Converts slug -> id to check.
	"""
	if not is_valid_slug(slug):
		return False
	if slug[0] == settings._CUSTOM_CHAR:
		rows = utility.sql().where('short', slug).get(settings._SCHEMA_REDIRECTS)
	else:
		rows = utility.sql().where('id', slug_to_id(slug)).get(settings._SCHEMA_REDIRECTS)
	return len(rows) == 1

def is_valid_slug(slug):
	"""Attempts to saturate a slug, to check validity.
		Custom slugs are assumed to be valid, unless otherwise shown.
	"""
	if slug[0] == settings._CUSTOM_CHAR:
		return True

	try:
		base62.saturate(slug)
		return True
	except (TypeError, ValueError) as e:
		logger.debug(e)
		return False

def url_from_slug(slug):
	"""Get the long URL attached to a slug.
		Returns long URL or False.
	"""
	if not is_valid_slug(slug):
		return False
	if not slug_exists(slug):
		return False
	if slug[0] == settings._CUSTOM_CHAR:
		row = utility.sql().where('short', slug).get(settings._SCHEMA_REDIRECTS)[0]
	else:
		row = utility.sql().where('id', slug_to_id(slug)).get(settings._SCHEMA_REDIRECTS)[0]
	return row['long']

#------------------
# MODIFICATION
#------------------

def add_hit(slug, ip, time=int(time.time())):
	"""Add a hit relating to the given slug.
		Converts slug -> id before adding.
	"""
	if not is_valid_slug(slug):
		return False
	if not re.match(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.' + \
			'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip):
		return False
	id = slug_to_id(slug)
	data = {
		"url": id,
		"ip": ip,
		"time": time
	}
	return utility.sql().insert(settings._SCHEMA_CLICKS, data)

#------------------
# GENERATORS
#------------------

def make_delete_slug(length=64):
	"""Generate a {length} long string which is 
		used as the slug deletion key.
	"""
	import string, random
	parts = string.uppercase + string.lowercase + string.digits
	return ''.join(random.choice(parts) for x in range(length))