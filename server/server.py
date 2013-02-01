import json
import bottle
from bottle import route, run, request, abort, response
from pymongo import Connection
from bson import json_util


conn = Connection('edward.localserver', 27017)
db = conn['discursos']

def bson2json(bson_file):
    return simplejson.dumps(bson.decode_all(bson_file))

def mime(mime_type):
    def decorator(f):
        def g(*a, **k):
            response.content_type = mime_type
            return f(*a, **k)
        return g
    return decorator

@route('/documents', method='PUT')
def put_document():
	data = request.body.readline()
	if not data:
		abort(400, 'No data received')
	entity = json.loads(data)
	if not entity.has_key('_id'):
		abort(400, 'No _id specified')
	try:
		db['documents'].save(entity)
	except ValidationError as ve:
		abort(400, str(ve))
	
@route('/discursos/:search', method='GET')
def get_discursos(search):
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')
    try:
        search = simplejson.loads(search)
    except:
        search = {}
    entity = db['discursos'].find().limit(15)
    entity = json.dumps(list(entity), default=json_util.default)
    if not entity:
        abort(404, 'No document with id %s' % search)
    return entity

run(host='localhost', port=5000)
