#!/usr/bin/env python3

from aiohttp import web
import aiosqlite
import asyncio
import aiohttp_jinja2
import jinja2
from pathlib import Path

class Server():
    
    def __init__(self):


        app = web.Application()

        here = Path(__file__).resolve().parent
        
        @aiohttp_jinja2.template('index.html')
        def index_handler(request):
            return web.HTTPFound('https://www.snippetdepot.com')

        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(here)))
        app.router.add_get('/', index_handler)

        web.run_app(app, host='78.141.209.170', port='80')

#------ MAIN ------#
server = Server()




