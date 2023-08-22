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

output_data = "../original_data/olx/gda_original.json"
output_links = "../original_data/olx/gda_links.csv"
output_errors = "../original_data/olx/gda_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"


driver.get("https://www.olx.pl/d/oferta/kawalerka-nowe-budownictwo-blisko-gum-i-politechniki-CID3-IDWNolH.html")
time.sleep(2)

cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
try:
    cookies.click()
    time.sleep(1)
except:
    pass
    
    
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
print(listing_details)
        
time.sleep(1)

all_listings.append(listing_details)

with open("TESTSAVE.json", "w") as collected_data_destination:
    json.dump(all_listings, collected_data_destination, indent=2)