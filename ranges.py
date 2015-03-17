import falcon
import datetime
import dateutil.parser
import logging
from bson import json_util
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        description = ('Sorry, couldn\'t write your thing to the '
        'database. It worked on my box.')
        raise falcon.HTTPError(falcon.HTTP_725, 'Database Error', description)

class Range(object):
    def __init__(self, db):
      self.db = db
      self.sr = self.db['sr']

    def on_get(self, req, resp):
        if req.params:
            logging.debug('Range query received: %s' % req.params)
            for parametro in req.params:
                valore = req.get_param_as_list(parametro)
                logging.debug('Parameter %s Value %s' % (parametro,valore))
                resp.body = json_util.dumps([r for r in self.sr.find(req.params)])
                resp.status = falcon.HTTP_200
        else:
            resp.body = json_util.dumps([r for r in self.sr.find()])
            resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        logging.debug('Add Range POST request received. Parameters:%s' % req.query_string)
        starts = req.get_param('starts',required=True)
        ends = req.get_param('ends',required=True)
        range_name = req.get_param('name',required=True)
        logging.debug('Range start:%s' % starts)
        logging.debug('Range end:%s' % ends)
        logging.debug('Range name:%s' % range_name)
        #range_item = {u'starts':starts,u'ends':ends,u'name':range_name}
        try:
            range_id = self.sr.insert(req.params)
        except DuplicateKeyError as e:
            logging.critical('DuplicateKey error:%s',json_util.dumps(e.message))
            resp.status = falcon.HTTP_409
            resp.body = json_util.dumps({'errors':True,'description':e.message})
        else:
            logging.debug('Range added successfully with ID %s' % str(range_id))
            resp.body = json_util.dumps(range_id)
            resp.status = falcon.HTTP_201
        return resp.body

    def on_put(self, req, resp,object_id):
        logging.debug('Modify Range PUT request received. Parameters:%s' % req.query_string)
        try:
            r = self.sr.find_one({'_id': ObjectId(object_id)})
        except:
            raise
        else:
            if r:
                starts = req.get_param('starts',required=True)
                ends = req.get_param('ends',required=True)
                range_name = req.get_param('name',required=True)
                logging.debug('Range start:%s' % starts)
                logging.debug('Range end:%s' % ends)
                logging.debug('Range name:%s' % range_name)
                #range_item = {u'starts':starts,u'ends':ends,u'name':range_name}
                try:
                    range_id = self.sr.update({u'_id':ObjectId(object_id)},req.params,upsert=False)
                except DuplicateKeyError as e:
                    logging.critical('DuplicateKey error:%s',json_util.dumps(e.message))
                    resp.status = falcon.HTTP_409
                    resp.body = json_util.dumps({'errors':True,'description':e.message})
                else:
                    logging.debug('Range modified successfully with ID %s' % str(range_id))
                    resp.body = json_util.dumps(range_id)
                    resp.status = falcon.HTTP_200
                    return resp.body
            else:
                resp.status = falcon.HTTP_404
                resp.body = json_util.dumps({'errors':True,'description':'ObjectID not found'})

    def on_delete(self, req, resp,object_id):
        logging.debug('DELETE Range request for id %s received. Parameters:%s' % (object_id,req.query_string))
        r = self.sr.find_one({'_id': ObjectId(object_id)})
        if r:
            result = self.sr.remove({u'_id':ObjectId(object_id)},multi=False)
            resp.body = json_util.dumps(result)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
            resp.body = json_util.dumps({'errors':True,'description':'ObjectID %s not found' % object_id})
