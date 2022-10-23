from modules.ConsoleColors import bcolors

class WebScraper:
    def __init__(self, url):
        self.url = str(url)
        print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKBLUE}Webscraper Constructed{bcolors.ENDC} | URL: {url}")

    def scrape(self):
        print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKGREEN}Starting webscrape{bcolors.ENDC}")
        

