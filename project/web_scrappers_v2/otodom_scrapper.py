import csv
import json
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from config import Config
from tqdm import tqdm

class OtodomScrapper:
    def __init__(self, city):
        self.config = Config()
        self.driver = self.config.get_driver()
        
        self.all_listings = []
        self.errored_links = []
        self.all_links = set()
        
        self.folder = self.config.folder
        self.portal = "otodom"
        self.city = city
        
        self.output_data = self.config.path_generator(self.folder, self.portal, self.city, "original", ending="json")
        self.output_links = self.config.path_generator(self.folder, self.portal, self.city, "links", ending="csv")
        self.output_errors = self.config.path_generator(self.folder, self.portal, self.city, "errors", ending="json")
        
        self.location_id = "rentPopularLocationGdansk" if self.city == "gda" else "rentPopularLocationKrakow"
        
    def main(self):
        try:
            print(f"Rozpoczynam pracę scrappera portalu {self.portal} dla miasta {self.city}")
            self.innitials()
            self.early_steps()
            self.all_links = self.get_all_links()
            self.save_collected_data(what="links")
        except Exception as e:
            print(e)
            input("Dupa")
            
        progress_bar = tqdm(total=len(self.all_links), unit="link", unit_scale=True)
        for counter, link in enumerate(self.all_links, 1):
            self.process_link(link)
            progress_bar.update(1)
            if counter % 50 == 0:
                self.save_collected_data()
        progress_bar.close()
        
        self.save_collected_data()
        self.save_collected_data(what="errors")
        self.finish()

    def innitials(self):
        self.driver.get("https://otodom.pl")
        time.sleep(5)

    def early_steps(self):
        cookies = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
        try:
            cookies.click()
            time.sleep(1)
        except:
            pass

        search_by_category = self.driver.find_element(By.ID, "rent")
        search_by_category.click()
        time.sleep(2)

        if self.location_id:
            renting_category = self.driver.find_element(By.ID, self.location_id)
            time.sleep(1)
            renting_category.click()
        else:
            input("No location_id... ")

    def get_all_links(self):
        counter = 1
        while True:
            try:
                time.sleep(2)
                next_page_button = self.driver.find_element(By.CSS_SELECTOR,
                                                            'button[aria-label="następna strona"][data-cy="pagination.next-page"]')
                is_disabled = next_page_button.get_attribute('disabled')
                time.sleep(1)
                self.driver.execute_script("window.scrollBy(0, 1000)")
                time.sleep(1)
                offer_list = self.driver.find_elements(By.CSS_SELECTOR, "a[data-cy=listing-item-link]")
                time.sleep(1)
                links_from_current_site = []

                for offer in offer_list:
                    try:
                        link = offer.get_attribute("href")
                        if link.lstrip("https://www.")[:3] != "oto":
                            continue
                        links_from_current_site.append(link)
                        self.all_links.add(link)
                    except:
                        pass

                print(f"Links on site {counter}: {len(links_from_current_site)}")
                counter += 1

                if not links_from_current_site:
                    input("No links got at the current site: ")

                if is_disabled:
                    break

                next_page_button.click()
                self.driver.implicitly_wait(3)

            except NoSuchElementException:
                print("No more pages to click.")
                break

        return self.all_links

    def process_link(self, link):
        main_chrome_tab = self.driver.current_window_handle
        self.driver.switch_to.new_window()
        time.sleep(1)
        self.driver.get(link)
        time.sleep(1)

        try:
            self.get_from_otodom()
        except Exception as e:
            error_details = {"url": self.driver.current_url}
            self.errored_links.append(error_details)

        self.driver.close()
        self.driver.switch_to.window(main_chrome_tab)

    def get_from_otodom(self):
        listing_details = {}
        listing_details['link'] = self.driver.current_url

        try:
            address_element = self.driver.find_element(By.XPATH, "//a[@aria-label='Adres']")
            listing_details['address'] = address_element.text

            title_element = self.driver.find_element(By.XPATH, "//h1[@data-cy='adPageAdTitle']")
            listing_details['title'] = title_element.text

            price_element = self.driver.find_element(By.XPATH, "//strong[@data-cy='adPageHeaderPrice']")
            listing_details['price'] = price_element.text
        except Exception as e:
            error_details = {"url": self.driver.current_url}
            self.errored_links.append(error_details)
            listing_details['address'] = None
            listing_details['title'] = None
            listing_details['price'] = None

        def extract_data(item_id):
            try:
                element = self.driver.find_element(By.XPATH, f'//*[@id="__next"]/main/div[2]/div[2]/div[1]/div/div[{item_id}]/div[2]/div')
                return element.text.strip()
            except:
                return None

        listing_details["surface"] = extract_data(1)
        listing_details['rent_extra'] = extract_data(2)
        listing_details['rooms'] = extract_data(3)
        listing_details['deposit'] = extract_data(4)
        listing_details['floor'] = extract_data(5)
        listing_details['building_type'] = extract_data(6)
        listing_details['avilable_since'] = extract_data(7)
        listing_details['outside_are'] = extract_data(8)
        time.sleep(1)

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
                with open(self.output_errors, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    for link in self.errored_links:
                        url = ''.join(link)
                        csv_writer.writerow([url])

    def finish(self):
        self.driver.quit()
        print("Success without failure :)")
        
        
def main():
    for town in ["gda", "krk"]:
        scrapper = OtodomScrapper(city=town)
        scrapper.main()
        time.sleep(10)
    
if __name__ == "__main__":
    main()