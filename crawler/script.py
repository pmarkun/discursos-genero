from settings import *
from tools import *
from lxml import etree
import urllib2, base64, simplejson, md5

def getSumarios(dataIni="20/11/2012", dataFim="23/11/2012"):
    """Acessa o XML para um intervalo de datas especifico (formato dd/mm/yyyy) usando o webservice da Camara."""
    args = "ListarDiscursosPlenario?dataIni=" + dataIni + "&dataFim=" + dataFim + "&codigoSessao=&parteNomeParlamentar=&siglaPartido=&siglaUF="
    url = BASE_URL + args
    print url
    xml = urllib2.urlopen(url)
    xml_file = open('rawdata/discursoscamara_'+dataIni.replace("/","-")+"_"+dataFim.replace("/","-")+".xml", 'w')
    xml_file.write(xml.read())
    xml_file.close()
    xml_read = open('rawdata/discursoscamara_'+dataIni.replace("/","-")+"_"+dataFim.replace("/","-")+".xml", 'r')
    soup = etree.parse(xml_read).getroot()
    xml_read.close()
    return soup

def scrapeSumarios(sumarios):
    """Extrai os discursos do XMLs dos sumarios e retorna uma array com dicionarios."""
    discursos_dict = {}
    for s in sumarios.xpath('/sessoesDiscursos/sessao/fasesSessao/faseSessao/discursos/discurso'):
        discurso = {}
        discurso['codigo_sessao'] = s.xpath('../../../../codigo')[0].text.strip()
        discurso['data_sessao'] = s.xpath('../../../../data')[0].text.strip()
        discurso['numero_sessao'] = s.xpath('../../../../numero')[0].text.strip()
        discurso['tipo_sessao'] = s.xpath('../../../../tipo')[0].text.strip()
        
        discurso['fase_codigo'] = s.xpath('../../codigo')[0].text.strip()
        discurso['fase_descricao'] = s.xpath('../../descricao')[0].text.strip()
        
        discurso['orador_nome'] = s.xpath('./orador/nome')[0].text.strip()
        discurso['orador_numero'] = s.xpath('./orador/numero')[0].text.strip()
        discurso['orador_partido'] = s.xpath('./orador/partido')[0].text.strip()
        discurso['orador_uf'] = s.xpath('./orador/uf')[0].text.strip()
        discurso['hora_inicio'] = s.xpath('./horaInicioDiscurso')[0].text.strip()
        discurso['quarto'] = s.xpath('./numeroQuarto')[0].text.strip()
        discurso['insercao'] = s.xpath('./numeroInsercao')[0].text.strip()
        discurso['sumario'] = s.xpath('./sumario')[0].text.strip()
        discurso['id'] = md5.new(simplejson.dumps(discurso)).hexdigest()
        discursos_dict[discurso['id']] = discurso
    
    discursos = []
    for d in discursos_dict:
        discursos.append(discursos_dict[d])
    return discursos

def getIntegra(discurso):
    """Extrai a integra do discurso usando o webservice da Camara"""
    args = 'obterInteiroTeorDiscursosPlenario?codSessao=' + discurso['codigo_sessao'] + '&numOrador=' + discurso['orador_numero'] + '&numQuarto=' + discurso['quarto'] + '&numInsercao=' + discurso['insercao']
    url = BASE_URL + args
    xml = None;
    try:
        xml = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print discurso
        print "Erro carregando a url:"
        print url
        return None
    if (xml):
        soup = etree.parse(xml).getroot()
        discurso['integrartf64'] = base64.b64decode(soup.xpath('/sessao/discursoRTFBase64')[0].text)
        try:
            discurso['integra'] = rtf2md(discurso['integrartf64'])
            return discurso
        except:
            print discurso
            print url
            return None
    else:
        return None
               
def rockandroll(dataIni, dataFim):
    """Rock and roll all night!"""
    sumarios = getSumarios(dataIni, dataFim)
    discursos = scrapeSumarios(sumarios)
    print "Antes " + str(db['discursos'].find().count())
    loadDb(discursos, db, "discursos")
    print "Agora " + str(db['discursos'].find().count())
    
def carregaIntegras(db, collection='discursos'):
    discursos = db[collection].find({ "integra" : { "$exists" : False }})
    i = 0
    for d in discursos:
        i = i + 1
        item = getIntegra(d)
        if item:
            db.discursos.update({"id" : item["id"]}, item,  True)
        if i == 1000:
            print "Loading 1000 more..."
            i = 0

def missingIntegras(db, collection="discursos"):
    return db[collection].find({ "integra" : { "$exists" : False }})
    
def addKeyword(word, db, collection='discursos'):
    regex_word = "(?i).*"+word+".*"
    discursos = db[collection].find({ "integra" : { "$regex" : regex_word }})
    for d in discursos:
        if d.has_key("keywords"):
            try:
                #lame way
                d["keywords"].index(word)
            except:
                d["keywords"].append(word)
        else:
            d["keywords"] = [word]
        db[collection].update({"id" : d["id"]}, d,  True)
    return db[collection].find({"keywords" : word})

def findKeyword(word, db, collection='discursos'):
    return db[collection].find({"keywords" : word})
    
def removeKeyword(word, db, collection='discursos'):
    discursos = db[collection].find({"keywords" : word})
    for d in discursos:
        d['keywords'].remove(word)
        db[collection].update({"id" : d["id"]}, d,  True)
    return discursos

conn = pymongo.Connection(MONGODB_SERVER)
db = conn['discursos']
print "Hello!"
