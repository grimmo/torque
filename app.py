#!/usr/bin/env python
import falcon
import ranges
import shifts
import logging
from pymongo import MongoClient
from wsgiref import simple_server

# falcon.API instances are callable WSGI apps
wsgi_app = api = falcon.API()

client = MongoClient('localhost',27017,safe=True)
db = client.dbturni

ranges = ranges.Range(db)
workshifts = shifts.WorkShift(db)

api.add_route('/ranges', ranges)
api.add_route('/add/range/',ranges)
api.add_route('/mod/range/{object_id}/',ranges)
api.add_route('/del/range/{object_id}/',ranges)
api.add_route('/shifts', workshifts)
api.add_route('/add/shift/',workshifts)
api.add_route('/mod/shift/{object_id}/',workshifts)
api.add_route('/del/shift/{object_id}/',workshifts)


if __name__ == '__main__':
    logging.basicConfig(filename='app.log',level=logging.DEBUG)
    httpd = simple_server.make_server('127.0.0.1', 8000, wsgi_app)
    httpd.serve_forever()
