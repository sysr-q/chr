# -*- coding: utf-8 -*-
# Settings file for chr url shortener.

debug = False

flask_debug = debug
flask_host = '127.0.0.1'
flask_port = 8080
flask_secret_key = 'SOMETHING!SECRET@AND#HARD$TO%GUESS'

salt_password = 'SOMETHING!UNIQUE@AND#HARD$TO%GUESS^OR&ELSE'

# Absolute directory for logging.
log_dir = '/path/to/logs'

# This has to be absolute or sqlite will complain.
sql_path = '/path/to/chr.db'

# API stuff, for when we finish this.
api_enabled = False

#--------------------------#
# Constants (do not touch) #
#--------------------------#

# _SCHEMA_* are the table names.
# This allows simple changement of table names without changing 500 classes.
_SCHEMA_USERS = 'users'
_SCHEMA_REDIRECTS = 'redirects'
_SCHEMA_CLICKS = 'clicks'