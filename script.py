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
    soup = etree.parse(xml).getroot()
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
    try:
        xml = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print discurso
        print "Erro carregando a url:"
        print url
        return None
    soup = etree.parse(xml).getroot()
    discurso['integrartf64'] = base64.b64decode(soup.xpath('/sessao/discursoRTFBase64')[0].text)
    discurso['integra'] = rtf2md(discurso['integrartf64'])
    return discurso
               
def rockandroll(dataIni, dataFim):
    """Rock and roll all night!"""
    sumarios = getSumarios(dataIni, dataFim)
    discursos = scrapeSumarios(sumarios)
    print "Antes " + str(db['discursos'].find().count())
    loadDb(discursos, db, "discursos")
    print "Agora " + str(db['discursos'].find().count())
    
def carregaIntegras(db, collection='discursos'):
    discursos = db[collection].find({ "integra" : { "$exists" : False }})
    discursos_completos = []
    for d in discursos:
        #discursos_completos.append(getIntegra(d))
        item = getIntegra(d)
        if item:
            db.discursos.update({"id" : item["id"]}, item,  True)
    return discursos_completos

conn = pymongo.Connection(MONGODB_SERVER)
db = conn['discursos']
print "Hello!"
