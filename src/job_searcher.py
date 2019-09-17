import asyncio
import re
from datetime import datetime

import aiohttp
import bs4
import pandas
from pip._vendor.colorama import Fore
from tqdm import tqdm

from src.gspread import spreadsheet
from src.models.website.jindex import jindex
from src.models.job import Job


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()


class job_searcher:
    def __init__(self):
        self.website = jindex("Jobindex", "https://www.jobindex.dk/jobsoegning?geoareaid=15182&geoareaid=15187&geoareaid=4&geoareaid=3&geoareaid=2&geoareaid=15180&geoareaid=16149&subid=1&subid=2&subid=3&subid=4&subid=6&subid=7&subid=93&subid=116&subid=127")
        self.jobs = []
        self.html_pages = []
        self.printstring = "{desc:<20}{percentage:3.0f}%%|%s{bar}%s{r_bar}" % (Fore.LIGHTBLUE_EX, Fore.RESET)

    async def fetch_all_urls(self, weburls):
        tasks = []

        async with aiohttp.ClientSession() as session:
            for url in weburls:
                tasks.append(asyncio.tasks.create_task((fetch(session, url))))

            self.html_pages = [await f for f in
                               tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching:", bar_format=self.printstring)]

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
            joblink = str(paidjob.find("b").parent.attrs['href']).replace("'", "")
            paidjob.find("div", {'class': ['jix_toolbar', 'jix_appetizer_toolbar']}).decompose()
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
                    descriptionstring += paragraph.replace("<b>", "").replace("</b>", "")

            if len(job_page.find("p").contents) > 2:
                location = str(job_page.find("p").contents[2]).split(' ')[-1]
            else:
                location = "Couldn't find location"

            newjob = Job(title=title, location=location, company=company, joblink=joblink,
                         description=descriptionstring, publishdate=publishdate)

            steder = ["Copenhagen", "Glostrup", "København", "Aars", "Aalborg", "Støvring", "Hobro", "Aarhus",
                      "Randers", "Couldn't find location"]
            #areas = ["python", "python3", "C#", "dotnet", "dotnet core", ".net", "asp.net", "mysql", "sql", "devops", "jenkins", "git", "gitlab"]
            if re.compile('|'.join(steder), re.IGNORECASE).search(location):
                #if re.compile('|'.join(areas), re.IGNORECASE).search(descriptionstring):
                self.jobs.append(newjob)

    def write_to_csv(self):
        df = pandas.DataFrame.from_records([s.as_dict() for s in self.jobs])
        df.to_csv(r'C:\users\alex\desktop\info.csv', header=True, sep='|')

    def jobs_unique_and_sorted(self):
        # self.jobs = list(set(self.jobs))
        self.jobs.sort(key=lambda x: x.company, reverse=False)


if __name__ == '__main__':
    js = job_searcher()
    gspread = spreadsheet()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(js.fetch_all_urls(js.website.generate_urls_for_pages()))

    js.scrape_all_pages()

    with tqdm(iterable=False, total=2, bar_format=js.printstring) as pbar:
        pbar.set_description("Sorting Jobs")
        js.jobs_unique_and_sorted()
        pbar.update(1)
        pbar.set_description("Writing CSV")
        js.write_to_csv()
        pbar.update(1)

    with tqdm(iterable=False, total=2, bar_format=js.printstring) as pbar:
        pbar.set_description("Creating Worksheet")
        gspread.create_new_worksheet()
        pbar.update(1)
        pbar.set_description("Uploading CSV")
        gspread.insert_csv_file()
        pbar.update(1)
