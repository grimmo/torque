import falcon
import datetime
import dateutil.parser
import logging
from bson import json_util
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId
from bson.objectid import ObjectId

class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        description = ('Sorry, couldn\'t write your thing to the '
        'database. It worked on my box.')
        raise falcon.HTTPError(falcon.HTTP_725, 'Database Error', description)

class WorkShift(object):
    def __init__(self, db):
      self.db = db
      self.ws = self.db['workshift']
      self.sr = self.db['sr']

    def on_get(self, req, resp):
        if req.params:
            logging.debug('Workshift query received: %s' % req.params)
            for parameter in req.params:
                valore = req.get_param_as_list(parameter)
                logging.debug('Parameter %s Value %s' % (parameter,valore))
                #raw_date = req.get_param('date')
                #new_params = dict.copy(req.params)
                #if raw_date:
                #    new_params['date'] = datetime.datetime.strptime(raw_date,'%d-%m-%Y')
                #resp.body = json_util.dumps([workshift for workshift in self.ws.find(new_params)])
                resp.body = json_util.dumps([workshift for workshift in self.ws.find(req.params)])
                resp.status = falcon.HTTP_200
        else:
            resp.body = json_util.dumps([workshift for workshift in self.ws.find()])
            resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        logging.debug('Add WorkShift POST request received. Parameters:%s' % req.query_string)
        raw_date = req.get_param('date',required=True)
        range_id = req.get_param('range_id',required=True)
        logging.debug('workshift raw date:%s' % raw_date)
        true_range_id = None
        try:
            true_range_id = self.sr.find_one({u'_id':ObjectId(range_id)})
            logging.debug('Range id: %s' % true_range_id)
        except InvalidId:
            resp.status = falcon.HTTP_400
            resp.body = json_util.dumps({'errors':True,'description':'Invalid range ID'})
        if not true_range_id:
            resp.status = falcon.HTTP_400
            resp.body = json_util.dumps({'errors':True,'description':'Invalid range ID'})
            return
        try:
            date = datetime.datetime.strptime(raw_date,'%d-%m-%Y')
        except:
            resp.status = falcon.HTTP_400
            resp.body = json_util.dumps({'errors':True,'description':'Date must me in DD-MM-YYYY format.'})
        #logging.debug('Request parameters before modification: %s' % req.params)
        #new_params = dict.copy(req.params)
        #new_params['range_id'] = range_id
        #logging.debug('Request parameters after modification: %s' % new_params)
        #logging.debug('range id:%s' % range_id)
        #range_item = {u'starts':starts,u'ends':ends,u'name':range_name}
        try:
            workshift_id = self.ws.insert(req.params)
        except DuplicateKeyError as e:
            logging.critical('DuplicateKey error:%s',json_util.dumps(e.message))
            resp.status = falcon.HTTP_409
            resp.body = json_util.dumps({'errors':True,'description':e.message})
        else:
            logging.debug('WorkShift added successfully with ID %s' % str(workshift_id))
            resp.body = json_util.dumps(workshift_id)
            resp.status = falcon.HTTP_201
        return resp.body

    def on_put(self, req, resp,object_id):
        logging.debug('Modify WorkShift PUT request received. Parameters:%s' % req.query_string)
        try:
            ws = self.ws.find_one({'_id': ObjectId(object_id)})
        except:
            raise
        else:
            if ws:
                date = req.get_param('date',required=True)
                range_id = req.get_param('range_id',required=True)
                range_name = req.get_param('name',required=True)
                logging.debug('WorkShift date:%s' % starts)
                logging.debug('Range ID:%s' % range_id)
                #range_item = {u'starts':starts,u'ends':ends,u'name':range_name}
                try:
                    workshift_id = self.ws.update({u'_id':ObjectId(object_id)},req.params,upsert=False)
                except DuplicateKeyError as e:
                    logging.critical('DuplicateKey error:%s',json_util.dumps(e.message))
                    resp.status = falcon.HTTP_409
                    resp.body = json_util.dumps({'errors':True,'description':e.message})
                else:
                    logging.debug('Range modified successfully with ID %s' % str(workshift_id))
                    resp.body = json_util.dumps(workshift_id)
                    resp.status = falcon.HTTP_200
                    return resp.body
            else:
                resp.status = falcon.HTTP_404
                resp.body = json_util.dumps({'errors':True,'description':'ObjectID not found'})

    def on_delete(self, req, resp,object_id):
        logging.debug('DELETE WorkShift request for id %s received. Parameters:%s' % (object_id,req.query_string))
        ws = self.ws.find_one({'_id': ObjectId(object_id)})
        if ws:
            result = self.ws.remove({u'_id':ObjectId(object_id)},multi=False)
            resp.body = json_util.dumps(result)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404
            resp.body = json_util.dumps({'errors':True,'description':'ObjectID %s not found' % object_id})
