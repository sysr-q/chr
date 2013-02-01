""" **chr** (coded under the name ``chru``) is a Python based URL shortening
    service which uses Flask as a front end, and pysqlw as the SQL
    backend, to interface with sqlite3.

    It can shrink billions of unique URLs with less than 6 characters,
    run in the background with no human interaction,
    and it can fly like a bird -- or is that Super Man?
"""
from .version import __version__, __supported__