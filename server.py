#!/usr/bin/env python3

from sqlite3 import Error
from aiohttp import web
import os.path
import aiosqlite
import asyncio
import sqlite3
import random
import string
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

class Userdata():

    def __init__(self):

        self.conn = self.createConnection("userdata.db")
        self.initUserdata()
        self.sessions = []

    def createConnection(self, dbName):

        conn = None
        try:
            conn = sqlite3.connect(dbName)
            return conn
        except Error as e:
            print(e)

    def initUserdata(self):

        tableQuery = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        username text,
                                        salt text,
                                        hash text,
                                        priv text
                                    ); """

        c = self.conn.cursor()
        c.execute(tableQuery)

    async def auth(self, request):
        session = await get_session(request)
        if 'token' in session:
            token = session['token']
            if token in self.sessions:
                return True
        return False

    def generateToken(self):
        token =  ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(75))
        self.sessions.append(token)
        return token

    async def login(self, username, password):
        if username == "a" and password == "b":
            return True
        else:
            return False

    def userExists(self, username):
        return True

    def registerUser(self, username, password):
        return True

    def getUserPriv(self, username):
        return True

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
                                        example text,
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
        values = []
        values.append(funcName)
        values.append(lang)
        query = "SELECT * FROM snippets WHERE funcName = ? AND lang = ?"
        c.execute(query, values)
        rows = c.fetchall()
    
        if len(rows) > 0:
            return True
        else:
            return False

    def getCount(self):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets"
        c.execute(query)
        rows = c.fetchall()
        count = str(len(rows))

        data = {}
        data["count"] = count;

        json_data = json.dumps(data)
        return json_data

    def getSuggestions(self, query, lang):

        c = self.conn.cursor()
        values = []
        values.append("%" + query + "%")
        values.append("%" + query + "%")
        values.append(lang)
        query = "SELECT * FROM snippets WHERE (funcName like ? OR tags like ?) AND lang = ? limit 7"
        c.execute(query, values)
        rows = c.fetchall()

        results = []

        fields = [ix[0] for ix in c.description]

        for row in rows:
            rowDict = {}
            rowDict[fields[0]] = row[0]
            rowDict[fields[1]] = row[1]
            rowDict[fields[3]] = row[3]
            rowDict[fields[4]] = row[4]
            rowDict[fields[7]] = row[7]
            results.append(rowDict)
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data

    def getLatest(self):

        c = self.conn.cursor()
        query = "SELECT * FROM snippets ORDER BY id DESC LIMIT 7"
        c.execute(query)
        rows = c.fetchall()

        results = []

        fields = [ix[0] for ix in c.description]

        for row in rows:
            rowDict = {}
            rowDict[fields[0]] = row[0]
            rowDict[fields[1]] = row[1]
            results.append(rowDict)
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data

    def getSnippetsBetween(self, a, b):

        c = self.conn.cursor()
        values = []
        values.append(b)
        values.append(a)
        query = "SELECT * FROM snippets ORDER BY id LIMIT ? OFFSET ?"
        c.execute(query, values)
        rows = c.fetchall()

        results = []

        fields = [ix[0] for ix in c.description]

        for row in rows:
            rowDict = {}
            rowDict[fields[0]] = row[0]
            rowDict[fields[1]] = row[1]
            results.append(rowDict)
            
        data = {}
        data['results'] = results
        json_data = json.dumps(data)

        return json_data

    def getSnippet(self, funcName):

        #Retrieve information
        c = self.conn.cursor()
        values = []
        values.append(funcName)
        query = "SELECT * FROM snippets WHERE id = ? LIMIT 1"
        c.execute(query, values)
        rows = c.fetchall()
        
        data = {}
        if len(rows) == 0:
            data['funcName'] = ""
            data['tags'] = ""
            data['input'] = ""
            data['example'] = ""
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
        data['example'] = result[4]
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
 
    def addSnippet(self, funcName, tags, inputEx, example, deps, author, desc, lang, code):

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
        values.append(example)
        values.append(deps)
        values.append(author)
        values.append(desc)
        values.append(lang)
        values.append(code)

        query = '''INSERT INTO snippets(    funcName,
                                            tags,
                                            input,
                                            example,
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

    def deleteSnippet(self, funcID):

        c = self.conn.cursor()
        values = []
        values.append(int(funcID))
        query = "DELETE FROM snippets WHERE id = ?"
        c.execute(query, values)
        self.conn.commit()
    
    def modifySnippet(self, funcName, tags, inputEx, example, deps, author, desc, lang, code):
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
        self.userdata = Userdata()

        app = web.Application()
        app.router.add_get('/search/{lang}/{query}', self.search)
        app.router.add_get('/latest/', self.latest)
        app.router.add_get('/getSnippet/{query}', self.getSnippet)
        app.router.add_post('/addSnippet/', self.addSnippet)
        app.router.add_post('/login/', self.login)
        app.router.add_post('/delete/', self.deleteSnippet)
        app.router.add_get('/isAuth/', self.isAuth)
        app.router.add_get('/getSnippetCount/', self.getSnippetCount)
        app.router.add_get('/getSnippetsBetween/{a}/{b}', self.getSnippetsBetween)
    
        #For session handling
        key = "l7uPzuvRZt0bhv6ApgvR30stNZfAKV-VX7RLlgQvWLU="
        fernet_key = key.encode('utf-8')
        #fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(app, EncryptedCookieStorage(secret_key, httponly = False))
        
        here = Path(__file__).resolve().parent
        
        @aiohttp_jinja2.template('index.html')
        def index_handler(request):
            return {'name': 'Jonatan'}

        @aiohttp_jinja2.template('home.html')
        def home_handler(request):
            return {'name': 'Jonatan'}

        @aiohttp_jinja2.template('list.html')
        def list_handler(request):
            return {'name': 'Jonatan'}

        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
        app.router.add_get('/', index_handler)
        app.router.add_get('/home/', home_handler)
        app.router.add_get('/list/', list_handler)
        app.router.add_get('/list/{temp}', list_handler)

        app.router.add_static('/static/',
                      path=str('static'),
                      name='static')

        app.router.add_static('/images/',
                      path=str('images'),
                      name='images')

        cert = '/etc/letsencrypt/live/snippetdepot.com/fullchain.pem'
        key = '/etc/letsencrypt/live/snippetdepot.com/privkey.pem'

        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_OPTIONAL
        ssl_context.load_cert_chain(cert, key)

        web.run_app(app, ssl_context=ssl_context, host='78.141.209.170', port='443')

    async def isAuth(self, request):

        data = {}
        auth = await self.userdata.auth(request)
        if not auth:
            data['authenticated'] = "false"
            json_data = json.dumps(data)
            return await self.respond(request, json_data)
        else:
            data['authenticated'] = "true"
            json_data = json.dumps(data)
            return await self.respond(request, json_data)

    async def login(self, request):

        spam = await self.isSpam(request, 1)
        if spam:
            return await self.respond(request, "You are trying passwords too fast..")

        session = await get_session(request)
        post = await request.post()
        username = post.get('username')
        password = post.get('password')
        success = await self.userdata.login(username, password)
        if success:
            token = self.userdata.generateToken()
            session['token'] = token
            return web.Response(text=token)
        else:
            return web.Response(text="Adding account support soon..")

    async def search(self, request):

        name = request.match_info.get('query', 'Anonymous')
        lang = request.match_info.get('lang', 'Anonymous')
        result = self.database.getSuggestions(name, lang)

        return await self.respond(request, result)
        
    async def latest(self, request):

        result = self.database.getLatest()

        return await self.respond(request, result)

    async def getSnippetsBetween(self, request):

        a = request.match_info.get('a', 'Anonymous')
        b = request.match_info.get('b', 'Anonymous')
        result = self.database.getSnippetsBetween(a, b)

        return await self.respond(request, result)

    async def getSnippet(self, request):
        
        name = request.match_info.get('query', 'Anonymous')
        result = self.database.getSnippet(name)

        return await self.respond(request, result)

    async def getSnippetCount(self, request):
        
        count = self.database.getCount()

        return await self.respond(request, count)

    async def addSnippet(self, request):
 
        spam = await self.isSpam(request, 1)
        if spam:
            return await self.respond(request, "You can only add one snippet each 10 seconds..")
        post = await request.post()
        funcName = post.get('funcName')
        tags = post.get('tags')
        inputEx = post.get('input')
        example = post.get('example')
        deps = post.get('deps')
        author = post.get('author')
        desc = post.get('desc')
        lang = post.get('lang')
        code = post.get('code')

        result = self.database.addSnippet(  funcName,
                                            tags,
                                            inputEx,
                                            example,
                                            deps,
                                            author,
                                            desc,
                                            lang,
                                            code)
    
        if len(result) > 0:
            return await self.respond(request, result)

    #Admin features
    async def deleteSnippet(self, request):

        spam = await self.isSpam(request, 1)
        if spam:
            return await self.respond(request, "You are doing this too fast..")

        auth = await self.userdata.auth(request)
        if not auth:
            return await self.respond(request, "Not authenticated..")
        
        post = await request.post()
        funcID = post.get('id')
        self.database.deleteSnippet(funcID)

        return await self.respond(request, "Snippet deleted..")

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




