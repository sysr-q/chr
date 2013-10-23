# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import collections
import calendar
import random
import urllib
import time

from flask import (Flask, render_template, abort, redirect, url_for, flash,
                   request, jsonify)
from flask.ext.wtf import Form, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField, validators)
from werkzeug.useragents import UserAgent, UserAgentParser
# Monkey patch in an xbot++ recogniser
UserAgentParser.browsers = tuple([(r"xbot\+\+", "xbot++")] + list(UserAgentParser.browsers))
UserAgentParser.platforms = tuple([(r"xbot\+\+", "hpux")] + list(UserAgentParser.platforms))
UserAgent._parser = UserAgentParser()

from chrso import url


class ShrinkForm(Form):
    url = TextField(validators=[validators.URL()])
    custom = TextField(validators=[validators.Length(max=16)])
    burn = BooleanField()
    statistics = BooleanField()
class ShrinkCaptcha(ShrinkForm):
    captcha = RecaptchaField()

app = Flask(__name__)
app.jinja_env.globals.update({
    "chr_header": lambda: app.config.get("CHR_HEADER", "chr"),
    "chr_sub_header": lambda: app.config.get("CHR_SUB_HEADER", "simple url shortening"),
    "sorted": sorted,
    "len": len,
    # The old __doc__ was: ``Strips the day out of a date.. I think.``
    "date_strip_day": lambda date_: date_.split("/")[1],
})

# This stops nasty bugs if there's unicode in the URLs and stuff.
app.jinja_env.filters.update({
    "unquote": lambda s: urllib.unquote(s).decode("utf8"),
})

def get_shrink_form():
    return ShrinkCaptcha() if "RECAPTCHA_PUBLIC_KEY" in app.config else ShrinkForm()

@app.route("/", methods=["GET", "POST"])
def index():
    form = get_shrink_form()
    surl = None
    render = lambda: render_template("index.html", form=form, url=surl)
    if form.validate_on_submit():
        if form.custom.data and url.exists(form.custom.data):
            flash("Sorry, that custom URL already exists.", "error")
            return render()
        url_ = url.add(
            form.url.data,
            statistics=form.statistics.data,
            burn=form.burn.data,
            short=form.custom.data if form.custom.data else None,
            ua=request.user_agent.string,
            ip=request.remote_addr
        )
        if url_:
            flash("Successfully shrunk your URL!", "success")
            surl = {
                "long": form.url.data,
                "short": url_for("reroute", short=url_[0], _external=True),
                "stats": url_for("stats", short=url_[0], _external=True),
                "delete": url_for("delete", short=url_[0], key=url_[1], _external=True),
                "burn": form.burn.data,
            }
            form.url.data = form.custom.data = ""
            form.statistics.data = True
            form.burn.data = False
    return render()

@app.route("/<short>")
def reroute(short):  # redirect() would clash with flask.redirect
    if not url.exists(short):
        return redirect(url_for("index"))
    long_ = url.long(short)
    url.hit(short, ua=request.user_agent.string, ip=request.remote_addr)
    return redirect(long_)

def get_stats(short, clip=35):
    # Make sure "short" exists by now or you're goners.
    long_ = url.long(short)
    hits = url.hits(short)
    hits_len = len(hits)
    hits_unique = collections.Counter(hit["ip"] for hit in hits)
    hits_unique_len = len(hits_unique)
    def platform(h):
        ua = UserAgent(h["useragent"])
        if ua.platform is None:
            return "Unknown"
        return ua.platform.capitalize()
    def browser(h):
        ua = UserAgent(h["useragent"])
        if ua.browser is None:
            return "Unknown"
        return ua.browser.capitalize()
    stats = {
        "error": False,
        "message": "",
        "short": url_for("reroute", short=short, _external=True),
        "long": long_,
        "long_clip": "{0}{1}".format(long_[:clip], "..." if len(long_) > clip else ""),
        "hits": {
            "unique": hits_unique_len,
            "return": (hits_len - hits_unique_len) if hits_len > 0 else 0,
            # (unique / all)% of visitors only come once
            "ratio": (str(round(float(hits_unique_len) / float(hits_len), 2))[2:]) if hits_len > 0 else None,
            "all": hits_len,
        },
        "clicks": {
            "platforms": collections.Counter(map(platform, hits)),
            "browsers": collections.Counter(map(browser, hits)),
            "pd": {}  # This is generated below..
        },
    }
    x = datetime.now() - timedelta(days=30)
    month = calendar.timegm(x.timetuple())
    for _ in xrange(1, 31):
        # This has to go first or else you get KeyErrors later.
        x += timedelta(days=1)
        stats["clicks"]["pd"][x.strftime("%m/%d")] = 0
    print stats["clicks"]["pd"]
    for hit in hits:
        if hit["time"] < month: # if it's more than a month old we don't care
            continue
        stats["clicks"]["pd"][datetime.fromtimestamp(hit["time"]).strftime("%m/%d")] += 1
    return stats

@app.route("/<short>/stats")
def stats(short):
    if not url.exists(short):
        return redirect(url_for("index"))
    stats_ = get_stats(short)
    return render_template("stats.html", stats=stats_)

@app.route("/<short>/stats.json")
def stats_json(short):
    if not url.exists(short):
        return jsonify({"error": True, "message": "That shortened URL doesn't exist!"})
    stats_ = get_stats(short)
    return jsonify(stats_)

@app.route("/<short>/delete/<key>")
def delete(short, key):
    if not url.exists(short):
        return redirect(url_for("index"))
    if not key == url.delete_key(short):
        return redirect(url_for("index"))
    url.remove(short)
    flash("Successfully deleted {0}!".format(url_for("reroute", short=short, _external=True)), "success")
    return redirect(url_for("index"))
