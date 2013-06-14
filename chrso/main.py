# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import abort

app = Flask(__name__)
app.jinja_env.globals.update(recaptcha=lambda: True)
app.debug = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit")
def submit():
    abort(403)
