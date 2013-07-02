# -*- coding: utf-8 -*-
import chrso
chrso.mongo["host"] = None # host & port go here
chrso.mongo["port"] = None # None/None make pymongo use defaults

from chrso.main import app
app.config.update({
    "SECRET_KEY": "testing_testing_123",
})

# gunicorn -b 127.0.0.1:5000 -p /tmp/chr.pid example:app