import csv
import json
import time
import sys

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from config import Config
from tqdm import tqdm

config = Config()

class GratkaScraper:
    def __init__(self, city):
        self.driver = webdriver.Chrome()
        
        self.all_listings = []
        self.errored_links = []
        self.all_links = set()
        
        self.folder = config.folder
        self.portal = "gratka"
        self.city = city
        
        self.output_data = config.path_generator(self.folder, self.portal, self.city, "original", ending="json")
        self.output_links = config.path_generator(self.folder, self.portal, self.city, "links", ending="csv")
        self.output_errors = config.path_generator(self.folder, self.portal, self.city, "errors", ending="json")
        
        self.city_to_search = "gdansk" if self.city == "gda" else "krakow"

    def main(self):
        print(f"Rozpoczynam pracę scrappera portalu {self.portal} dla miasta {self.city}")
        
        self.innitials()
        self.early_steps()
        time.sleep(1)
        self.all_links = self.get_all_links()
        self.save_collected_data(what="links")

        progress_bar = tqdm(total=len(self.all_links), unit="link", unit_scale=True)
        for counter, link in enumerate(self.all_links, 1):
            try:
                self.process_link(link)
            except Exception as e:
                # If not, save what actually happened
                error_details = {
                    "url": link,
                }
                self.errored_links.append(error_details)
            if counter % 50 == 0:
                self.save_collected_data()
            progress_bar.update(1)
        progress_bar.close()
        
        self.save_collected_data()
        self.save_collected_data(what="errors")
        self.finish()

    def innitials(self):
        self.driver.get(f"https://gratka.pl/nieruchomosci/mieszkania/{self.city_to_search}/wynajem")
        time.sleep(2)

    def early_steps(self):
        # Step 2 - search for a certain thing
        cookies = self.driver.find_element(By.CLASS_NAME, "cmp-intro_acceptAll")
        try:
            cookies.click()
            time.sleep(1)
        except NoSuchElementException:
            pass

    def get_all_links(self):
        
        counter = 1
        while True:
            time.sleep(2)
            next_page = None
            
            try:
                if self.driver.find_element(By.CLASS_NAME, "pagination__nextPage").get_attribute("href"):
                    next_page = self.driver.find_element(By.CLASS_NAME, "pagination__nextPage").get_attribute("href")
                else:
                    next_page = None
                    
            except Exception as e:
                pass

            # classify the link part of offers
            offers = self.driver.find_elements(By.CLASS_NAME, "listing__teaserWrapper")
            time.sleep(2)
            
            # find out the links
            links_from_current_site = []
            for offer in offers:
                try:
                    link = offer.find_element(By.CLASS_NAME, "teaserLink").get_attribute("href")
                    if link.lstrip("hhtps://")[:3] != "gra":
                        continue
                    links_from_current_site.append(link)
                    self.all_links.add(link)
                except:
                    pass
            print(f"Links on site {counter}: {len(links_from_current_site)}")
            counter += 1

            if not links_from_current_site:
                input("No links got at current site: ")
            
            if next_page:
                self.driver.get(next_page)
                time.sleep(2)
                
            else:
                print("no more links to go to.... /n im leaving this loop")
                break
                # Go to next page to collect links.
        return self.all_links

    def process_link(self, link):
        try:
            response = requests.get(link)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
        except requests.RequestException as e:
            print(f"An error occurred while fetching the website: {e}")
            return None

        listing_details = {}
        listing_details['link'] = link

        try:
            price_element = soup.find('div', class_='priceInfo')
            listing_details['rent'] = price_element.find('span', class_='priceInfo__value').text.replace("\n", "").replace("zł/miesiąc", "").strip()
        except AttributeError:
            listing_details['rent'] = 'N/A'

        try:
            description_element = soup.find('div', class_='description__rolled')
            listing_details['description'] = description_element.get_text(strip=True, separator=" ")
        except AttributeError:
            listing_details['description'] = 'N/A'

        try:
            address_element = soup.find('span', class_='offerLocation')
            listing_details['address'] = " ".join(address_element.text.replace("\n", "").strip().replace(",", "").split())
        except AttributeError:
            listing_details['address'] = 'N/A'

        try:
            title_element = soup.find('h1', class_='sticker__title')
            listing_details['title'] = title_element.text.replace("\n", "").replace(",", "").strip()
        except AttributeError:
            listing_details['title'] = 'N/A'

        try:
            additional_info_element = soup.find('div', class_='oglField--array')
            additional_info = [info.text.strip() for info in additional_info_element.find_all('li', class_='oglFieldList__item')]
            listing_details['additional_info'] = additional_info
        except AttributeError:
            listing_details['additional_info'] = []

        try:
            parameters_div = soup.find('div', class_='parameters')
            parameters_deeper = parameters_div.find('ul', class_='parameters__singleParameters')

            for element in parameters_deeper:
                try:
                    key = element.find('span').text
                    if element.find("b", class_='parameters__value').text.replace("\n", "").strip():
                        val = element.find("b", class_='parameters__value').text.replace("\n", "").strip()
                    else:
                        val = element.find("div", class_='parameters__value').text.replace("\n", "").strip()
                    if key and val:
                        listing_details[key] = val
                    elif key:
                        listing_details[key] = "N/A"
                except:
                    pass

                try:
                    key = element.find('span').text
                    val = element.find("div", class_='parameters__value').text.replace("\n", "").strip()
                    listing_details[key] = val
                    if key and val:
                        listing_details[key] = val
                except:
                    pass
        except AttributeError:
            pass

        self.all_listings.append(listing_details)

    def save_collected_data(self, what="data"):
        if what == "data":
            with open(self.output_data, "w") as collected_data_destination:
                json.dump(self.all_listings, collected_data_destination, indent=2)

        if what == "links":
            with open(self.output_links, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                for link in self.all_links:
                    url = ''.join(link)
                    csv_writer.writerow([url])

        if what == "errors":
            if self.errored_links:
                with open(self.output_errors, "w") as occurred_errors_destination:
                    json.dump(self.errored_links, occurred_errors_destination, indent=2)

    def finish(self):
        self.driver.quit()
        print("Success without failure :)")


def main():
    for town in ["gda", "krk"]:
        scrapper = GratkaScraper(city=town)
        scrapper.main()
        time.sleep(10)
    
if __name__ == "__main__":
    main()
