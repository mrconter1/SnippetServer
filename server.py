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
                                        code text
                                    ); """

        c = self.conn.cursor()
        c.execute(tableQuery)

        tableQuery = """ CREATE TABLE IF NOT EXISTS code (
                                        funcName text,
                                        javascript text,
                                        python2 text,
                                        python3 text,
                                        php text,
                                        cpp text,
                                        csharp text,
                                        typescript text,
                                        shell text,
                                        c text,
                                        ruby text
                                    ); """

        c = self.conn.cursor()
        c.execute(tableQuery)

    def snippetExists(self, funcName):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets WHERE funcName = '" + funcName + "'"
        c.execute(query)
        rows = c.fetchall()
    
        if len(rows) > 0:
            return True
        else:
            return False

    def getSuggestions(self, funcName):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets WHERE funcName like '%" + funcName + "%' limit 10"
        c.execute(query)
        rows = c.fetchall()

        results = []

        for row in rows:
            results.append(row[1])
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data.encode("utf8")

    def getLatest(self):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets ORDER BY id DESC LIMIT 10"
        c.execute(query)
        rows = c.fetchall()

        results = []

        for row in rows:
            results.append(row[1])
            print(row[1])
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data.encode("utf8")

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
            json_data = json.dumps(data)
            return json_data.encode("utf8")
    
        result = rows[0]
    
        data['funcName'] = result[1]
        data['tags'] = result[2]
        data['input'] = result[3]
        data['output'] = result[4]
        data['deps'] = result[5]
        data['author'] = result[6]
        data['desc'] = result[7]

        #Retrieve code
        c = self.conn.cursor()
        query = "SELECT * FROM code WHERE funcName = '" + funcName + "' LIMIT 1"
        c.execute(query)
        rows = c.fetchall()
    
        result = rows[0]

        names = list(map(lambda x: x[0], c.description))
        i = 1
        for name in names:
            data['code_'+name] = result[i]
            i += 1

        json_data = json.dumps(data)
        return json_data.encode("utf8")
    
    def addSnippet(self, funcName, tags, inputEx, outputEx, deps, author, desc, code):

        if self.snippetExists(funcName):
            return "Name already exists.."

        values = []
        values.append(funcName)
        values.append(tags)
        values.append(inputEx)
        values.append(outputEx)
        values.append(deps)
        values.append(author)
        values.append(desc)
        values.append(code)
        query = '''INSERT INTO snippets(    funcName,
                                            tags,
                                            input,
                                            output,
                                            deps,
                                            author,
                                            desc,
                                            code)
              VALUES(?,?,?,?,?,?,?,?)'''
        c = self.conn.cursor()
        c.execute(query, values)
        self.conn.commit()
    
        return "Thank you! Snippet will be added after a review.."

class Server():
    
    def __init__(self):

        self.database = Database()

        app = web.Application()
        app.router.add_get('/search/{query}', self.search)
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

        web.run_app(app, host='78.141.209.170')


    async def search(self, request):
        
        resp = web.StreamResponse()
        name = request.match_info.get('query', 'Anonymous')
        result = self.database.getSuggestions(name)
        resp.content_length = len(result)
        resp.content_type = 'text/plain'
        await resp.prepare(request)
        await resp.write(result)
        await resp.write_eof()
        return resp
    
    async def latest(self, request):

        resp = web.StreamResponse()
        result = self.database.getLatest()
        resp.content_length = len(result)
        resp.content_type = 'text/plain'
        await resp.prepare(request)
        await resp.write(result)
        await resp.write_eof()
        return resp

    async def getSnippet(self, request):
        
        resp = web.StreamResponse()
        name = request.match_info.get('query', 'Anonymous')
        result = self.database.getSnippet(name)
        resp.content_length = len(result)
        resp.content_type = 'text/plain'
        await resp.prepare(request)
        await resp.write(result)
        await resp.write_eof()
        return resp

    async def addSnippet(self, request):
 
        post = await request.post()
        funcName = post.get('funcName')
        tags = post.get('tags')
        inputEx = post.get('input')
        outputEx = post.get('output')
        deps = post.get('deps')
        author = post.get('author')
        desc = post.get('desc')
        code = post.get('code')

        result = self.database.addSnippet(  funcName,
                                            tags,
                                            inputEx,
                                            outputEx,
                                            deps,
                                            author,
                                            desc,
                                            code)
    
        if len(result) > 0:
            resp = web.StreamResponse()
            result = result.encode("utf8")
            resp.content_length = len(result)
            resp.content_type = 'text/plain'
            await resp.prepare(request)
            await resp.write(result)
            await resp.write_eof()
            return resp


#------ MAIN ------#
server = Server()




