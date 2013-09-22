# -*- coding: utf-8 -*-
from flask import (Flask, render_template, abort, redirect, url_for, flash,
                   request)

from flask.ext.wtf import Form, validators, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField)

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
        url_ = url.add(form.url.data,
                   statistics=form.statistics.data,
                   burn=form.burn.data,
                   short=form.custom.data if form.custom.data else None,
                   ua=request.user_agent.string,
                   ip=request.remote_addr)
        if url_:
            flash("Successfully shrunk your URL!", "success")
            surl = {
                "long": form.url.data,
                "short": url_for("reroute", short=url_[0], _external=True),
                "stats": url_for("stats", short=url_[0], _external=True),
                "delete": url_for("delete", short=url_[0], key=url_[1], _external=True),
                "burn": form.burn.data,
            }
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
    # TODO: check url.exists(), pull all url hits, render some pretty graphs
    abort(403)

@app.route("/<short>/delete/<key>")
def delete(short, key):
    if not url.exists(short):
        return redirect(url_for("index"))
    if not key == url.delete_key(short):
        return redirect(url_for("index"))
    url.remove(short)
    flash("Successfully deleted {0}!".format(url_for("reroute", short=short, _external=True)), "success")
    return redirect(url_for("index"))
