from gratka_scrapper import GratkaScraper
from olx_scrapper import OlxScrapper
from otodom_scrapper import OtodomScrapper
from trojmiasto_scrapper import TrojmiastoScraper

def main():
    pass

if __name__ == "__main__":
    cities = ["gda", "krk"]
    for city in cities:
        olx_collector = OlxScrapper(city)
        olx_collector.main()
        
        gratka_collector = GratkaScraper(city)
        gratka_collector.main()
        
        otodom_collector = OtodomScrapper(city)
        otodom_collector.main()
        
        if city == "gda":
            trojmiasto_collector = TrojmiastoScraper(city)
            trojmiasto_collector.main()