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

def get_shrink_form():
    return ShrinkCaptcha() if "RECAPTCHA_PUBLIC_KEY" in app.config else ShrinkForm()

@app.route("/", methods=["GET", "POST"])
def index():
    form = get_shrink_form()
    url = None
    if form.validate_on_submit():
        # TODO: check for AJAX and jsonify() output
        return "YEAH OK BRAH"
    return render_template("index.html", form=form, url=url)

@app.route("/<url>")
def reroute(url):  # redirect() would clash with flask.redirect
    # TODO: check url.exists(), pull url.from_short(), url.hit(), redirect
    abort(403)
