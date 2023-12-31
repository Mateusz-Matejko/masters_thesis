import csv
import json
import pprint
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import Config
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OlxScrapper:
    def __init__(self, city):
        self.config = Config()
        self.driver = self.config.get_driver()
        
        self.all_listings = []
        self.errored_links = []
        self.all_links = set()
        
        self.folder = self.config.folder
        self.portal = "olx"
        self.city = city
        
        self.output_data = self.config.path_generator(self.folder, self.portal, self.city, "original", ending="json")
        self.output_links = self.config.path_generator(self.folder, self.portal, self.city, "links", ending="csv")
        self.output_errors = self.config.path_generator(self.folder, self.portal, self.city, "errors", ending="json")
        
        self.phrase_to_search = "Mieszkania na wynajem"
        self.city_to_search = "Gdańsk" if self.city == "gda" else "Kraków"

    def main(self):
        print(f"Rozpoczynam pracę scrappera portalu {self.portal} dla miasta {self.city}")
        
        self.innitials()
        self.early_steps()
        time.sleep(1)
        self.get_all_links()
        self.save_collected_data(what="links")
        
        progress_bar = tqdm(total=len(self.all_links), unit="link", unit_scale=True)
        for counter, link in enumerate(self.all_links, 1):
            try:
                self.process_link(link)
            except Exception as e:
                # If not, save what actually happened
                error_details = {
                    "url": link,
                    "excpetion": str(e)
                }
                self.errored_links.append(error_details)
            if counter % 50 == 0:
                self.save_collected_data()
            progress_bar.update(1)
        progress_bar.close()
        
        self.save_collected_data()
        self.save_collected_data(what="errors")
        self.finish()
        
    def process_link(self, link):

        main_chrome_tab = self.driver.current_window_handle
        self.driver.switch_to.new_window()
        time.sleep(1)
        self.driver.get(link)
        time.sleep(2)
        self.get_from_olx()
        time.sleep(1)
        self.driver.close()
        self.driver.switch_to.window(main_chrome_tab)

    def innitials(self):
        self.driver.get("https://olx.pl")
        time.sleep(5)
        cookies = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
        time.sleep(2)
        try:
            cookies.click()
            time.sleep(1)
        except:
            pass

    def early_steps(self):
        search = self.driver.find_element(By.ID, "search")
        search.send_keys(self.phrase_to_search)
        time.sleep(2)
        search.click()
        time.sleep(1)
        search_by_category = self.driver.find_element(By.XPATH, '//*[@id="searchmain-container"]/div[1]/div/div/div/form/div/div[1]/div/div/div[2]/div/div[1]')
        search_by_category.click()
        time.sleep(2)
        city = self.driver.find_element(By.ID, 'location-input')
        city.click()
        time.sleep(1)
        city.send_keys(self.city_to_search)
        time.sleep(2)
        city_submit = self.driver.find_element(By.CLASS_NAME, "css-16tss5f")
        city_submit.click()
        time.sleep(1)
        submit = self.driver.find_element(By.CLASS_NAME, "css-wqd0vz")
        submit.click()
        time.sleep(1)

    def get_all_links(self):
        counter = 1
        while True:
            time.sleep(3)
            next_page = None
            try:
                if self.driver.find_element(By.CSS_SELECTOR, '[data-cy="pagination-forward"]'):
                    next_page = self.driver.find_element(By.CSS_SELECTOR, '[data-cy="pagination-forward"]')
                else:
                    next_page = None
            except Exception as e:
                pass

            offers = self.driver.find_elements(By.CLASS_NAME, "css-1sw7q4x")
            time.sleep(2)

            links_from_current_site = []
            for offer in offers:
                try:
                    link = offer.find_element(By.CLASS_NAME, "css-rc5s2u").get_attribute("href")
                    if link.lstrip("hhtps://www.")[:3] != "olx":
                        continue
                    links_from_current_site.append(link)
                    self.all_links.add(link)
                except:
                    pass
            print(f"Links on site {counter}: {len(links_from_current_site)}")
            counter += 1

            if not links_from_current_site:
                print("0 links got at current site: ")

            if next_page:
                next_page.click()
            else:
                break

        return self.all_links

    def get_from_olx(self):
        listing_details = {}
        time.sleep(1)
        listing_details["link"] = self.driver.current_url

        if self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[3]'):
            price = self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[3]')
            listing_details["rent"] = price.text.strip()

        if self.driver.find_elements(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[2]/div[2]/div/section/div[1]/div/p[1]'):
            locations = self.driver.find_element(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[2]/div[2]/div/section/div[1]/div/p[1]')
            listing_details["location"] = locations.text.strip()

        if self.driver.find_elements(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[2]/h4'):
            title = self.driver.find_element(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[2]/h4')
            listing_details["title"] = title.text.strip()

        if self.driver.find_elements(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[1]/span/span'):
            add_date = self.driver.find_element(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[1]/span/span')
            listing_details["add_date"] = add_date.text.strip()

        if self.driver.find_elements(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[8]/div'):
            description = self.driver.find_element(By.XPATH,'//*[@id="mainContent"]/div[2]/div[3]/div[1]/div[2]/div[8]/div')
            listing_details["description"] = description.text.strip()

        options_element = self.driver.find_element(By.CLASS_NAME, "css-sfcl1s")
        option_list = options_element.text.split("\n")
        for option in option_list:
            try:
                k, v = option.split(":")
                listing_details[k] = v
            except ValueError:
                listing_details[option] = True
            except:
                pass

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
                with open(self.output_errors, "w") as occured_errors_destination:
                    json.dump(self.errored_links, occured_errors_destination, indent=2)

    def finish(self):
        self.driver.quit()
        print("Success without failure :)")
        
def main():
    for town in ["krk", "gda"]:
        scrapper = OlxScrapper(city=town)
        scrapper.main()
        scrapper.finish()
        time.sleep(10)
    
if __name__ == "__main__":
    main()

