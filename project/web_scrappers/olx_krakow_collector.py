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

folder = "collected_09_19"
portal = "olx"
city = "krk"

output_data = f"../original_data/{folder}/{portal}/{city}_original.json"
output_links = f"../original_data/{folder}/{portal}/{city}_links.csv"
output_errors = f"../original_data/{folder}/{portal}/{city}_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Kraków"

def main():
    innitials()
    early_steps()
    
    all_links = get_all_links()
    save_collected_data(what="links")
    
    # get actuall data
    print(f"To jest ilość linków: {len(all_links)}")
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
                            }
            errored_links.append(error_details)
        
        time.sleep(1)
        driver.close()
        
        driver.switch_to.window(main_chrome_tab)
        
    save_collected_data()
    save_collected_data(what="errors")
    print("Data Collected Correctly")


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