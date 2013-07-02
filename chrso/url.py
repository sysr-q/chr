# -*- coding: utf-8 -*-
import pymongo
from chrso import mongo


mong = pymongo.MongoClient(host=mongo['host'], port=mongo['port'])
db = mong.chrso

def add(long, statistics, burn, short=None, ip=None, ptime=None):
    """ Shorten a long URL and add it to our database.

        :param long: the long URL we're wishing to shorten
        :param statistics: should we bother enabling statistics
            for the shortened URL?
        :param burn: should this be a "burn after reading" URL?
        :param short: an optional custom URL
        :param ip: the IP address the URL was shortened by
        :param ptime: the time of the shorten (time.time() is
            used if omitted)
    """
    pass
