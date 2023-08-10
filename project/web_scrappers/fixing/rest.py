import csv
import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

driver = webdriver.Chrome()

all_listings = []
errored_links = []
all_links = set()

output_data = "../original_data/olx_gda_original.json"
output_links = "../original_data/olx_gda_original_links.csv"
output_errors = "../original_data/olx_gda_original_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"



def main():
    innitials()
    early_steps()
    
    all_links = get_all_links()
    save_collected_data(what="links")
    
    # get actuall data
    for link in all_links:
        # open new window        
        main_chrome_tab = driver.current_window_handle
        
        driver.switch_to.new_window()
        time.sleep(1)
        
        driver.get(link)
        time.sleep(2)
        
        try:
            get_from_olx()
        except Exception as e:
            error_details = {
                            "url": driver.current_url,
                            "exception": e 
                            }
            errored_links.append(error_details)
        
        time.sleep(1)
        driver.close()
        
        time.sleep(1)
        driver.switch_to.window(main_chrome_tab)


def get_data_of_listing():
    #click on certain offer
    time.sleep(1)
    try:
        get_from_olx()
    except Exception as e:
        error_details = {"url": driver.current_url,
                             "exception": e}
        errored_links.append(error_details)
    driver.quit()
    print("Succes without failiure :)")


def innitials():
    driver.get("https://olx.pl")
    time.sleep(2)
        

def early_steps():
    # Step 2 - search for certain thing
    cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    try:
        cookies.click()
        time.sleep(1)
    except:
        pass
    
    search = driver.find_element(By.NAME, "q")
    search.send_keys(phrase_to_search)
    time.sleep(2)

    # Chose category
    search_by_category = driver.find_element(By.CLASS_NAME, "c000")
    search_by_category.click()
    time.sleep(2)

    # Chose closer category
    renting_category = driver.find_element(By.CLASS_NAME, "css-1bdi9t1")
    renting_category.click()
    time.sleep(3)

    # Chose city
    city = driver.find_element(By.CLASS_NAME, "css-uvldze")
    city.click()
    time.sleep(1)
    city.send_keys(city_to_search)
    time.sleep(2)

    # submit city
    city_submit = driver.find_element(By.CLASS_NAME, "css-16tss5f")
    city_submit.click()
    time.sleep(1)

    # submit choice
    submit = driver.find_element(By.CLASS_NAME, "css-wqd0vz")
    submit.click()
    time.sleep(1)


def get_all_links():
    
    counter = 1
    while True:
        time.sleep(3)
        next_page = None
        
        try:
            if driver.find_element(By.CSS_SELECTOR, '[data-cy="pagination-forward"]'):
                next_page = driver.find_element(By.CSS_SELECTOR, '[data-cy="pagination-forward"]')
            else:
                next_page = None
                
        except Exception as e:
            pass

        # classify the link part of offers
        offers = driver.find_elements(By.CLASS_NAME, "css-1sw7q4x")
        time.sleep(2)
        
        # find out the links
        links_from_current_site = []
        for offer in offers:
            try:
                link = offer.find_element(By.CLASS_NAME, "css-rc5s2u").get_attribute("href")
                if link.lstrip("hhtps://www.")[:3] != "olx":
                    continue
                links_from_current_site.append(link)
                all_links.add(link)
            except:
                pass
        print(f"Links on site {counter}: {len(links_from_current_site)}")
        counter += 1

        if not links_from_current_site:
            input("No links got at current site: ")
        
        if next_page:
            next_page.click()

        else:
            break
            # Go to next page to collect links.

    return all_links


def current_site_operation():
    time.sleep(4)

    # next page button located
    next_page = driver.find_element(By.CSS_SELECTOR, '[data-cy="pagination-forward"]')
        
    time.sleep(3)
    
    # classify the link part of offers
    offers = driver.find_elements(By.CLASS_NAME, "css-1sw7q4x")
    
    
    time.sleep(2)

    
    links_from_current_site = []
    for offer in offers:
        try:
            link = offer.find_element(By.CLASS_NAME, "css-rc5s2u").get_attribute("href")
            if link.lstrip("hhtps://www.")[:3] != "olx":
                continue
            links_from_current_site.append(link)
            all_links.add(link)
        except:
            pass
    
    if not links_from_current_site:
        input("No links got at current site: ")
    
    
    iteration_and_window_handle(links_from_current_site)
    
    while True:
        try:
            next_page.click()
            time.sleep(3)
            current_site_operation()
        except Exception as e:
            print(f"Exception {e} occured!")
            save_collected_data()
            finish()
            break
    

def get_from_olx():
    listing_details = {}
    
    time.sleep(1)
    # price of listing
    price = driver.find_element(By.CLASS_NAME, "css-47bkj9")
    listing_details["rent"] = price.text
    
    # location 
    location = driver.find_element(By.CLASS_NAME, "css-1c0ed4l")
    listing_details["location"] = location.text
    
    # username 
    username_attr = driver.find_element(By.CLASS_NAME, "css-1fp4ipz")
    username_attr = username_attr.text.split("\n")

    listing_details["username"] = username_attr[1]
    listing_details["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
    listing_details["last_activity"] = username_attr[3]    
    
    # added date 
    date_of_listing_add = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing_details["add_date"] = date_of_listing_add.text.lstrip("Dodane")
    
    # title
    title = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing_details["title"] = title.text
    
    # link
    listing_details["link"] = driver.current_url

    # description
    description = driver.find_element(By.CLASS_NAME, "css-1m8mzwg")
    listing_details["description"] = description.text.lstrip("OPIS\n")
    
    # other options 
    options = driver.find_elements(By.CLASS_NAME, "css-sfcl1s")
    for option in options:
        try:
            k, v = option.text.split(":")
            listing_details[k] = v
        except:
            listing_details[option.text] = "true"
            
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

    
    if what == "erros":
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
    
##############################################################

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
driver.get("https://www.otodom.pl/pl/oferta/sloneczny-apartament-na-17-pietrze-morena-ID47vjR")
time.sleep(2)
# Step 2 - search for certain thing
cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
try:
    cookies.click()
    time.sleep(1)
except:
    pass


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


get_from_otodom()

##################################################

import csv
import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/pomorskie/gdansk/gdansk/gdansk")

time.sleep(2)
cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
try:
    cookies.click()
    time.sleep(1)
except:
    pass

all_links = []
links_from_current_site = []

# offers = driver.find_elements(By.CLASS_NAME, "css-iq9jxc e1n6ljqa1")

offer_list = driver.find_elements(By.CSS_SELECTOR, "[data-cy=listing-item]")


counter_of_failure = 0

driver.execute_script("window.scrollBy(0, 1000);")

time.sleep(5)

offer_list = driver.find_elements(By.CSS_SELECTOR, "a[data-cy=listing-item-link]")

print(f"Length of offers: {len(offer_list)}")

for offer in offer_list:
    try:
        link = offer.get_attribute("href")
        links_from_current_site.append(link)
        print(link)
        all_links.append(link)
    except:
        counter_of_failure += 1
        pass


if not links_from_current_site:
    input("No links got at current site: ")

print("Links correctly gotten:")
print(len(links_from_current_site))
print("Failures:")
print(counter_of_failure)

#############################################################


import pprint
import requests
from bs4 import BeautifulSoup
import time

def get_listing_details(url):
    listing_details = {}
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    price_element = soup.find('h2', class_= "css-5ufiv7 er34gjf0")
    price = price_element.text.strip()
    
    title_element = soup.find("h1", class_ = "css-bg3pmc er34gjf0")
    title = title_element.text.strip()
    
    name_element = soup.find("h4", class_= "css-1lcz6o7 er34gjf0")
    name = name_element.text.strip()
        
   # Find the location element with class "css-1c0ed4l"
    location_element = soup.select_one('span.css-1c0ed4l')

    # Extract the location text if the element is found, otherwise return "Location not found"
    location = location_element.text.strip() if location_element else "Location not found"

    # Print or use the location as needed
    print(location)
    
    input()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # Price of listing
    # price = soup.find("span", class_="css-47bkj9")
    # listing_details["rent"] = price.text if price else ""
    
    # # Location
    # location = soup.find("div", class_="css-1cju8pu er34gjf0")
    # listing_details["location"] = location.text if location else ""
    
    # # Username and other details
    # username_attr = soup.find("div", class_="css-1fp4ipz")
    # if username_attr:
    #     username_attr = username_attr.get_text("\n").split("\n")
    #     listing_details["username"] = username_attr[1]
    #     listing_details["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
    #     listing_details["last_activity"] = username_attr[3]
    
    # # Added date
    # date_of_listing_add = soup.find("span", class_="css-8mfr0h")
    # listing_details["add_date"] = date_of_listing_add.text.lstrip("Dodane") if date_of_listing_add else ""
    
    # # Title
    # title = soup.find("span", class_="css-8mfr0h")
    # listing_details["title"] = title.text if title else ""
    
    # # Link
    # listing_details["link"] = url
    
    # # Description
    # description = soup.find("div", class_="css-1m8mzwg")
    # listing_details["description"] = description.text.lstrip("Opis").replace("\n", '') if description else ""
    
    # # Other options
    # options = soup.find_all("div", class_="css-sfcl1s")
    # for option in options:
    #     try:
    #         k, v = option.text.split(":")
    #         listing_details[k] = v
    #     except ValueError:
    #         listing_details[option.text] = "true"
    
    return listing_details

url = "https://www.olx.pl/d/oferta/kawalerka-nowy-budownictwo-wolna-od-wrzesnia-CID3-IDWkhgl.html"  # Replace with the actual URL of the listing
listing_details = get_listing_details(url)

pprint.pprint(listing_details)


############################################################