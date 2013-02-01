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
    for s in sumarios.xpath('/sessoesDiscursos/sessao'):
        discurso = {}
        discurso['codigo_sessao'] = s.xpath('./codigo')[0].text.strip()
        discurso['data_sessao'] = s.xpath('./data')[0].text.strip()
        discurso['numero_sessao'] = s.xpath('./numero')[0].text.strip()
        discurso['tipo_sessao'] = s.xpath('./tipo')[0].text.strip()
        for f in s.xpath('./fasesSessao/faseSessao'):
            discurso['fase_codigo'] = f.xpath('./codigo')[0].text.strip()
            discurso['fase_descricao'] = f.xpath('./descricao')[0].text.strip()
            for d in f.xpath('./discursos/discurso'):
                discurso['orador_nome'] = d.xpath('./orador/nome')[0].text.strip()
                discurso['orador_numero'] = d.xpath('./orador/numero')[0].text.strip()
                discurso['orador_partido'] = d.xpath('./orador/partido')[0].text.strip()
                discurso['orador_uf'] = d.xpath('./orador/uf')[0].text.strip()
                discurso['hora_inicio'] = d.xpath('./horaInicioDiscurso')[0].text.strip()
                discurso['quarto'] = d.xpath('./numeroQuarto')[0].text.strip()
                discurso['insercao'] = d.xpath('./numeroInsercao')[0].text.strip()
                discurso['sumario'] = d.xpath('./sumario')[0].text.strip()
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
    print url
    xml = urllib2.urlopen(url)
    soup = etree.parse(xml).getroot()
    discurso['integrartf64'] = base64.b64decode(soup.xpath('/sessao/discursoRTFBase64')[0].text)
    discurso['integra'] = rtf2md(discurso['integrartf64'])
    return discurso
       
def rockandroll():
    """Rock and roll all night!"""
    conn = pymongo.Connection(MONGODB_SERVER)
    db = conn['discursos']
