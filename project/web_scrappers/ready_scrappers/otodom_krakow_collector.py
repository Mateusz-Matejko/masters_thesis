import csv
import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

all_listings = []
errored_links = []
all_links = set()

output_data = "../original_data/otodo/gda_original.json"
output_links = "../original_data/otodom/gda_links.csv"
output_errors = "../original_data/otodom/gda_errors.json"

def main():
    innitials()
    early_steps()
    
    all_links = get_all_links()
    save_collected_data(what="links")
    
    print("without error got here")
    input("...:")
    # get actuall data
    for link in all_links:
        # open new window        
        main_chrome_tab = driver.current_window_handle
        
        driver.switch_to.new_window()
        time.sleep(1)
        
        driver.get(link)
        time.sleep(2)
        
        try:
            # try to get data from olx site
            get_from_otodom()
        except Exception as e:
            # if not, save what actually happend
            error_details = {
                            "url": driver.current_url,
                            "exception": e 
                            }
            errored_links.append(error_details)
        
        # wait and close new window
        time.sleep(1)
        driver.close()
        
        driver.switch_to.window(main_chrome_tab)
        
    save_collected_data()
    save_collected_data(what="errors")

def innitials():
    driver.get("https://otodom.pl")
    time.sleep(2)
        

def early_steps():
    # Step 2 - search for certain thing
    cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    try:
        cookies.click()
        time.sleep(1)
    except:
        pass

    # Chose rent as category
    search_by_category = driver.find_element(By.ID, "rent")
    search_by_category.click()
    time.sleep(2)

    # Chose confirm city
    renting_category = driver.find_element(By.ID, "rentPopularLocationKrakow")
    time.sleep(1)
    renting_category.click()


def get_all_links():
    
    counter = 1
    
    while True:
        try:
            time.sleep(1)
            # Find the "Next Page" button using the 'data-cy' attribute
            next_page_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="następna strona"][data-cy="pagination.next-page"]')
            is_disabled = next_page_button.get_attribute('disabled')

            time.sleep(1)
            driver.execute_script("window.scrollBy(0, 1000);")
            
            time.sleep(1)
            offer_list = driver.find_elements(By.CSS_SELECTOR, "a[data-cy=listing-item-link]")

            time.sleep(1)
            # find out the links
            links_from_current_site = []
            
            for offer in offer_list:
                try:
                    link = offer.get_attribute("href")
                    if link.lstrip("hhtps://www.")[:3] != "oto":
                        continue
                    links_from_current_site.append(link)
                    all_links.add(link)
                except:
                    pass
            print(f"Links on site {counter}: {len(links_from_current_site)}")
            counter += 1

            if not links_from_current_site:
                input("No links got at current site: ")

            if is_disabled:
                break
            
            # Click the "Next Page" button
            next_page_button.click()
            driver.implicitly_wait(3)

        except NoSuchElementException:
            # If the button is not found, break the loop as there are no more pages
            print("No more pages to click.")
            break

    return all_links


def get_from_otodom():
    listing_details = {}
    
    listing_details['link'] = driver.current_url

    try:
        # Find the address element
        address_element = driver.find_element(By.XPATH, "//div[@class='css-gx6go5 efcnut312']//a[@aria-label='Adres']")
        listing_details['address'] = address_element.text
        print("Address:", address_element.text)

        # Find the title element
        title_element = driver.find_element(By.XPATH, "//h1[@data-cy='adPageAdTitle']")
        listing_details['title'] = title_element.text
        print("Title:", title_element.text)

        # Find the price element
        price_element = driver.find_element(By.XPATH, "//strong[@data-cy='adPageHeaderPrice']")
        listing_details['price'] = price_element.text
        print("Price:", price_element.text)

    except Exception as e:
        error_details = {
                "url": driver.current_url,
                "exception": e 
                }
        errored_links.append(error_details)
        
        listing_details['address'] = None
        listing_details['title'] = None
        listing_details['price'] = None


    def extract_data(label):
        try:
            element = driver.find_element(By.XPATH, f"//div[@aria-label='{label}']//div[@class='css-1wi2w6s enb64yk4']")
            return element.text
        except:
            return None
    
    listing_details["surface"] = extract_data('Powierzchnia')
    
    listing_details['rent_extra'] = extract_data('Czynsz')
    
    listing_details['rooms'] = extract_data('Liczba pokoi')
    
    listing_details['deposit'] = extract_data('Kaucja')
    
    listing_details['floor'] = extract_data('Piętro')
    
    listing_details['building_type'] = extract_data('Rodzaj zabudowy')
    
    listing_details['avilable_since'] = extract_data('Dostępne od')
    
    listing_details['outside_are'] = extract_data('Balkon / ogród / taras')
    
    time.sleep(1)
    
    all_listings.append(listing_details)

def save_collected_data(what="data"):
    
    if what == "data":
    # write out collected masterdata
        with open(output_data, "w") as collected_data_destination:
            json.dump(all_listings, collected_data_destination, indent=2)
    
    
    if what == "links":
    # Write out collected all links
        with open(output_links, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for link in all_links:
                # Join the characters of the link to form a single URL string
                url = ''.join(link)
                csv_writer.writerow([url])

    
    if what == "errors":
    # write out errors if ocured
        if errored_links:
            with open(output_errors, "w") as occured_errors_destination:
                json.dump(all_listings, occured_errors_destination, indent=2)


def finish():
    driver.quit()
    print("Succes without failiure :)")
    sys.exit()
    

if __name__ == "__main__":
    main()