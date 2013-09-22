# -*- coding: utf-8 -*-
import collections
from datetime import datetime
import time

from flask import (Flask, render_template, abort, redirect, url_for, flash,
                   request)
from flask.ext.wtf import Form, validators, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField)
from werkzeug.useragents import UserAgent

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
    # I honestly do not know whats going on here, it was just in the old
    # chr stats template. The old __doc__ was: 
    #   Strips the day out of a date.. I think.
    "date_strip_day": lambda date_: date_.split("/")[1],
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

@app.route("/<short>/stats")
def stats(short):
    if not url.exists(short):
        return redirect(url_for("index"))
    long_ = url.long(short)
    hits = url.hits(short)
    hits_len = len(hits)
    hits_unique = collections.Counter(hit["ip"] for hit in hits)
    hits_unique_len = len(hits_unique)
    stats = {
        "short": url_for("reroute", short=short, _external=True),
        "long": long_,
        "long_clip": "{0}{1}".format(long_[:35], "..." if len(long_) > 35 else ""),
        "hits": {
            "unique": hits_unique_len,
            "return": (hits_len - hits_unique_len) if hits_len > 0 else 0,
            # (unique / all)% of visitors only come once
            "ratio": str(round(float(hits_unique_len) / float(hits_len), 2))[2:],
            "all": hits_len,
        },
        "clicks": {
            "platforms": collections.Counter(
                UserAgent(hit["useragent"]).platform.capitalize() or "Unknown" for hit in hits
            ),
            "browsers": collections.Counter(
                UserAgent(hit["useragent"]).browser.capitalize() or "Unknown" for hit in hits
            ),
            "pd": {}  # TODO: render per day click counts and stuff
        },
    }
    # Warning: garbage code
    month_ago = month_ago_ext = int(time.time()) - (60 * 60 * 24 * 30)
    for _ in xrange(1, 31):
        month_ago_ext += (60 * 60 * 24)
        day_strf = str(datetime.fromtimestamp(month_ago_ext).strftime("%m/%d"))
        stats["clicks"]["pd"][day_strf] = 0
    for hit in hits:
        if hit["time"] < month_ago:
            # Click more than a month old, not interested.
            continue
        day_strf = str(datetime.fromtimestamp(hit["time"]).strftime("%m/%d"))
        stats["clicks"]["pd"][day_strf] += 1
    return render_template("stats.html", stats=stats)

@app.route("/<short>/delete/<key>")
def delete(short, key):
    if not url.exists(short):
        return redirect(url_for("index"))
    if not key == url.delete_key(short):
        return redirect(url_for("index"))
    url.remove(short)
    flash("Successfully deleted {0}!".format(url_for("reroute", short=short, _external=True)), "success")
    return redirect(url_for("index"))
