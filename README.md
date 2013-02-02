# Gênero do Discurso

Esse aplicativo visualiza o uso da palavra `mulher` nos discursos realizados na Câmara Federal entre 2010 e 2012 (o atual mandato).

## Instalação

O Gênero do Discurso é um aplicativo desenvolvido em HTML5 e Javascript consumindo JSONs de banco MongoDB através de um servidor em Python (que provê a interface RESt).

Depêndencias crawler (python 2.7):
* lxml
* [rdf](http://code.google.com/p/html2fb/source/browse/trunk/rtf/?)
* html2text

Depêndencias server (python 2.7):
* bottle
* pymongo

Depêndencias client (javascript/css):
* jquery
* raphaeljs
* [wordtree](https://github.com/silverasm/wordtree)
* bootstrap

(as dependencias de javascript estão incluidas na pasta `vendor`)

## Configuração

**Crawler**
O crawer `script.py` captura e converte os discursos parlamentares e envia para um banco de dados MongoDB.

Para usar, acesse o terminal do Python e execute:

    run script.py
    rockndroll("dd/mm/yyyy","dd/mm/yyyy")

Isso vai extrair a lista de discurso com seus respectivos sumários.
Para obter a integra dos discursos e atualizar o banco:

    carregaDiscursos(db)

O sistema vai buscar as entradas no banco que não tem integra ainda e vai acessar o webservice da Câmara para preencher.
A Câmara armazena as integras como arquivos RTF armazenados em base64.
O sistema mantem o arquivo original no banco e cria uma versão - convertida em sintaxe markdown para uso por outros apps.

**Servidor**
Para rodar o servidor basta executar o `server.py`

A unica configuração relevante é a variavel SETTINGS que guarda a configuração do banco do MongoDB.

    SETTINGS['MONGODB_SERVER'] = 'localhost'
    SETTINGS['MONGODB_PORT'] = 27017
    SETTINGS['MONGODB_DB'] = 'discursos'
    

**Cliente**
Configure o `settings.js` para apontar para o servidor da aplicação.
O servidor esta configurado para suportar CORS.
