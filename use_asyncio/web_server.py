#!/usr/bin/env python
# -*- coding:utf-8 -*-

import asyncio

from aiohttp import web


async def index(request):
    await asyncio.sleep(0.5)
    body = b"<h1>this is index</h1>"
    return web.Response(body=body)


async def hello(request):
    await asyncio.sleep(0.5)
    body = "<h1>hello, %s</h1>" % request.match_info['name']
    return web.Response(body=body)


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/index', index)
    app.router.add_route('GET', '/hello/{name}', hello)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server is running at http://127.0.0.1:8000')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
