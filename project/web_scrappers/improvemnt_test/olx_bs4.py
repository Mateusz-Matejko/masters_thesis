import csv
import json
import pprint
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# path = "../../related/chromedriver"
# driver = webdriver.Chrome(path)
# driver = webdriver.Chrome()

all_listings = []
errored_links = []
all_links = set()

city = "gda"

output_data = f"{city}_original.json"
output_links = f"{city}_links.csv"
output_errors = f"{city}_errors.json"

phrase_to_search = "Mieszkania na wynajem"
city_to_search = "Gdańsk"

def main():
    # innitials()
    # early_steps()
    
    # all_links = get_all_links()
    # save_collected_data(what="links")
        
    # time.sleep(3)
    all_links = [
        "https://www.olx.pl/d/oferta/apartament-na-wynajem-w-centrum-gdanska-dlugoterminowo-na-miesiac-CID3-IDVF5p1.html",
        # "https://www.olx.pl/d/oferta/mieszkanie-2-pokojowe-do-wynajecia-gdansk-zabianka-CID3-IDIwZAJ.html"
    ]
    for link in all_links:
        get_from_olx(link)

        time.sleep(1)
        
        
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
    

def get_from_olx(link):
    listing_details = {}

    try:
        response = requests.get(link)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
    except requests.RequestException as e:
        print(f"An error occurred while fetching the website: {e}")
        return None

    listing_details['link'] = link

    # add date
    date_element = soup.find('span', {'data-cy': 'ad-posted-at'})
    if date_element:
        date = date_element.text.strip()
        listing_details["add_date"] = date
    else:
        listing_details["add_date"] = None
        
    # title
    title_element = soup.find('h1', {'data-cy': 'ad_title'})
    if title_element:
        title = title_element.text.strip()
        listing_details["title"] = title
    else:
        listing_details["title"] = None

    # rent
    price_element = soup.find('h3', class_='css-1twl9tf')
    if price_element:
        price = price_element.text.strip()
        listing_details["rent"] = price
    else:
        listing_details["rent"] = None
    
    location_element = soup.find("p", class_="css-1cju8pu er34gjf0")
    if location_element:
        location_text = location_element.get_text(strip=True)
        print("Lokalizacja:", location_text)
    else:
        print("Brak informacji o lokalizacji")
        input("FAIL")


    location_element = soup.find_all(class_="css-16sja3n")
    if location_element:
        print(location_element)
        input("DUPAGIGANT")
        location_text = location_element.get_text(strip=True)
        print("Lokalizacja:", location_text)
    else:
        print("Brak informacji o lokalizacji")
        input("FAIL")
        
    pprint.pprint(listing_details)
    input("....")

    username_element = soup.find('span', class_='css-1fp4ipz')
    if username_element:
        username_attr = username_element.text.split("\n")
        listing_details['username'] = username_attr[1]
        listing_details['on_olx_since'] = username_attr[2].lstrip("Na OLX od ")
        listing_details['last_activity'] = username_attr[3]
    else:
        listing_details['username'] = 'N/A'
        listing_details['on_olx_since'] = 'N/A'
        listing_details['last_activity'] = 'N/A'

    title_element = soup.find_all('div', class_='css-z799oh')
    if title_element:
        listing_details['add_date'] = title_element[0].text.lstrip("Dodane")
        listing_details['title'] = title_element[1].text.strip()
    else:
        listing_details['add_date'] = 'N/A'
        listing_details['title'] = 'N/A'

    description_element = soup.find('div', class_='css-1m8mzwg')
    if description_element:
        listing_details['description'] = description_element.text.lstrip("OPIS")
    else:
        listing_details['description'] = 'N/A'

    options_element = soup.find('div', class_='css-sfcl1s')
    if options_element:
        option_list = options_element.text.split("\n")
        for option in option_list:
            try:
                k, v = option.split(":")
                listing_details[k] = v
            except ValueError:
                listing_details[option] = True
            except:
                pass
    else:
        listing_details['options'] = 'N/A'


    pprint.pprint(listing_details)
    input("Just printed listing details")
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