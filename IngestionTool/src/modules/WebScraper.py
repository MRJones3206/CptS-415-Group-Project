from modules.ConsoleColors import bcolors
import requests
from  bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, url, download_directory):
        self.url = str(url)
        self.download_directory = download_directory
        print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKBLUE}Webscraper Constructed{bcolors.ENDC} | URL: {url}")

    def scrape(self):
        print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKGREEN}Starting webscrape{bcolors.ENDC}")
        page = requests.get(self.url)
        
        if page.status_code != 200:
            raise ConnectionError
        urls = []
        names = []
        soup = BeautifulSoup(page.content, "html.parser")

        table = soup.find_all("table")[1]
        i = -1
        rows = table.findChildren('tr', recursive=False)
        for row in rows:
            tds = row.findChildren('td', recursive=False)
            for td in tds:
                inner_tables = td.findChildren('table', recursive=False)
                for table in inner_tables:
                    i+=1
                    table_name_prefix = f"Table{i}"
                    rows = table.findChildren('tr', recursive=False) 
                    for row in rows:
                        cells = row.findChildren("td", recursive=False)
                        # -- Only 1 in each row, but it's good be able to access all other row details
                        for cell in cells:
                            links = cell.findChildren('a')
                            for link in links:
                                if link:
                                    _fullURL = self.url + link.get('href')
                                    if _fullURL.endswith(".zip"):
                                        urls.append(_fullURL)
                                        names.append(table_name_prefix + link['href'])

        names_urls = zip(names, urls)
                
        for name, url in names_urls:
            
            dir = self.download_directory / name

            if not dir.exists():
                rq = requests.get(url)
                print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKGREEN}Downloading {name} from {url}{bcolors.ENDC}")
                with dir.open("wb") as fp:
                    fp.write(rq.content)
            else:
                print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKCYAN}Directory: {dir} already exists.... skipping download{bcolors.ENDC}")

        print(f"{bcolors.INFO} [Info] >\t{bcolors.ENDC}{bcolors.OKCYAN}Completed File Download{bcolors.ENDC}")

