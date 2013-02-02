import json
import bottle
from bottle import route, run, request, abort, response
from pymongo import Connection
from bson import json_util

SETTINGS = {}
SETTINGS['MONGODB_SERVER'] = 'edward.localserver'
SETTINGS['MONGODB_PORT'] = 27017
SETTINGS['MONGODB_DB'] = 'discursos'



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
	
@route('/discursos/q/<query>/<projection>', method='GET')
def get_discursos(query, projection={}):
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')
    try:
        query = json.loads(query)
        projection = json.loads(projection)
    except:
        query = {}
        projection = {}
    entity = db['discursos'].find(query).limit(50)
    entity = json.dumps(list(entity), default=json_util.default)
    if not entity:
        abort(404, 'No document with id %s' % query)
    return entity

@route('/discursos/aggregate/<word>', method='GET')
def aggregate_discursos(word):
    response.set_header('Content-Type', 'application/json')
    response.set_header('Access-Control-Allow-Origin', '*')
    entity = db['discursos'].find({ "keywords" : word}, { "integra" : 1, "orador_nome" : 1, "orador_uf" : 1, "orador_partido" : 1 })
    discursos = {}
    for d in entity:
	discurso_stripped = ''
	for line in d['integra'].split('\n'):
	    try:
		line.index(word)
		discurso_stripped = discurso_stripped + line + "\n"
	    except:
		pass
	deputado = d['orador_nome']+d['orador_partido']+d['orador_uf']
	if discursos.has_key(deputado):
	    discursos[deputado]['discursos'].append(discurso_stripped)
	else:
	    discursos[deputado] = {}
	    discursos[deputado]['orador_nome'] = d['orador_nome']
	    discursos[deputado]['orador_uf'] = d['orador_uf']
	    discursos[deputado]['orador_partido'] = d['orador_partido']
	    discursos[deputado]['discursos'] = [discurso_stripped]
    
    resposta = []
    for d in discursos:
	tmp = discursos[d]
	tmp["id"] = d
	resposta.append(tmp)
    resposta = json.dumps(resposta, default=json_util.default)
    if not entity:
        abort(404, 'No document with id %s' % query)
    return resposta

run(host='localhost', port=5000)
