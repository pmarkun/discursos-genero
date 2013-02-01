from lxml import etree
import urllib2, base64, simplejson, md5
import rtf as rtflib, html2text #Ensure that you have those libs first
import pymongo

def rtf2md(rtfstring):
    tmp_html = rtflib.Rtf2Html.getHtml(rtfstring)
    tmp_markdown = html2text.html2text(tmp_html)
    return tmp_markdown
    
BASE_URL = "http://www.camara.gov.br/sitcamaraws/SessoesReunioes.asmx/"

def getSumarios(dataIni="20/11/2012", dataFim="23/11/2012"):
    args = "ListarDiscursosPlenario?dataIni=" + dataIni + "&dataFim=" + dataFim + "&codigoSessao=&parteNomeParlamentar=&siglaPartido=&siglaUF="
    url = BASE_URL + args
    print url
    xml = urllib2.urlopen(url)
    soup = etree.parse(xml).getroot()
    return soup

def scrapeSumarios(sumarios):
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

tmp_discurso = {
    "codigo_sessao" : "317.2.54.O",
    "orador_numero" : "3",
    "insercao" : "86",
    "quarto" : "1"
    }
    
tmp_discurso['nome'] = "JANETE ROCHA PIETA"

def getIntegra(discurso):
    args = 'obterInteiroTeorDiscursosPlenario?codSessao=' + discurso['codigo_sessao'] + '&numOrador=' + discurso['orador_numero'] + '&numQuarto=' + discurso['quarto'] + '&numInsercao=' + discurso['insercao']
    url = BASE_URL + args
    print url
    xml = urllib2.urlopen(url)
    soup = etree.parse(xml).getroot()
    discurso['integrartf64'] = base64.b64decode(soup.xpath('/sessao/discursoRTFBase64')[0].text)
    discurso['integra'] = rtf2md(discurso['integrartf64'])
    return discurso

def yieldDb(discursos):    
    for discurso in discursos:
        yield discurso
            
def loadDb(discursos, db):
    for discurso in yieldDb(discursos):
        db.discursos.update({"id" : discurso["id"]}, discurso,  True)
        
def rockandroll():
    print "Loading sumarios"
    sumarios = getSumarios("20/11/2012", "23/11/2012")
    print "Converting in discursos"
    discursos = scrapeSumarios(sumarios)
    return discursos

conn = pymongo.Connection("mongodb://edward.localserver")
db = conn['discursos']
