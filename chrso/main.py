# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import abort  # flask isn't pro-life?

from chrso import url

app = Flask(__name__)
app.config.update({
    "RECAPTCHA_PUBLIC": False,
    "RECAPTCHA_PRIVATE": False,
})
app.jinja_env.globals.update({
    "recaptcha": lambda: app.config['RECAPTCHA_PUBLIC'],
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tos")
def tos():
    return render_template("tos.html")

@app.route("/submit", methods=["POST"])
def submit():
    abort(403)
