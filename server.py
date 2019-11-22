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

    def addSnippet(self, funcName, tags, inputEx, outputEx, deps, author, desc, code):

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

class Server():
    
    def __init__(self):

        self.database = Database()

        app = web.Application()
        app.router.add_get('/search/{query}', self.search)
        app.router.add_get('/latest/', self.latest)
        app.router.add_post('/addSnippet/', self.addSnippet)
        
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

        self.database.addSnippet(   funcName,
                                    tags,
                                    inputEx,
                                    outputEx,
                                    deps,
                                    author,
                                    desc,
                                    code)

        print("Added function: " + funcName)

    async def getSnippet(self, name):

        return "test"

#------ MAIN ------#
server = Server()




