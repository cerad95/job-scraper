import asyncio
import re
from datetime import datetime

import aiohttp
import bs4

from tqdm import tqdm

from job import Job
from website import Website

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()


class graduateland(Website):
    async def fetch_all_urls(self, weburls):
        tasks = []

        async with aiohttp.ClientSession() as session:
            for url in weburls:
                tasks.append(asyncio.tasks.create_task((fetch(session, url))))

            self.html_pages = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching:", bar_format=self.printstring)]

    async def get_max_page(self):
        async with aiohttp.ClientSession() as session:
            task = asyncio.tasks.create_task(fetch(session, self.url))
            page = await asyncio.gather(task)

        for one in tqdm(page, desc="Fetching max page",  bar_format=self.printstring):
            strainer = bs4.SoupStrainer("div", {'class': ['pagination']})
            soup = bs4.BeautifulSoup(one.decode('utf-8'), "lxml", parse_only=strainer)
            pages = soup.find("div", {'class': ['pagination']})

            hrefs = []

            for element in pages:
                if 'href' in str(element):
                    try:
                        hrefs.append(int(element.contents[0]))
                    except Exception as e:
                        pass

            self.max_page = int(max(hrefs))

    def generate_urls_for_pages(self):
        urls = []

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_max_page())

        for i in tqdm(range(1, self.max_page), desc="Generating URLS", bar_format=self.printstring):
            if i % 10 == 0:
                urls.append(self.url + "&offset={}".format(i))

        return urls

    def jobs_unique_and_sorted(self):
        self.jobs = list(set(self.jobs))
        self.jobs.sort(key=lambda x: (x.location, x.title), reverse=False)

    def scrape_all_pages(self):
        for job_page in tqdm(self.html_pages, desc="Scraping:", bar_format=self.printstring):
            strainer = bs4.SoupStrainer("div", {'class': ['hidden-xs section-view-list']})
            soup = bs4.BeautifulSoup(job_page.decode('utf-8'), 'lxml', parse_only=strainer)
            self.scrape_page(soup)

    def scrape_page(self, job_page):
        paidjobs = job_page.find_all("div", {'class': ['bem-enabled']})

        for paidjob in paidjobs:
            title = paidjob.find("h1", {'class': ["job-box__heading"]}).text.strip().replace("\n","").replace("|"," ")
            joblink = paidjob.find("a", href=True).attrs['href']
            joblink = "https://graduateland.com" + joblink
            
            company = paidjob.find("span", {'class': ['job-box__company-name']})
            if company:
                company = company.text.strip()

            location = paidjob.find("div", {'class': ['job-box__meta-info']}).contents[5].text.strip()
            
            publishdate = paidjob.find("span", {'class': ['text-light-gray', 'text-warning']})
            if not publishdate:
                publishdate = "N/A"
            else:
                publishdate = publishdate.text.strip()

            
            descriptionstring = paidjob.find("div", {'class': ['job-box__text']})

            if descriptionstring.contents[-1] is not None:
                descriptionstring = str(descriptionstring.contents[-1]).strip().replace("|", "")
            else:
                descriptionstring = "N/A"


            newjob = Job(title=title, location=location, company=company, joblink=joblink, description=descriptionstring, publishdate=publishdate, urlname="Graduateland")
            
            self.clean_object(newjob)

            if re.compile('|'.join(self.steder), re.IGNORECASE).search(location):
                self.jobs.append(newjob)
        

