# -*- coding: utf-8 -*-
import urllib

from flask import (Flask, render_template, abort, redirect, url_for, flash,
                   request, jsonify)
from flask.ext.wtf import Form, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField, validators)

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

@app.route("/<short>/stats")
def stats(short):
    if not url.exists(short):
        return redirect(url_for("index"))
    if not url.has_stats(short):
        return redirect(url_for("index"))
    return render_template("stats.html", stats=url.stats(short))

@app.route("/<short>/stats.json")
def stats_json(short):
    return jsonify(url.stats(short))

@app.route("/<short>/delete/<key>")
def delete(short, key):
    if not url.exists(short):
        return redirect(url_for("index"))
    if key != url.delete_key(short):
        return redirect(url_for("index"))
    url.remove(short)
    flash("Successfully deleted {0}!".format(url_for("reroute", short=short, _external=True)), "success")
    return redirect(url_for("index"))
