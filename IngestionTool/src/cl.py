import click
import time
import shutil
from pathlib import Path
from modules.WebScraper import WebScraper
from modules.ConsoleColors import bcolors

@click.group()
def cli():
    pass

@click.command()
@click.option(
    "--test",
    help="""Should just print hello world.""",
    required=False,
    type=str
)
def test_run(test):
    print(f"The test print is: {test}")


@click.command()
@click.option(
    "-path",
    help="""Path to save scraped zip files to.""",
    required=True,
    type=str
)
def scrape_yt(path):
    try:
        if(path[0] == '~'):
            dir = Path.home()
            dir = dir / path[2:]
            print(dir)
        else:
            dir = Path(path)
        

        print(f"{bcolors.INFO} [INFO] >\t{bcolors.ENDC}{bcolors.OKGREEN}Directory: {dir} exists: {dir.exists()}{bcolors.ENDC}")
        if(not dir.exists()):
            raise NotADirectoryError


        # -- Create the directory
        dir = dir / "YoutubeAnalyzerData"
        print(f"{bcolors.INFO} [Info] > \t{bcolors.ENDC}Creating new data directory at: {dir}")
        dir.mkdir(parents=True, exist_ok=True )

        # -- Scrape the zips from the page.
        scraper = WebScraper("http://netsg.cs.sfu.ca/youtubedata/", dir)
        scraper.scrape()

    except NotADirectoryError:
        print(f"{bcolors.FAIL}This filepath does not exist.{bcolors.ENDC}")

    except ConnectionError:
        print(f"{bcolors.FAIL}The requested page returned a status other than 200{bcolors.ENDC}")
@click.command()
@click.option(
    "-path",
    help="""Path to saved zip files.""",
    required=True,
    type=str
)
def decompress_yt(path):
    try:
        if(path[0] == '~'):
            dir = Path.home()
            dir = dir / path[2:]
            print(dir)
        else:
            dir = Path(path)
        

        print(f"{bcolors.INFO} [INFO] >\t{bcolors.ENDC}{bcolors.OKGREEN}Directory: {dir} exists: {dir.exists()}{bcolors.ENDC}")
        
        if(not dir.exists()):
            raise NotADirectoryError

        dir = dir / "YoutubeAnalyzerData"
        print(f"{bcolors.INFO} [INFO] >\t{bcolors.ENDC}{bcolors.OKGREEN}Extracting all zip files in {dir}{bcolors.ENDC}")
    
    except NotADirectoryError:
        print(f"{bcolors.FAIL}This filepath does not exist.{bcolors.ENDC}")
        

def main():
    cli.add_command(test_run)
    cli.add_command(scrape_yt)
    cli.add_command(decompress_yt)
    cli()
    
if __name__ == "__main__":
    exit(main())