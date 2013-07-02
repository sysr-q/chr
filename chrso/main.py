# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import abort

from flask.ext.wtf import Form, validators
from wtforms import (TextField, PasswordField, IntegerField,
                     BooleanField)

from chrso import url


class SubmitForm(Form):
    url = TextField(url)

app = Flask(__name__)
app.debug = True

app.config.update({
    "RECAPTCHA_PUBLIC": False,
    "RECAPTCHA_PRIVATE": False,
})
app.jinja_env.globals.update({
    "recaptcha": lambda: app.config['RECAPTCHA_PUBLIC'],
})


@app.route("/")
def index():
    form = SubmitForm()
    return render_template("index.html", form=form)


@app.route("/tos")
def tos():
    return render_template("tos.html")


@app.route("/submit", methods=["POST"])
def submit():
    abort(403)
