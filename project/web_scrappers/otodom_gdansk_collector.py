import csv
import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()

all_listings = []
errored_links = []
all_links = []

output_data = "../original_data/otodom_gda_original.json"
output_links = "../original_data/otodom_gda_original_links.csv"
output_errors = "../original_data/otodom_gda_original_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"



def main():
    innitials()

    early_steps()
    # Quit the driver after the work is done :)
    current_site_operation()
    driver.quit()
    print("Succes without failiure :)")


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
    renting_category = driver.find_element(By.ID, "rentPopularLocationGdansk")
    time.sleep(1)
    renting_category.click()

    
def current_site_operation():
    time.sleep(4)
    
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)

    # next page button located
    next_page = driver.find_element(By.CSS_SELECTOR, ["data-cy=pagination.next-page"])
    time.sleep(2)
    
    # classify the link part of offers
    offer_list = driver.find_elements(By.CSS_SELECTOR, "[data-cy=listing-item]")
    time.sleep(2)
    
    
    links_from_current_site = []
    for offer in offer_list:
        link = offer.get_attribute("href")
        links_from_current_site.append(link)
        all_links.append(link)
    
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
        
def iteration_and_window_handle(links_from_current_site):
    for link in links_from_current_site:
        if link.lstrip("hhtps://www.")[:3] != "olx":
            continue
        # open new window
        time.sleep(1)
        main_chrome_tab = driver.current_window_handle
        driver.switch_to.new_window()
        time.sleep(1)
        driver.get(link)
        time.sleep(2)
        get_data_of_listing()
        time.sleep(1)
        driver.close()
        time.sleep(1)
        driver.switch_to.window(main_chrome_tab)
        time.sleep(1)


def get_data_of_listing():
    #click on certain offer
    time.sleep(1)
    try:
        get_from_olx()
    except Exception as e:
        error_details = {"url": driver.current_url,
                             "exception": e}
        errored_links.append(error_details)
    

def get_from_olx():
    listing_details = {}
        
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
    time.sleep(1)
    
    
    # added date 
    date_of_listing_add = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing_details["add_date"] = date_of_listing_add.text.lstrip("Dodane")
    
    # title
    title = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing_details["title"] = title.text
    
    # link
    listing_details["link"] = driver.current_url
    time.sleep(1)

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


def save_collected_data():
    # write out collected masterdata
    with open(output_data, "w") as collected_data_destination:
        json.dump(all_listings, collected_data_destination, indent=2)
    
    # write out collected all links
    with open(output_links, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in all_links:
            csv_writer.writerow(row)
    
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