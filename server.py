#!/usr/bin/env python3

from sqlite3 import Error
from aiohttp import web
import aiosqlite
import asyncio
import sqlite3
import aiohttp_jinja2
import jinja2
from pathlib import Path
import json
import time
import ssl
import os

import base64
from cryptography import fernet
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

class Database():

    def __init__(self):

        self.conn = self.createConnection("data.db")
        self.initDatabase()

    def createConnection(self, dbName):

        conn = None 
        try:
            conn = sqlite3.connect(dbName)
            return conn
        except Error as e:
            print(e)

    def initDatabase(self):

        tableQuery = """ CREATE TABLE IF NOT EXISTS snippets (
                                        id integer PRIMARY KEY,
                                        funcName text,
                                        tags text,
                                        input text,
                                        output text,
                                        deps text,
                                        author text,
                                        desc text,
                                        lang text,
                                        code text,
                                        review text
                                    ); """

        c = self.conn.cursor()
        c.execute(tableQuery)

    def snippetExists(self, funcName, lang):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets WHERE funcName = '" + funcName + "' AND lang = '" + lang + "'"
        c.execute(query)
        rows = c.fetchall()
    
        if len(rows) > 0:
            return True
        else:
            return False

    def getSuggestions(self, funcName, lang):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets WHERE funcName like '%" + funcName + "%' AND lang = '" + lang + "'limit 10"
        c.execute(query)
        rows = c.fetchall()

        results = []

        for row in rows:
            results.append(row[1])
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data

    def getLatest(self):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets ORDER BY id DESC LIMIT 10"
        c.execute(query)
        rows = c.fetchall()

        results = []

        for row in rows:
            results.append(row[1])
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data

    def getSnippet(self, funcName):

        #Retrieve information
        c = self.conn.cursor()
        query = "SELECT * FROM snippets WHERE funcName = '" + funcName + "' LIMIT 1"
        c.execute(query)
        rows = c.fetchall()
        
        data = {}
        if len(rows) == 0:
            data['funcName'] = ""
            data['tags'] = ""
            data['input'] = ""
            data['output'] = ""
            data['deps'] = ""
            data['author'] = ""
            data['desc'] = ""
            data['lang'] = ""
            data['code'] = ""
            json_data = json.dumps(data)
            return json_data
    
        result = rows[0]
    
        data['funcName'] = result[1]
        data['tags'] = result[2]
        data['input'] = result[3]
        data['output'] = result[4]
        data['deps'] = result[5]
        data['author'] = result[6]
        data['desc'] = result[7]
        data['lang'] = result[8]
        data['code'] = result[9]

        json_data = json.dumps(data)
        return json_data

    def validLanguage(self, lang):

        langList = [    "javascript",
                        "python2",
                        "python3",
                        "java",
                        "php",
                        "cpp",
                        "csharp",
                        "typescript",
                        "shell",
                        "c",
                        "ruby"]

        if lang in langList:
            return True
        return False
 
    def addSnippet(self, funcName, tags, inputEx, outputEx, deps, author, desc, lang, code):

        lang = lang.strip().lower()

        if funcName == "":
            return "The snippet must have a name.."
        if desc == "":
            return "The snippet must have a description.."
        if code == "":
            return "The snippet must have a code.."

        if self.snippetExists(funcName, lang):
            return "Name already exists.."

        if not self.validLanguage(lang):
            return "The language have not been added yet.."

        values = []
        values.append(funcName)
        values.append(tags)
        values.append(inputEx)
        values.append(outputEx)
        values.append(deps)
        values.append(author)
        values.append(desc)
        values.append(lang)
        values.append(code)

        query = '''INSERT INTO snippets(    funcName,
                                            tags,
                                            input,
                                            output,
                                            deps,
                                            author,
                                            desc,
                                            lang,
                                            code)
              VALUES(?,?,?,?,?,?,?,?,?)'''
        c = self.conn.cursor()
        c.execute(query, values)
        self.conn.commit()
    
        return "Thank you!"
    
    def modifySnippet(self, funcName, tags, inputEx, outputEx, deps, author, desc, lang, code):
        return 0

    def returnSnippetHistory(self, funcName):
        return 0

    def rollbackSnippet(self, funcName, historyID):
        return 0

class Server():
    
    def __init__(self):

        #Stores last activity by IP 
        self.activityDict = {}

        self.database = Database()

        app = web.Application()
        app.router.add_get('/search/{query}', self.search)
        app.router.add_get('/search/{lang}/{query}', self.search)
        app.router.add_get('/latest/', self.latest)
        app.router.add_get('/getSnippet/{query}', self.getSnippet)
        app.router.add_post('/addSnippet/', self.addSnippet)
    
        #For session handling
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key))
        
        here = Path(__file__).resolve().parent
        
        @aiohttp_jinja2.template('index.html')
        def index_handler(request):
            return {'name': 'Jonatan'}

        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
        app.router.add_get('/', index_handler)

        app.router.add_static('/static/',
                      path=str('static'),
                      name='static')

        app.router.add_static('/images/',
                      path=str('images'),
                      name='images')

        cert = '/etc/letsencrypt/live/snippetdepot.com/fullchain.pem'
        key = '/etc/letsencrypt/live/snippetdepot.com/privkey.pem'

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.verify_mode = ssl.CERT_OPTIONAL
        ssl_context.load_cert_chain(cert, key)

        web.run_app(app, ssl_context=ssl_context, host='78.141.209.170', port='443')

    async def search(self, request):
        
        name = request.match_info.get('query', 'Anonymous')
        lang = request.match_info.get('lang', 'Anonymous')
        result = self.database.getSuggestions(name, lang)

        return await self.respond(request, result)
        
    async def latest(self, request):

        result = self.database.getLatest()

        return await self.respond(request, result)

    async def getSnippet(self, request):
        
        name = request.match_info.get('query', 'Anonymous')
        result = self.database.getSnippet(name)

        return await self.respond(request, result)

    async def addSnippet(self, request):
 
        spam = await self.isSpam(request, 60)
        if spam:
            return await self.respond(request, "You can only add one snippet per minute..")
        post = await request.post()
        funcName = post.get('funcName')
        tags = post.get('tags')
        inputEx = post.get('input')
        outputEx = post.get('output')
        deps = post.get('deps')
        author = post.get('author')
        desc = post.get('desc')
        lang = post.get('lang')
        code = post.get('code')

        result = self.database.addSnippet(  funcName,
                                            tags,
                                            inputEx,
                                            outputEx,
                                            deps,
                                            author,
                                            desc,
                                            lang,
                                            code)
    
        if len(result) > 0:
            return await self.respond(request, result)

    async def isSpam(self, request, allowedRequestRate):
        spam = False
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            host, port = peername
            currentTime = round(time.time())
            if host in self.activityDict.keys():
                oldTime = self.activityDict[host]
                if (currentTime - oldTime) < allowedRequestRate:
                    spam = True
            self.activityDict[host] = currentTime
        return spam 

    async def respond(self, request, response):
        resp = web.StreamResponse()
        result = response.encode("utf8")
        resp.content_length = len(result)
        resp.content_type = 'text/plain'
        await resp.prepare(request)
        await resp.write(result)
        await resp.write_eof()
        return resp

#------ MAIN ------#
server = Server()




