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

output_data = "../original_data/trojmiasto/gda_original.json"
output_links = "../original_data/trojmiasto/gda_links.csv"
output_errors = "../original_data/trojmiasto/gda_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"

driver.get("https://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/wynajme-apartament-ogl65273392.html")
time.sleep(3)


# Step 2 - search for certain thing
cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
try:
    cookies.click()
    time.sleep(1)
except:
    pass

def get_from_trojmiasto_pl():
    
    def get_element_text(element):
        try:
            return element.text.strip()
        except AttributeError:
            return None
        
    time.sleep(2)
    listing_details = {}
    
    price_element = driver.find_element(By.CSS_SELECTOR, ".oglField--cena .oglField__value")
    listing_details['rent'] = get_element_text(price_element)

    year_element = driver.find_element(By.CSS_SELECTOR, ".oglField--rok_budowy .oglField__value")
    listing_details['build_year'] = get_element_text(year_element)

    level_element = driver.find_element(By.CSS_SELECTOR, ".oglField--pietro .oglField__value")
    listing_details['level'] = get_element_text(level_element)

    surface_element = driver.find_element(By.CSS_SELECTOR, "#show-powierzchnia .oglField__value")
    listing_details['surface'] = get_element_text(surface_element)

    heating_element = driver.find_element(By.CSS_SELECTOR, ".oglField--typ_ogrzewania .oglField__value")
    listing_details['heating'] = get_element_text(heating_element)

    floors_element = driver.find_element(By.CSS_SELECTOR, ".oglField--l_pieter .oglField__value")
    listing_details['floors_in_building'] = get_element_text(floors_element)

    description_element = driver.find_element(By.CSS_SELECTOR, ".oglField--array .oglField__value")
    listing_details['description'] = get_element_text(description_element)

    available_since_element = driver.find_element(By.CSS_SELECTOR, ".oglField--dostepne_od .oglField__value")
    listing_details['available_since'] = get_element_text(available_since_element)

    private_element = driver.find_element(By.CSS_SELECTOR, ".oglField--osoba_firma .oglField__value")
    listing_details['private_or_business'] = get_element_text(private_element)

    property_type_element = driver.find_element(By.CSS_SELECTOR, ".oglField--rodzaj_nieruchomosci .oglField__value")
    listing_details['property_type'] = get_element_text(property_type_element)

    address_element = driver.find_element(By.CSS_SELECTOR, ".oglField--address .oglField__name + a")
    listing_details['address'] = address_element.text.strip()

    additional_info_element = driver.find_elements(By.CSS_SELECTOR, ".oglFieldList__item span")
    additional_info = [info.text.strip() for info in additional_info_element]
    listing_details['additional_info'] = additional_info.text

    print(listing_details)
        
    
    
    # time.sleep(1)
    # # price of listing
    # price = driver.find_element(By.CSS_SELECTOR, "[class='oglDetailsMoney autolinkSafariFix']")
    # listing_details["rent"] = price.text
    
    # # rooms of listing
    # roooms = driver.find_element(By.XPATH, ".//div[@class='oglField__name'][text()='Liczba pokoi']/following-sibling::span[@class='oglField__value']")
    # listing_details["rooms"] = roooms.text
    
    # # level of listing
    # level = driver.find_element(By.XPATH, ".//div[@class='oglField__name'][text()='Piętro']/following-sibling::span[@class='oglField__value']")
    # listing_details["level"] = level.text
    
    # # build year of listing
    # build_year = driver.find_element(By.XPATH, ".//div[@class='oglField__name'][text()='Rok budowy']/following-sibling::span[@class='oglField__value']")
    # listing_details["build_year"] = build_year.text
    
    # # description of listing
    # description = driver.find_element(By.CLASS_NAME, "ogl__description")
    # listing_details["description"] = description.text
    
    # # print(listing_details)
    

    # # Find all key-value pairs using CSS selectors and iterate through them
    # details_list = driver.find_elements(By.CSS_SELECTOR, "class='oglDetails panel'")
    # print(len(details_list))
    # print(details_list)
    # time.sleep(6)
    # for detail in details_list:
    #     print(detail.text)
    #     time.sleep(2)
    #     key = detail.text.strip()
        
    #     # Use XPath to find the corresponding value based on the key
    #     value_element = detail.find_element(By.XPATH, "./following-sibling::span[@class='oglField__value']")
    #     value = value_element.text.strip()
        
    #     print(key, ":", value)
    # # location 
    # location = driver.find_element(By.CLASS_NAME, "css-1c0ed4l")
    # listing_details["location"] = location.text
    
    # # username 
    # username_attr = driver.find_element(By.CLASS_NAME, "css-1fp4ipz")
    # username_attr = username_attr.text.split("\n")

    # listing_details["username"] = username_attr[1]
    # listing_details["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
    # listing_details["last_activity"] = username_attr[3]    
    
    # # added date 
    # date_of_listing_add = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    # listing_details["add_date"] = date_of_listing_add.text.lstrip("Dodane")
    
    # # title
    # title = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    # listing_details["title"] = title.text
    
    # # link
    # listing_details["link"] = driver.current_url

    # # description
    # description = driver.find_element(By.CLASS_NAME, "css-1m8mzwg")
    # listing_details["description"] = description.text.lstrip("OPIS\n")
    
    # # other options 
    options = driver.find_elements(By.CLASS_NAME, "css-sfcl1s")
    for option in options:
        try:
            k, v = option.text.split(":")
            listing_details[k] = v
        except:
            listing_details[option.text] = "true"
            
    time.sleep(1)
    
    all_listings.append(listing_details)
    
    
get_from_trojmiasto_pl()