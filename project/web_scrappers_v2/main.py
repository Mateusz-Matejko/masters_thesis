import logging
from gratka_scrapper import main as gratka
from olx_scrapper import main as olx
from otodom_scrapper import main as otodom
from trojmiasto_scrapper import main as trojmiasto

def main():
    for scirpt in [gratka, olx, otodom, trojmiasto]:
        try:
            scirpt()
        except Exception as e:
            logging.info(e)

if __name__ == "__main__":
    main()