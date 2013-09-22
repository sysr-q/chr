# -*- coding: utf-8 -*-
from flask import (Flask, render_template, abort)

from flask.ext.wtf import Form, validators, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField)

from chrso import url


class ShrinkForm(Form):
    url = TextField()
    custom = TextField()
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
    if form.validate_on_submit():
        # TODO: check not url.exists(), then url.add(...), etc
        return "YEAH OK BRAH"
    return render_template("index.html", form=form, url=surl)

@app.route("/<short>")
def reroute(short):  # redirect() would clash with flask.redirect
    # TODO: check url.exists(), pull url.from_short(), url.hit(), redirect
    if not url.exists(short):
        return redirect

@app.route("/<short>/stats")
def stats(short):
    # TODO: check url.exists(), pull all url hits, render some pretty graphs
    abort(403)
