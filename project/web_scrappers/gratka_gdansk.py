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

folder = "collected_09_19"
portal = "gratka"
city = "gda"

output_data = f"../original_data/{folder}/{portal}/{city}_original.json"
output_links = f"../original_data/{folder}/{portal}/{city}_links.csv"
output_errors = f"../original_data/{folder}/{portal}/{city}_errors.json"

def main():
    innitials()
    early_steps()
    time.sleep(1)
    all_links = get_all_links()
    save_collected_data(what="links")
    
    # get actuall data
    counter = 0
    for link in all_links:
        counter += 1
        if counter % 50 == 0:
            print(f"I processed: {counter} offers!")
            save_collected_data()
        try:
            # try to get data from olx site
            get_from_gratka(site_url=link)
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
    driver.get("https://gratka.pl/nieruchomosci/mieszkania/gdansk/wynajem")
    time.sleep(2)
        

def early_steps():
    # Step 2 - search for certain thing
    cookies = driver.find_element(By.CLASS_NAME, "cmp-intro_acceptAll")
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
            if driver.find_element(By.CLASS_NAME, "pagination__nextPage").get_attribute("href"):
                next_page = driver.find_element(By.CLASS_NAME, "pagination__nextPage").get_attribute("href")
            else:
                next_page = None
                
        except Exception as e:
            pass

        # classify the link part of offers
        offers = driver.find_elements(By.CLASS_NAME, "listing__teaserWrapper")
        time.sleep(2)
        
        # find out the links
        links_from_current_site = []
        for offer in offers:
            try:
                link = offer.find_element(By.CLASS_NAME, "teaserLink").get_attribute("href")
                if link.lstrip("hhtps://")[:3] != "gra":
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
            driver.get(next_page)
            time.sleep(2)
            
        else:
            print("no more links to go to.... /n im leaving this loop")
            break
            # Go to next page to collect links.

    return all_links

def read_links_from_csv(file_path):
    links = []

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                row_string = ', '.join(row)
                links.append(row_string)

    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return links

def get_from_gratka(site_url):
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
        price_element = soup.find('div', class_='priceInfo')
        listing_details['rent'] = price_element.find('span', class_='priceInfo__value').text.replace("\n", "").replace("zł/miesiąc", "").strip()
    except AttributeError:
        listing_details['rent'] = 'N/A'

    try:
        description_element = soup.find('div', class_='description__rolled')
        listing_details['description'] = description_element.get_text(strip=True, separator=" ")
    except AttributeError:
        listing_details['description'] = 'N/A'

    try:
        address_element = soup.find('span', class_='offerLocation')
        listing_details['address'] = " ".join(address_element.text.replace("\n", "").strip().replace(",", "").split())
    except AttributeError:
        listing_details['address'] = 'N/A'

    try:
        title_element = soup.find('h1', class_='sticker__title')
        listing_details['title'] = title_element.text.replace("\n", "").replace(",", "").strip()
    except AttributeError:
        listing_details['title'] = 'N/A'

    try:
        additional_info_element = soup.find('div', class_='oglField--array')
        additional_info = [info.text.strip() for info in additional_info_element.find_all('li', class_='oglFieldList__item')]
        listing_details['additional_info'] = additional_info
    except AttributeError:
        listing_details['additional_info'] = []

    try:
        parameters_div = soup.find('div', class_='parameters')
        parameters_deeper = parameters_div.find('ul', class_='parameters__singleParameters')
                
        for element in parameters_deeper:
            try:
                key = element.find('span').text
                if element.find("b", class_= 'parameters__value').text.replace("\n", "").strip():
                    val = element.find("b", class_= 'parameters__value').text.replace("\n", "").strip()
                else:
                    val = element.find("div", class_= 'parameters__value').text.replace("\n", "").strip()
                if key and val:
                    listing_details[key] = val
                elif key:
                    listing_details[key] = "N/A"
            except:
                pass
            
            try:
                key = element.find('span').text
                val = element.find("div", class_= 'parameters__value').text.replace("\n", "").strip()
                listing_details[key] = val
                if key and val:
                    listing_details[key] = val
            except:
                pass
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