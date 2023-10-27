import logging
from gratka_scrapper import main as gratka
from olx_scrapper import main as olx
from otodom_scrapper import main as otodom
from trojmiasto_scrapper import main as trojmiasto

# Configure the logger
logging.basicConfig(filename='scraper.log', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    for scirpt in [otodom]:
        try:
            scirpt()
        except Exception as e:
            logging.info(e)

if __name__ == "__main__":
    main()