# -*- coding: utf-8 -*-
import pymongo
from chrso import mongo


mong = pymongo.MongoClient(host=mongo['host'], port=mongo['port'])
db = mong.chrso
