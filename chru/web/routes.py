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
from flask import redirect, url_for, flash, make_response, jsonify

from recaptcha.client import captcha

# ----- #
import chru
import chru.utility as utility
import chru.web as web
import chru.web.slug

app = Flask(__name__)
app.jinja_env.globals.update(sorted=sorted)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(date_strip_day=utility.funcs.date_strip_day)

def set_app(debug=False, settings_file=None, log_file=None, __supported__=[]):
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
    """
    settings_dict = json.load(settings_file)
    settings_file.close()
    settings = utility.struct(**settings_dict)

    web.s = settings
    web.s.debug = debug

    if "_version" not in settings_dict \
            or web.s._version not in __supported__:
        v = "unknown"
        if "_version" in settings_dict:
            v = settings_dict["_version"]
        import sys
        print "Given settings file (v: {0}) is not supported!".format(v)
        print "Supported:", ", ".join(__supported__)
        print "Please make a new one (--make-config > settings.json) and start again."
        sys.exit(1)

    utility.funcs.verify_sql()

    app.debug = debug
    app.secret_key = str(web.s.flask_secret_key)

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S%p",
        level=logging.DEBUG,
        filename=log_file
    )
    logging.info("Successfully setup app and settings!")

reserved_routes = ("index", "submit")

@app.route("/index")
@app.route("/")
def index():
    """ Simply renders the index page. """
    return render_template("index.html", recaptcha_key=web.s.captcha_public_key)

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
    web.slug.add_hit(slug, request.remote_addr, request.user_agent)
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
        logging.debug("%s gave invalid delete code ('%s')", request.remote_addr, delete)
        return redirect(url_for("index"))

    if not web.slug.delete(slug):
        logging.error("Unable to delete slug %s", slug)
        flash("Something went wrong deleting {0}".format(web.s.flask_url.format(slug=row["short"])), "error")
    else:
        flash("Successfully deleted {0}".format(web.s.flask_url.format(slug=row["short"])), "success")
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
        :return: the rendered stats page
    """
    if not web.slug.is_valid(slug) or not web.slug.exists(slug):
        return redirect(url_for("index"))

    row = web.slug.to_row(slug)
    clicks = utility.funcs.sql().where("url", row["id"]).get(web.s._SCHEMA_CLICKS)

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
    unique = utility.funcs.sql().query("SELECT COUNT(DISTINCT `{0}`) AS \"{1}\" FROM `{2}`".format("ip", "unq", web.s._SCHEMA_CLICKS))
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
        "short_url": web.s.flask_url.format(slug=row["short"])
    }
    if len(row["long"]) > 30:
        stats["long_clip"] = row["long"][:30] + "..."
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

        :return: a JSON dictionary with submission info.
    """
    response = captcha.submit(
        request.form["recaptcha_challenge_field"],
        request.form["recaptcha_response_field"],
        web.s.captcha_private_key,
        request.remote_addr
    )
    # reCAPTCHA failed
    if not response.is_valid:
        return jsonify({
            "error": "true",
            "message": "The captcha typed was incorrect.",
            "url": "",
            "delete": "",
            "given": request.form["chr_text_long"]
        })

    # URL too long
    if len(request.form["chr_text_long"]) > web.s.soft_url_cap:
        return jsonify({
            "error": "true",
            "message": "The URL you provided was actually <i>too</i> long to shrink!",
            "url": "",
            "delete": "",
            "given": request.form["chr_text_long"]
        })

    # Invalid URL
    if web.s.validate_urls:
        valid = utility.funcs.validate_url(
            url=request.form["chr_text_long"],
            regex=web.s.validate_regex,
            use_requests=web.s.validate_requests,
            fallback=web.s.validate_fallback,
            timeout=5
        )
        if not valid:
            return jsonify({
                "error": "true",
                "message": "The URL provided was unable to be validated.",
                "url": "",
                "delete": "",
                "given": request.form["chr_text_long"]
            })

    # Custom URL validation (slugs)
    custom_slug = False
    if len(request.form["chr_text_short"]) > 0:
        # If this isn't False at the end,
        # we display the error.
        invalid_slug = False
        slug_ = request.form["chr_text_short"]

        if not re.match("^[\w-]+$", slug_):
            invalid_slug = "That custom URL is invalid. Only alphanumeric characters, dashes, underscores, <i>please</i>!"
        elif len(slug_) > web.s._SCHEMA_MAX_SLUG:
            invalid_slug = "That custom URL is too long! Less than 32 characters, <i>please</i>!"
        elif slug_.lower() in reserved_routes:
            invalid_slug = "Sorry, that custom URL is reserved!"
        elif web.slug.exists(web.s._CUSTOM_CHAR + slug_):
            invalid_slug = "Sorry, that custom URL already exists!"

        if invalid_slug:
            return jsonify({
                "error": "true",
                "message": invalid_slug,
                "url": "",
                "delete": "",
                "given": request.form["chr_text_long"]
            })

        custom_slug = web.s._CUSTOM_CHAR + slug_

    # Yippee, it's valid!

    slug_, id_, delete_, url_, old_ = web.slug.url_to_slug(
        request.form["chr_text_long"],
        ip=request.remote_addr,
        slug=custom_slug
    )
    # xxxx -> http://wht.nt/slug/delete/xxxx
    delete_ = web.s.flask_url.format(slug=slug_) + "/delete/" + delete_
    delete_ = delete_ if "chr_check_delete" in request.form \
                and request.form["chr_check_delete"] == "yes" \
                and not old_ \
                else ""

    data = {
        "error": "false",
        "message": "Successfully shrunk your URL!" if not old_ else "URL already shrunk, here it is!",
        "url": web.s.flask_url.format(slug=slug_),
        "delete": delete_,
        "given": url_
    }
    return jsonify(data)