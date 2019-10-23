from pip._vendor.colorama import Fore


class Website:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.html_pages = []
        self.max_page = 0
        self.jobs = []
        self.printstring = "{desc:<20}{percentage:3.0f}%%|%s{bar}%s{r_bar}" % (Fore.LIGHTBLUE_EX, Fore.RESET)
        self.steder = ["Copenhagen", "Glostrup", "København", "Aalborg",
                      "Couldn't find location", "Region Hovedstaden", "Aalborg eller København", "Billund", "Danmark", "Fjernarbejde", "Japan", "Oslo", "Malmö", "Stockholm", "Søborg", ]
        self.areas = ["python", "python3", "C#", "dotnet", "dotnet core", ".net", "asp.net", "mysql",
                     "sql", "devops", "jenkins", "git", "gitlab", "linux", "windows", "html", "css", 
                     "dapper", "entity", "django", "nodejs", "docker", "rest", "tensorflow", "tkinker", 
                     "vmware", "tfs", "uml", "systemudvikling", "microservices", "integration", "test", 
                     "functional test", "funktionelle test", "tests"]

    def get_max_page(self):
        pass

    def generate_urls_for_pages(self):
        pass

    
