from pip._vendor.colorama import Fore


class Website:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.html_pages = []
        self.max_page = 0
        self.jobs = []
        self.printstring = "{desc:<20}{percentage:3.0f}%%|%s{bar}%s{r_bar}" % (Fore.LIGHTBLUE_EX, Fore.RESET)

    def get_max_page(self):
        pass

    def generate_urls_for_pages(self):
        pass

    
