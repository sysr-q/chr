# -*- coding: utf-8 -*-
# chr's flask handler.

from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify

from pysql_wrapper import pysql_wrapper
import base62
import settings
import logger

def revision():
	# Change after modification, etc.
	return 'r1'

app = Flask(__name__)
app.debug = settings.flask_debug
app.secret_key = settings.flask_secret_key

@app.route("/")
def index():
	return 'I AM A MAN, NOT AN INDEX!'

def hash_pass(username, password, salt=settings.salt_password):
	import hashlib
	# This is so they can log in as Foo, FOO or fOo.
	username = username.lower()
	return hashlib.sha256(salt + password + username + salt).hexdigest()

def sql():
	"""Reuse this every time you need to do SQL stuff.
		sql().where('id', 1).get('table')
	"""
	return pysql_wrapper(db_type='sqlite', db_path=settings.sql_path)

def run():
	app.run(host=settings.flask_host, port=settings.flask_port)

if __name__ == "__main__":
	run()