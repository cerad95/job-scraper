import asyncio
import re
import aiohttp
import bs4
import pandas
import os

from gspread import spreadsheet
from jindex import jindex
from job import Job
from pip._vendor.colorama import Fore
from tqdm import tqdm
from datetime import datetime
from sys import platform as _platform

from graduateland import graduateland


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()


class job_searcher:
    def __init__(self):
        self.websites = []
        self.websites.append(graduateland("Graduateland", "https://graduateland.com/da/jobs?types%5B%5D=1&types%5B%5D=3&positions%5B%5D=15&languages%5B%5D=1&languages%5B%5D=23&limit=10"))
        self.websites.append(jindex("Jobindex", "https://www.jobindex.dk/jobsoegning?geoareaid=15182&geoareaid=15187&geoareaid=4&geoareaid=3&geoareaid=2&geoareaid=15180&geoareaid=16149&subid=1&subid=2&subid=3&subid=4&subid=6&subid=7&subid=93&subid=116&subid=127"))

        self.printstring = "{desc:<20}{percentage:3.0f}%%|%s{bar}%s{r_bar}" % (Fore.LIGHTBLUE_EX, Fore.RESET)

    def write_to_csv(self):

        df = 0

        for site in self.websites:
            df = pandas.DataFrame.from_records([s.as_dict() for s in site.jobs])

        df.reset_index(drop=True, inplace=True)

        if _platform == "linux" or _platform == "linux2":
            df.to_csv(r'data.csv', header=True, sep='|', index=False)
        elif _platform == "darwin":
            print("mac is trash")
        elif _platform == "win32":
            df.to_csv(r'C:\users\alex\desktop\info.csv',
                      header=True, sep='|', index=False)
        elif _platform == "win64":
            df.to_csv(r'C:\users\alex\desktop\info.csv',
                      header=True, sep='|', index=False)

    def jobs_unique_and_sorted(self):
        for website in self.websites:
            website.jobs = list(set(website.jobs))
            website.jobs.sort(key=lambda x: (x.location, x.title), reverse=False)


if __name__ == '__main__':
    js = job_searcher()

    loop = asyncio.get_event_loop()

    for website in js.websites:
        urls = website.generate_urls_for_pages()
        loop.run_until_complete(website.fetch_all_urls(urls))
        website.scrape_all_pages()

    while True:
        decision = input("\nStore local or cloud: ")
        print("\n")
        if decision == "local":
            with tqdm(iterable=False, total=2, bar_format=js.printstring) as pbar:
                pbar.set_description("Sorting Jobs")
                js.jobs_unique_and_sorted()
                pbar.update(1)
                pbar.set_description("Writing CSV")
                js.write_to_csv()
                pbar.update(1)
            break
        elif decision == "cloud":
            gspread = spreadsheet()
            with tqdm(iterable=False, total=5, bar_format=js.printstring) as pbar:
                pbar.set_description("Sorting Jobs")
                js.jobs_unique_and_sorted()
                pbar.update(1)
                pbar.set_description("Writing CSV")
                js.write_to_csv()
                pbar.update(1)
                pbar.set_description("Creating Worksheet")
                gspread.create_new_worksheet()
                pbar.update(1)
                pbar.set_description("Uploading CSV")
                gspread.insert_csv_file()
                pbar.update(1)
                pbar.set_description("Deleting leftover CSV file")
                os.remove("data.csv")
                pbar.update(1)
            break
        else:
            print("Only \'local\' or \'cloud\' as input is accepted.")
