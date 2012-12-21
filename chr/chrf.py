# -*- coding: utf-8 -*-
# chr's flask handler.

from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

from recaptcha.client import captcha

import base62
import settings
import logger
import utility

def revision():
	# Change after modification, etc.
	return 'r2'

app = Flask(__name__)
app.debug = settings.flask_debug
app.secret_key = settings.flask_secret_key

@app.route("/")
def index():
	return render_template('index.html', recaptcha_key=settings.captcha_public_key)

@app.route("/submit", methods=["POST"])
def submit():
	response = captcha.submit(
		request.form['recaptcha_challenge_field'],
		request.form['recaptcha_response_field'],
		settings.captcha_private_key,
		request.remote_addr
	)
	if not response.is_valid:
		data = {
			"error": "true",
			"message": "The captcha typed was incorrect.",
			"url": ""
		}
		return jsonify(data)
	else:
		# TODO: create and add the url
		data = {
			"error": "false",
			"message": "Successfully shrunk your URL!",
			"url": "http://something/wut"
		}
		return jsonify(data)

def run():
	app.run(host=settings.flask_host, port=settings.flask_port)

if __name__ == "__main__":
	run()