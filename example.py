# -*- coding: utf-8 -*-
from chrso.main import app
app.config.update({
    "SECRET_KEY": "testing_testing_123",
})

# gunicorn -b 127.0.0.1:5000 -p /tmp/chr.pid example:app