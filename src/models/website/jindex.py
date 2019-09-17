import asyncio

import aiohttp
import bs4
from tqdm import tqdm, trange

from src.example import Website


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()


class jindex(Website):

    async def get_max_page(self):
        async with aiohttp.ClientSession() as session:
            task = asyncio.tasks.create_task(fetch(session, self.url))
            page = await asyncio.gather(task)

        for one in tqdm(page, desc="Fetching max page",  bar_format=self.printstring):
            strainer = bs4.SoupStrainer("div", {'class': ['jix_pagination_pages']})
            soup = bs4.BeautifulSoup(one.decode('utf-8'), "lxml", parse_only=strainer)
            pages = soup.find("div", {'class': ['jix_pagination_pages']})

            hrefs = []

            for element in pages:
                if 'href' in str(element):
                    try:
                        hrefs.append(int(element.contents[0]))
                    except Exception as e:
                        pass

            self.max_page = max(hrefs) + 1

    def generate_urls_for_pages(self):
        urls = []

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_max_page())

        for i in tqdm(range(1, self.max_page), desc="Generating URLS", bar_format=self.printstring):
            urls.append(self.url + "&page={}".format(i))

        return urls
