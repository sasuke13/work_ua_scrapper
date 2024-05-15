import asyncio

import aiohttp
from bs4 import BeautifulSoup

headers = {
    'User-Agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
}


def get_bs4_instance(target) -> BeautifulSoup:
    return BeautifulSoup(target, 'html5lib')


async def get_site_content(url) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            text = await resp.read()

    return get_bs4_instance(text.decode('utf-8'))


print(asyncio.run(get_site_content('https://en.m.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population')))
