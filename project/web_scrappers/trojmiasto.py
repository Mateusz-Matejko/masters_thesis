import csv
import json
import pprint
import sys
import time

from bs4 import BeautifulSoup
import requests

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

def main():
    innitials()
    early_steps()
    time.sleep(1)
    all_links = get_all_links()
    save_collected_data(what="links")
    
    # get actuall data
    print(f"All links to proceed: {all_links}")
    counter = 0
    for link in all_links:
        counter += 1
        if counter % 50 == 0:
            print("I processed: {counter} offers!")
        try:
            # try to get data from olx site
            get_from_trojmiasto(site_url=link)
        except Exception as e:
            # if not, save what actually happend
            error_details = {
                            "url": link,
                            }
            errored_links.append(error_details)
        
        time.sleep(1)
        # wait and close new window
        
    save_collected_data()
    save_collected_data(what="errors")

def innitials():
    driver.get("https://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/mieszkanie/gdansk/ai,1100_.html")
    time.sleep(3)
        

def early_steps():
    # Step 2 - search for certain thing
    cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler")
    try:
        cookies.click()
        time.sleep(1)
    except:
        pass


def get_all_links():
    
    counter = 1
    while True:
        time.sleep(2)
        next_page = None
        
        try:
            if driver.find_element(By.CLASS_NAME, 'pages__controls__next'):
                next_page = driver.find_element(By.CLASS_NAME, 'pages__controls__next')
            else:
                next_page = None
                
        except Exception as e:
            pass

        # classify the link part of offers
        offers = driver.find_elements(By.CLASS_NAME, "list__item__picture")
        time.sleep(2)
        
        # find out the links
        links_from_current_site = []
        for offer in offers:
            try:
                link = offer.find_element(By.CLASS_NAME, "listItemFirstPhoto").get_attribute("href")
                if link.lstrip("hhtps://")[:3] != "ogl":
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

def get_from_trojmiasto(site_url):
    try:
        response = requests.get(site_url)
        response.raise_for_status()  # Raise an exception if status code is not 200
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
    except requests.RequestException as e:
        print(f"An error occurred while fetching the website: {e}")
        return None

    listing_details = {}

    listing_details['link'] = site_url
    
    try:
        price_element = soup.find('div', class_='oglField--cena')
        listing_details['rent'] = price_element.find('p', class_='oglDetailsMoney').text.strip()
    except AttributeError:
        listing_details['rent'] = 'N/A'

    try:
        description_element = soup.find('div', class_='ogl__description')
        listing_details['description'] = description_element.get_text(strip=True, separator=" ")
    except AttributeError:
        listing_details['description'] = 'N/A'

    try:
        address_element = soup.find('div', class_='oglField--address')
        listing_details['address'] = address_element.text.replace('Adres', '').strip()
    except AttributeError:
        listing_details['address'] = 'N/A'

    try:
        additional_info_element = soup.find('div', class_='oglField--array')
        additional_info = [info.text.strip() for info in additional_info_element.find_all('li', class_='oglFieldList__item')]
        listing_details['additional_info'] = additional_info
    except AttributeError:
        listing_details['additional_info'] = []

    try:
        elements = soup.find_all(class_='oglField')
        for element in elements:
            key_element = element.find('div', class_='oglField__name')
            value_element = element.find('span', class_='oglField__value')

            if key_element and value_element:
                key = key_element.text.strip()
                value = value_element.text.strip()
                listing_details[key] = value
    except AttributeError:
        pass
    
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
    print("Succes without failiure :)")
    sys.exit()
    

if __name__ == "__main__":
    main()