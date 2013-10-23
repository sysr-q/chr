# -*- coding: utf-8 -*-
from functools import wraps
import urllib
import re

from flask import (Flask, render_template, abort, redirect, url_for,
                   flash as _flash, request, jsonify, g, Response, make_response)
from flask.ext.wtf import Form, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField, validators)

# Above url import for circ. deps.
def flash(message, type_=None):
    """ Replacement to Flask's flash() for "magic" functionality in chr.
        If you want to use the real flash, use _flash() or flask.flash itself.

        flash("SOMETHING", "error") if things go wrong
        flash("SOMETHING", "success") if things go right
    """
    f = (message, type_)
    g.flashes.append(f)

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

@app.before_request
def before_request():
    g.is_api_req = bool(re.findall(r"\.json$", request.path))
    g.flashes = []

@app.after_request
def after_request(res):
    if not g.is_api_req:
        # Flash all our flashes
        map(lambda f: _flash(*f), g.flashes)
    if not hasattr(res, "_ret_dict") or res._ret_dict is None:
        # Too specific for us, let's not screw around.
        return res
    res = res._ret_dict
    errors = filter(lambda f: len(f) >= 2 and f[1] == "error", g.flashes)
    if g.is_api_req:
        res["error"] = bool(errors)
        # Backwards compat.. Sort of?
        res.setdefault("message", "Check `messages` instead, buddy.")
        res["messages"] = map(lambda f: f[0], g.flashes)
        # Not interesting to API consumers.
        res.pop("_template", None)
        return jsonify(res)
    return make_response(render_template(res["_template"], res=res))

def responsify(f):
    # TODO: document this magic
    @wraps(f)
    def decorated(*args, **kwargs):
        ret = f(*args, **kwargs)
        if isinstance(ret, Response):
            ret._ret_dict = None
            return ret
        res = Response(ret)
        res._ret_dict = None
        if isinstance(ret, dict):
            res._ret_dict = ret
        return res
    return decorated

@app.route("/", methods=["GET", "POST"])
def index():
    form = get_shrink_form()
    surl = None
    render = lambda: render_template("index.html", form=form, url=surl)
    if form.validate_on_submit():
        if form.custom.data and url.exists(form.custom.data):
            _flash("Sorry, that custom URL already exists.", "error")
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
            _flash("Successfully shrunk your URL!", "success")
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

@app.route("/<short>/stats.json")
@app.route("/<short>/stats")
@responsify
def stats(short):
    stats_ = url.stats(short)
    stats_["_template"] = "stats.html"
    if not g.is_api_req and stats_["error"]:
        return redirect(url_for("index"))
    return stats_

@app.route("/<short>/delete/<key>.json")
@app.route("/<short>/delete/<key>")
@responsify
def delete(short, key):
    empty_or_redir = lambda: {} if g.is_api_req else redirect(url_for("index"))
    if not url.exists(short) or key != url.delete_key(short):
        flash("URL doesn't exist or deletion key is incorrect.", "error")
        return empty_or_redir()
    if not url.remove(short):
        flash("Something dun goofed! Sorry.", "error")
        return empty_or_redir()
    flash("Successfully deleted {0}!".format(url_for("reroute", short=short, _external=True)), "success")
    return empty_or_redir()
