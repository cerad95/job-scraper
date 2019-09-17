import csv
from pprint import pprint

import pygsheets
import datetime


class spreadsheet:
    def __init__(self):
        self.name = "jobs"
        self.spreadsheet_con = pygsheets.authorize()
        self.spreadsheet = self.spreadsheet_con.open(self.name)
        self.worksheet = self.spreadsheet.worksheet('index', 0)

    def create_new_worksheet(self):
        now = datetime.datetime.now()
        now = str(now.strftime("%B-%d-%Y_%H:%M:%S"))
        self.spreadsheet.add_worksheet(now, rows=1000, cols=6, index=0)
        self.worksheet = self.spreadsheet.worksheet_by_title(now)

    def insert_csv_file(self):
        with open('C:/users/alex/desktop/info.csv', encoding='utf-8', mode='r') as f:
            reader = csv.reader(f, skipinitialspace=True, delimiter='|', quotechar="'")
            data = list(reader)
            self.worksheet.update_values('A1', data)



