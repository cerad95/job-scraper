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


class jindex(Website):
    steder = ["Copenhagen", "Glostrup", "København", "Aalborg",
                      "Couldn't find location", "Region Hovedstaden", "Aalborg eller København", "Billund", "Danmark", "Fjernarbejde", "Japan", "Oslo", "Malmö", "Stockholm", "Søborg", ]
    areas = ["python", "python3", "C#", "dotnet", "dotnet core", ".net", "asp.net", "mysql",
                     "sql", "devops", "jenkins", "git", "gitlab", "linux", "windows", "html", "css", 
                     "dapper", "entity", "django", "nodejs", "docker", "rest", "tensorflow", "tkinker", 
                     "vmware", "tfs", "uml", "systemudvikling", "microservices", "integration", "test", 
                     "functional test", "funktionelle test", "tests"]

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

    def jobs_unique_and_sorted(self):
        self.jobs = list(set(self.jobs))
        self.jobs.sort(key=lambda x: (x.location, x.title), reverse=False)

    def scrape_all_pages(self):
        for job_page in tqdm(self.html_pages, desc="Scraping:", bar_format=self.printstring):
            strainer = bs4.SoupStrainer("div", {'class': ['PaidJob']})
            soup = bs4.BeautifulSoup(job_page.decode('utf-8'), 'lxml', parse_only=strainer)
            self.scrape_page(soup)

    def scrape_page(self, job_page):
        paidjobs = job_page.find_all("div", {'class': ['PaidJob']})

        for paidjob in paidjobs:
            title_div = paidjob.find("b")
            title = str(title_div.contents[0])
            publishdate = datetime.strptime(
                str(paidjob.find("li", {'class': ['toolbar-pubdate']}).contents[1].attrs['datetime']), '%Y-%m-%d')
            joblink = str(paidjob.find(
                "b").parent.attrs['href']).replace("'", "")
            paidjob.find(
                "div", {'class': ['jix_toolbar', 'jix_appetizer_toolbar']}).decompose()
            paragraphs = paidjob.find_all(["p", 'li'], recursive=True)

            for paragraph in paragraphs:
                if str(paragraph) == "<p></p>" or "<p>\n<a":
                    del paragraph

            if len(paragraphs[0].contents) != 0:
                company = paragraphs[0].contents[1].contents[0].contents[0]
            else:
                company = paragraphs[1].contents[1].contents[0].contents[0]

            company = str(company).replace("|", "/")

            description = []
            for paragraph in paragraphs:
                for content in paragraph.contents:
                    if type(content) == bs4.NavigableString:
                        description.append(str(content))
                    elif type(content) == bs4.Tag and len(content.contents) > 0:
                        description.append(str(content.contents[0]))

            del (description[0:3])

            descriptionstring = ""
            for paragraph in description:
                if paragraph == " ":
                    del paragraph
                else:
                    descriptionstring += paragraph.replace(
                        "<b>", "").replace("</b>", "")

            if len(job_page.find("p").contents) > 2:
                location = str(job_page.find("p").contents[2]).split(' ')[-1]
            else:
                location = "N/A"
            
            if descriptionstring:
                descriptionstring.replace("|","")
                descriptionstring.replace("\n","")
                descriptionstring.strip()

            if title:
                title.replace("|","")
                title.replace("\n","")
                title.strip()

            newjob = Job(title=title, location=location, company=company, joblink=joblink, description=descriptionstring, publishdate=publishdate, urlname="jobindex")

            if re.compile('|'.join(self.steder), re.IGNORECASE).search(location) and re.compile('|'.join(self.areas), re.IGNORECASE).search(descriptionstring):
                self.jobs.append(newjob)

