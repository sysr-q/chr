# -*- coding: utf-8 -*-
# chr's flask handler.

# flask stuff
from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify
# recaptcha related
from recaptcha.client import captcha
# requests
import requests
# python modules
import re
# chr modules
import base62
import settings
import logger
import utility

def revision():
	# Change after modification, etc.
	return 'r3'

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
			"url": "",
			"given": request.form['chr_text_long']
		}
		return jsonify(data)
	if settings.validate_urls:
		try:
			logger.debug("Sending HEAD request to:", request.form['chr_text_long'])
			head = requests.head(request.form['chr_text_long'])
			if not head.status_code == 200:
				raise requests.exceptions.HTTPError
		except requests.exceptions.InvalidSchema as e:
			data = {
				"error": "true",
				"message": "The URL provided was not valid.",
				"url": "",
				"given": request.form['chr_text_long']
			}
			return jsonify(data)
		except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
			data = {
				"error": "true",
				"message": "The URL provided was unable to be found.",
				"url": "",
				"given": request.form['chr_text_long']
			}
			return jsonify(data)
		except requests.exception.RequestException as e:
			data = {
				"error": "true",
				"message": "Something went wrong validating your URL.",
				"url": "",
				"given": request.form['chr_text_long']
			}
			return jsonify(data)
	else:
		logger.debug("Matching '{0}' against '{1}'.".format(request.form['chr_text_long'], settings.validate_regex))
		if not re.match(settings.validate_regex, request.form['chr_text_long'], re.I):
			data = {
				"error": "true",
				"message": "The URL provided was not valid.",
				"url": "",
				"given": request.form['chr_text_long']
			}
			return jsonify(data)

	# TODO: create and add the url
	slug = "wut"
	data = {
		"error": "false",
		"message": "Successfully shrunk your URL!",
		"url": settings.flask_url.format(slug=slug),
		"given": request.form['chr_text_long']
	}
	return jsonify(data)

def run():
	app.run(host=settings.flask_host, port=settings.flask_port)

if __name__ == "__main__":
	run()