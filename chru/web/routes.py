# -*- coding: utf-8 -*-

"""
    chru.web.routes handles the Flask app.

    This module contains all of the ``@app.route`` calls,
    and it sets up the module wide settings, so the rest of
    the app can use them without problems.
"""

import json
import re
import time
from datetime import datetime
import logging

from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for as flask_url_for, flash, make_response, jsonify

from recaptcha.client import captcha

# ----- #
import chru
import chru.utility as utility
import chru.web as web
import chru.web.slug
# API versions
import chru.api.web.v1
from chru.utility.funcs import real_ip, url_for

reserved_routes = ["index", "submit"]

app = Flask(__name__)
app.jinja_env.globals.update(sorted=sorted)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(date_strip_day=utility.funcs.date_strip_day)

def set_app(debug=False, settings_file=None, log_file=None, __supported__=[], update_schema=False):
    """ Sets up the finer details of the Flask app,
        as well as the parsing in the settings file.

        :param debug: should the app be set to debug mode?
        :type debug: bool
        :param settings_file: the file handler for the given settings file
        :type settings_file: file handler
        :param log_file: the file we're going to set :mod:`logging` to use
        :type log_file: str
        :param __supported__: the list of supported settings versions
        :type __supported__: list
        :param update_schema: shall we forcefully update the database schema?
        :type update_schema: bool
    """
    settings_dict = json.load(settings_file)
    settings_file.close()
    settings = utility.struct(**settings_dict)

    web.s = settings
    web.s.debug = debug
    web.s.reserved = reserved_routes + web.s.reserved

    if "_version" not in settings_dict \
            or web.s._version not in __supported__:
        v = "unknown"
        if "_version" in settings_dict:
            v = settings_dict["_version"]
        import sys
        print "Given settings file (v: {0}) is not supported!".format(v)
        print "Supported:", ", ".join(__supported__)
        print "Please make a new one (--make-config > settings.json) and start again."
        return False

    settings_problems = []
    settings_warnings = []
    for k, v in web.skeleton.items():
        if k not in settings_dict:
            settings_problems.append("Missing required field: '{0}'".format(k))
    for k, v in settings_dict.items():
        if k not in web.skeleton:
            settings_warnings.append("Unneeded field: '{0}'".format(k))

    if settings_problems or settings_warnings:
        print "There are some problems with your settings file:"
    if settings_warnings:
        print "\n".join(settings_warnings)
    if settings_problems:
        print "\n".join(settings_problems)
        print "Please fix these and try again"
        return False

    utility.funcs.verify_sql(force=update_schema)

    app.debug = debug
    app.secret_key = str(web.s.flask_secret_key)

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S%p",
        level=logging.DEBUG,
        filename=log_file
    )
    logging.info("Successfully setup main app and settings")

    # Import each API and set it up
    app.register_blueprint(chru.api.web.v1.app, url_prefix="/api/v1")

    logging.info("Successfully setup and registered all APIs")

    return True

@app.route("/index")
@app.route("/")
def index():
    """ Simply renders the index page. """
    return render_template("index.html", recaptcha_key=web.s.captcha_public_key)

@app.route("/<slug>/")
@app.route("/<slug>")
def slug_redirect(slug):
    """ Redirects to the appropriate slug, if it exists.

        :param slug: the shortened url slug
        :type slug: str
        :return: a redirection (to index or the shortened url)
    """
    if not web.slug.is_valid(slug):
        logging.debug("%s isn't valid", slug)
        return redirect(url_for("index"))
    if not web.slug.exists(slug):
        logging.debug("%s doesn't exist", slug)
        return redirect(url_for("index"))
    url = web.slug.url_from_slug(slug)
    web.slug.add_hit(slug, real_ip(), request.user_agent)
    return redirect(url)

@app.route("/<slug>/delete/")
@app.route("/<slug>/delete")
def slug_delete_nokey(slug):
    """ Redirects back to the index if no deletion key is given. """
    return redirect(url_for("index"))

@app.route("/<slug>/delete/<delete>")
def slug_delete(slug, delete):
    """ Will attempt to delete a slug, if given a correct deletion key.

        If an invalid key is given, simply redirects to the index.

        :param slug: the shortened url slug to delete
        :type slug: str
        :param delete: the deletion key to use
        :type delete: str
        :return: a redirection to the index
    """
    if not web.slug.is_valid(slug) or not web.slug.exists(slug):
        return redirect(url_for("index"))

    row = web.slug.to_row(slug)
    if delete != row["delete"]:
        logging.debug("%s gave invalid delete code ('%s')", real_ip(), delete)
        return redirect(url_for("index"))

    deleted = web.slug.delete(slug)

    if not delete:
        logging.error("Unable to delete slug %s", slug)
        flash("Something went wrong deleting {0}".format(
            url_for("slug_redirect", slug=row["short"], _external=True)
        ), "error")
    else:
        flash("Successfully deleted {0}".format(
            url_for("slug_redirect", slug=row["short"], _external=True)
        ), "success")
    return redirect(url_for("index"))

@app.route("/<slug>/stats")
def slug_stats(slug):
    """ Pulls up all related slug information, and provides it to
        the statistics template. This gives information about the
        amount of clicks, operating systems, browsers, when it
        got the most clicks, and more.

        If there are no clicks, this really won't return much
        of value, as there is nothing!

        :param slug: the shortened url slug to show stats for
        :type slug: str
        :return: the rendered stats page or a JSON dict for API calls
        :enum: 1, 6, 7
    """
    if not web.slug.is_valid(slug) or not web.slug.exists(slug):
        return redirect(url_for("index"))

    stats = web.slug.pull_stats(slug, url_for)
    
    return render_template("stats.html", stats=stats)

@app.route("/submit", methods=["GET"])
def submit_get():
    """ Redirects GET requests to /submit to the index. """
    return redirect(url_for("index"))

@app.route("/submit", methods=["POST"])
def submit():
    """ Handles URL submissions, validating URLs,
        creating the needed slug row, and providing
        information to the client via JSON.

        This will handle invalid captchas, overly
        long URLs, invalid URLs (if validation is on),
        and custom slug related problems.

        :return: a JSON dictionary with submission info

        :enum: 7
    """
    logging.debug("HELLO, NOT USING_API HERE")
    response = captcha.submit(
        request.form["recaptcha_challenge_field"],
        request.form["recaptcha_response_field"],
        web.s.captcha_private_key,
        real_ip()
    )
    # reCAPTCHA failed
    if not response.is_valid:
        return jsonify({
            "error": "true",
            "enum": 2,
            "message": "The captcha typed was incorrect."
        })

    # long_url, custom_url, give_delete
    url_long = request.form["long_url"]
    url_short = request.form["custom_url"]
    url_delete = request.form["give_delete"] if "give_delete" in request.form else False

    # URL too long
    if len(url_long) > web.s.soft_url_cap:
        return jsonify({
            "error": "true",
            "enum": 3,
            "message": "The URL you provided was actually too long to shrink!"
        })

    # Invalid URL
    if web.s.validate_urls:
        valid = utility.funcs.validate_url(
            url=url_long,
            regex=web.s.validate_regex,
            use_requests=web.s.validate_requests,
            fallback=web.s.validate_fallback,
            timeout=5
        )
        if not valid:
            return jsonify({
                "error": "true",
                "enum": 4,
                "message": "The URL provided was unable to be validated."
            })

    # Custom URL validation (slugs)
    custom_slug = False
    if len(url_short) > 0:
        # If this isn't False at the end,
        # we display the error.
        invalid_slug = False
        slug_ = url_short

        if not re.match("^[\w-]+$", slug_):
            invalid_slug = "That custom URL is invalid. Only alphanumeric characters, dashes and underscores, please!"
        elif len(slug_) > web.s._slug_max:
            invalid_slug = "That custom URL is too long! Less than 32 characters, please!"
        elif slug_.lower() in web.s.reserved:
            invalid_slug = "Sorry, that custom URL is reserved!"
        elif web.slug.exists(web.s._schema["char"] + slug_):
            invalid_slug = "Sorry, that custom URL already exists!"

        if invalid_slug:
            return jsonify({
                "error": "true",
                "enum": 5,
                "message": invalid_slug
            })

        custom_slug = web.s._schema["char"] + slug_

    # Yippee, it's valid!

    slug_, id_, delete_, url_, old_ = web.slug.url_to_slug(
        url_long,
        ip=real_ip(),
        slug=custom_slug
    )

    # xxxx -> http://wht.nt/slug/delete/xxxx
    delete_ = url_for("slug_delete", slug=slug_, delete=delete_, _external=True)
    logging.debug("delete_ + url_for(): %s", delete_)

    delete_ = delete_ if url_delete and not old_ else ""

    data = {
        "error": "false",
        "enum": 0,
        "message": "Successfully shrunk your URL!" if not old_ else "URL already shrunk, here it is!",
        "url": url_for("slug_redirect", slug=slug_, _external=True),
        "delete": delete_,
        "given": url_
    }

    logging.debug("jsonify(data): %s", data)
    return jsonify(data)