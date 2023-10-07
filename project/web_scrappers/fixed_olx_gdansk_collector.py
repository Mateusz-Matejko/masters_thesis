import csv
import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# path = "../../related/chromedriver"
# driver = webdriver.Chrome(path)
driver = webdriver.Chrome()

all_listings = []
errored_links = []
all_links = set()

folder = "collected_10_04"
portal = "olx"
city = "gda"

output_data = f"../original_data/{folder}/{portal}/{city}_original.json"
output_links = f"../original_data/{folder}/{portal}/{city}_links.csv"
output_errors = f"../original_data/{folder}/{portal}/{city}_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"

def main():
    innitials()
    # early_steps()
    
    # all_links = get_all_links()
    # save_collected_data(what="links")
        
    time.sleep(3)
    all_links = [
        "https://www.olx.pl/d/oferta/apartament-na-wynajem-w-centrum-gdanska-dlugoterminowo-na-miesiac-CID3-IDVF5p1.html",
        # "https://www.olx.pl/d/oferta/mieszkanie-2-pokojowe-do-wynajecia-gdansk-zabianka-CID3-IDIwZAJ.html"
    ]
    for link in all_links:
        # open new window        
        main_chrome_tab = driver.current_window_handle
        
        driver.switch_to.new_window()
        time.sleep(1)
        
        driver.get(link)
        time.sleep(2)
        
        get_from_olx()

        time.sleep(1)
        driver.close()
        
        driver.switch_to.window(main_chrome_tab)
        
    save_collected_data()
    save_collected_data(what="errors")
    print("Program work finished")


def get_data_of_listing():
    #click on certain offer
    time.sleep(1)
    get_from_olx()
    driver.quit()
    print("Succes without failiure :)")


def innitials():
    driver.get("https://olx.pl")
    time.sleep(2)
    
    cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    try:
        cookies.click()
        time.sleep(1)
    except:
        pass

def early_steps():
    # Step 2 - search for certain thing
    
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
    

def get_from_olx():
    listing_details = {}
    
    time.sleep(1)
    
    # link
    listing_details["link"] = driver.current_url
    
    # price of listing
    if driver.find_element(By.CLASS_NAME, "css-2xjd3c"):
        price = driver.find_element(By.CLASS_NAME, "css-2xjd3c")
        listing_details["rent"] = price.text
    
    # location 
    if driver.find_elements(By.CLASS_NAME, "css-16sja3n"):
        locations = driver.find_element(By.CLASS_NAME, "css-16sja3n")
        listing_details["location"] = locations.text

    # username 
    if driver.find_element(By.CLASS_NAME, "css-1fp4ipz"):
        username_attr = driver.find_element(By.CLASS_NAME, "css-1fp4ipz")
        username_attr = username_attr.text.split("\n")
        listing_details["username"] = username_attr[1]
        listing_details["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
        listing_details["last_activity"] = username_attr[3]    
    
    # title
    if driver.find_elements(By.CLASS_NAME, "css-z799oh"):
        title = driver.find_elements(By.CLASS_NAME, "css-z799oh")
        listing_details["add_date"] = title[0].text.lstrip("Dodane")
        listing_details["title"] = title[1].text
    
    # description
    if driver.find_element(By.CLASS_NAME, "css-1m8mzwg"):
        description = driver.find_element(By.CLASS_NAME, "css-1m8mzwg")
        listing_details["description"] = description.text.lstrip("OPIS\n")

    # other options
    options_element = driver.find_element(By.CLASS_NAME, "css-sfcl1s")
    option_list = options_element.text.split("\n")
    for option in option_list:
        try:
            k, v = option.split(":")
            listing_details[k] = v
        except ValueError:
            listing_details[option] = True  # Jeśli nie można podzielić na klucz i wartość, ustaw wartość na True
        except:
            pass
            
    time.sleep(1)
    
    pprint.pprint(listing_details)
    input("listing details here...")
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
                json.dump(errored_links, occured_errors_destination, indent=2)


def finish():
    driver.quit()
    print("Succes without failiure :)")
    sys.exit()
    

if __name__ == "__main__":
    main()