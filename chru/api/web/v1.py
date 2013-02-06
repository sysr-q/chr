# -*- coding: utf-8 -*-

import functools
import logging
import re

from flask import Blueprint, Flask, render_template, session, abort, request
from flask import g, redirect, url_for, flash, make_response, jsonify

import chru
import chru.web
import chru.utility.funcs as funcs

app = Blueprint('api_v1', __name__, template_folder="templates")

# Some constants that we'll use lots.
def _api_disabled(): # 1
    return {
        "error": "true",
        "enum": chru.codes.api_disabled,
        "message": "The chr API is disabled"
    }

def _url_too_long(): # 3
    return {
        "error": "true",
        "enum": chru.codes.url_too_long,
        "message": "The supplied URL was actually TOO long to shorten!"
    }

def _url_invalid(): # 4
    return {
        "error": "true",
        "enum": chru.codes.url_invalid,
        "message": "The supplied URL was unable to be validated."
    }

def _custom_url_invalid(msg): # 5
    return {
        "error": "true",
        "enum": chru.codes.custom_url_invalid,
        "message": msg
    }

def _partial_form_data(missing): # 6
    return {
        "error": "true",
        "enum": chru.codes.partial_form_data,
        "message": "You left fields: '{0}' out of your form".format("', '".join(missing))
    }

def _no_such_key(): # 7
    return {
        "error": "true",
        "enum": chru.codes.no_such_key,
        "message": "That API key does not exist"
    }

def _no_such_url(): # 8
    return {
        "error": "true",
        "enum": chru.codes.no_such_url,
        "message": "That shortened URL does not exist"
    }

# Decorators to make life easy as pie for us.

def requires_api():
    """ Decorates a function so that it will return
        an error if the chr API has been disabled.
    """
    def decorator(wrap_function):
        def wrapped_function(*args, **kwargs):
            if not chru.web.s.api_enabled:
                return jsonify(_api_disabled())
            return wrap_function(*args, **kwargs)
        return functools.update_wrapper(wrapped_function, wrap_function)
    return decorator

def requires_key():
    """ Decorates a function so that if the given
        api key is invalid, or there is no key
        given, it will return an error.
    """
    def decorator(wrap_function):
        def wrapped_function(*args, **kwargs):
            if "api_key" not in request.form:
                return jsonify(_no_such_key())
            api_key = request.form["api_key"]
            rows = funcs.sql().where("key", api_key).get(chru.web.s._schema["api"])
            if len(rows) != 1:
                return jsonify(_no_such_key())
            return wrap_function(*args, **kwargs)
        return functools.update_wrapper(wrapped_function, wrap_function)
    return decorator    

def requires_data(required):
    """ Decorates a function so that required
        form data is not present, it will
        return an error.
    """
    required = required + ["api_key"]
    def decorator(wrap_function):
        def wrapped_function(*args, **kwargs):
            missing = []
            for req in required:
                if req in request.form:
                    continue
                missing.append(req)
            if missing:
                return jsonify(_partial_form_data(missing))
            return wrap_function(*args, **kwargs)
        return functools.update_wrapper(wrapped_function, wrap_function)
    return decorator

# ----- DECORATORS

# !NB!
# You should put @app.route() calls BEFORE
# you call our @requires_*() decorators.
# The other way around means that Flask will
# directly bypass our wrapping, which is bad.

@app.route("/testing", methods=["POST"])
@requires_api()
@requires_key()
@requires_data(["hello", "test"])
def testing():
    return jsonify(request.form)

@app.route("/delete")
@app.route("/stats")
@app.route("/submit")
@requires_api()
def api_req_get():
    return jsonify({
        "error": "true",
        "enum": chru.codes.not_post,
        "message": "Please send all API requests as POST"
    })

@app.route("/submit", methods=["POST"])
@requires_api()
@requires_key()
@requires_data(["long", "short", "delete"])
def submit():
    url_long = request.form["long"]
    url_short = request.form["short"]
    url_delete = request.form["delete"]

    if chru.web.s.validate_urls:
        valid = funcs.validate_url(
            url=url_long,
            regex=chru.web.s.validate_regex,
            use_requests=chru.web.s.validate_requests,
            fallback=chru.web.s.validate_fallback,
            timeout=5
        )
        if not valid:
            return jsonify(_url_invalid())

    custom_slug = False
    if len(url_short) > 0:
        invalid_slug = False

        if not re.match("^[\w-]+$", url_short):
            invalid_slug = "That custom URL is invalid. Only alphanumeric characters, dashes and underscores, please!"
        elif len(url_short) > chru.web.s._slug_max:
            invalid_slug = "That custom URL is too long! Less than 32 characters, please!"
        elif url_short.lower() in chru.web.s.reserved:
            invalid_slug = "Sorry, that custom URL is reserved!"
        elif chru.web.slug.exists(chru.web.s._schema["char"] + url_short):
            invalid_slug = "Sorry, that custom URL already exists!"

        if invalid_slug:
            return jsonify(_custom_url_invalid(invalid_slug))

        custom_slug = chru.web.s._schema["char"] + url_short

    # Yippee, it's valid!

    slug_, id_, delete_, url_, old_ = chru.web.slug.url_to_slug(
        url_long,
        ip=funcs.real_ip(),
        slug=custom_slug
    )

    delete_ = delete_ if url_delete and not old_ else ""

    data = {
        "error": "false",
        "enum": chru.codes.ok,
        "message": "Successfully shrunk your URL!" if not old_ else "URL already shrunk, here it is!",
        "url": funcs.url_for("slug_redirect", slug=slug_, _external=True),
        "short": slug_,
        "delete": delete_,
        "given": url_
    }
    return jsonify(data)

@app.route("/stats", methods=["POST"])
@requires_api()
@requires_key()
@requires_data(["short"])
def stats():
    url_short = request.form["short"]
    if not chru.web.slug.is_valid(url_short) or not chru.web.slug.exists(url_short):
        return jsonify(_no_such_url())

    stats = chru.web.slug.pull_stats(url_short, funcs.url_for)
    stats = dict({
        "error": "false",
        "enum": chru.codes.ok,
        "message": "Here are your stats, piping hot from the oven!"
    }.items() + stats.items())

    return jsonify(stats)

@app.route("/delete", methods=["POST"])
@requires_api()
@requires_key()
@requires_data(["short", "delete"])
def delete():
    url_short = request.form["short"]
    url_delete = request.form["delete"]
    if not chru.web.slug.is_valid(url_short) or not chru.web.slug.exists(url_short):
        return jsonify(_no_such_url())

    row = chru.web.slug.to_row(url_short)
    if url_delete != row["delete"]:
        logging.debug("%s gave invalid delete code: %s", funcs.real_ip(), url_delete)
        return jsonify({
            "error": "true",
            "enum": chru.codes.deletion_invalid,
            "message": "The given delete code was invalid"
        })

    deleted = chru.web.slug.delete(url_short)

    url = funcs.url_for("slug_redirect", slug=row["short"], _external=True)

    if deleted:
        return jsonify({
            "error": "false",
            "enum": chru.codes.ok,
            "message": "Successfully deleted {0}".format(url)
        })
    else:
        return jsonify({
            "error": "true",
            "enum": chru.codes.deletion_failed,
            "message": "Unable to delete {0}".format(url)
        })

@app.route("/expand", methods=["POST"])
@requires_api()
@requires_key()
@requires_data(["short"])
def expand():
    url_short = request.form["short"]
    if not chru.web.slug.is_valid(url_short) or not chru.web.slug.exists(url_short):
        return jsonify(_no_such_url())

    row = chru.web.slug.to_row(url_short)

    return jsonify({
        "error": "false",
        "enum": chru.codes.ok,
        "message": "Here's the expanded URL",
        "long": row["long"],
        "short": row["short"]
    })