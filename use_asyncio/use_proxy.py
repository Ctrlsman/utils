import asyncio
import aiohttp


@asyncio.coroutine
def do_request():
    proxy_url = 'http://198.23.237.213:1080'  # your proxy address
    response = yield from aiohttp.request(
        'GET', 'http://google.com',
        proxy=proxy_url,
    )
    return response


loop = asyncio.get_event_loop()
loop.run_until_complete(do_request())