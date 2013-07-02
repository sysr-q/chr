# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import abort

from flask.ext.wtf import Form, validators, RecaptchaField
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField)

from chrso import url


class ShrinkForm(Form):
    url = TextField()
    custom = TextField()
    burn = BooleanField()
    statistics = BooleanField()
    captcha = RecaptchaField()

app = Flask(__name__)
app.debug = True

app.config.update({
    "RECAPTCHA_PUBLIC_KEY": False,
    "RECAPTCHA_PRIVATE_KEY": False,
})
app.jinja_env.globals.update({
    "recaptcha": lambda: app.config['RECAPTCHA_PUBLIC_KEY'],
})


@app.route("/")
def index():
    form = ShrinkForm()
    return render_template("index.html", form=form)


@app.route("/tos")
def tos():
    return render_template("tos.html")


@app.route("/submit", methods=["POST"])
def submit():
    abort(403)
