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

        scraper = WebScraper("http://netsg.cs.sfu.ca/youtubedata/")
        scraper.scrape()
    except NotADirectoryError:
        print(f"{bcolors.FAIL}This filepath does not exist.{bcolors.ENDC}")

def main():
    cli.add_command(test_run)
    cli.add_command(scrape_yt)
    cli()
    
if __name__ == "__main__":
    exit(main())