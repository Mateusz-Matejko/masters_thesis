import json
import pprint
import sys
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By


def current_site_operation():
    # waiting for site to load up
    time.sleep(5)

    next_page = driver.find_element(By.CLASS_NAME, "css-pyu9k9")   
    # next_page = driver.find_element(By.CLASS_NAME, "pagination-list")\
    #     .find_element(By.CSS_SELECTOR, 'a[data-cy="pagination-forward"]')
        

    time.sleep(3)
    
    # classify the link part of offers
    offers = driver.find_elements(By.CLASS_NAME, "css-1sw7q4x")
    time.sleep(3)
    
    print(offers)
    input("Offers printed")
    
    links_from_current_site = []
    for offer in offers:
        try:
            link = offer.find_element(By.CLASS_NAME, "css-rc5s2u").get_attribute("href")
            links_from_current_site.append(link)
        except:
            pass
    
    print(links_from_current_site)
    input("It should actually work!")
    
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
        # open new window
        time.sleep(2)
        current_window = driver.current_window_handle
        driver.switch_to.new_window()
        time.sleep(2)
        driver.get(link)
        time.sleep(2)
        get_data_of_listing()
        # wait for site to close
        time.sleep(2)
        driver.close()
        time.sleep(2)
        driver.switch_to.window(current_window)
        time.sleep(2)


def get_data_of_listing():
    #click on certain offer
    time.sleep(3)
    try:
        get_from_olx()
    except:
        pass
    

def get_from_olx():
    listing = {}
        
    # price of listing
    price = driver.find_element(By.CLASS_NAME, "css-47bkj9")
    listing["rent"] = price.text
    
    # location 
    location = driver.find_element(By.CLASS_NAME, "css-1c0ed4l")
    listing["location"] = location.text
    
    # username 
    username_attr = driver.find_element(By.CLASS_NAME, "css-1fp4ipz")
    username_attr = username_attr.text.split("\n")

    listing["username"] = username_attr[1]
    listing["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
    listing["last_activity"] = username_attr[3]
    time.sleep(1)
    
    
    # added date 
    date_of_listing_add = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing["add_date"] = date_of_listing_add.text.lstrip("Dodane")
    
    # title
    title = driver.find_element(By.CLASS_NAME, "css-8mfr0h")
    listing["title"] = title.text
    
    # link
    listing["link"] = driver.current_url
    time.sleep(1)

    # description
    description = driver.find_element(By.CLASS_NAME, "css-1m8mzwg")
    listing["description"] = description.text.lstrip("OPIS\n")
    
    # other options 
    options = driver.find_elements(By.CLASS_NAME, "css-sfcl1s")
    for option in options:
        try:
            k, v = option.text.split(":")
            listing[k] = v
        except:
            listing[option.text] = "true"
            
    time.sleep(1)
    
    pprint.pprint(listing)
    time.sleep(2)
    

def save_collected_data():
    with open("asdasdsaffsfgasga.json", "w") as json_file:
        json.dump(listings, json_file, indent=2)


def finish():
    question = input("Quit? ").upper()
    if question == "Y":
        driver.quit()
    data_finish = datetime.now()
    time = data_finish - data_start
    print(f"[{time.seconds}s]")
    sys.exit()
    

driver = webdriver.Chrome()
listings = []

# driver.get("https://www.olx.pl/nieruchomosci/mieszkania/wynajem/gdansk/q-MIeszkania-na-wynajem/")
driver.get("https://www.olx.pl/d/oferta/wynajem-mieszkania-CID3-IDWdH3F.html")
time.sleep(2)

cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
try:
    cookies.click()
    time.sleep(1)
except:
    pass

get_from_olx()

input("zgarnij csy xd")

