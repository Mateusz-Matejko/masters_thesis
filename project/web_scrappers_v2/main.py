import logging
from gratka_scrapper import GratkaScraper
from olx_scrapper import OlxScrapper
from otodom_scrapper import OtodomScrapper
from trojmiasto_scrapper import TrojmiastoScraper

# Configure the logger
logging.basicConfig(filename='scraper.log', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    city = "krk"
    try:
        scrapper = TrojmiastoScraper(city)
        scrapper.main()
    except Exception as e:
        logging.error(f"Error collecting data from Otodom for {city}: {e}")

        # if city == "gda":
        #     try:
        #         trojmiasto_collector = TrojmiastoScraper(city)
        #         trojmiasto_collector.main()
        #     except Exception as e:
        #         logging.error(f"Error collecting data from Trojmiasto for {city}: {e}")
                
        # if city == "krk":
        #     try:
        #         olx_collector = OlxScrapper(city)
        #         olx_collector.main()
        #     except Exception as e:
        #         logging.error(f"Error collecting data from OLX for {city}: {e}")


if __name__ == "__main__":
    main()