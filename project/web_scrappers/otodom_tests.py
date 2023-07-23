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

offer_list = driver.find_elements(By.CSS_SELECTOR, "[data-cy=listing-item]")

print(f"Length of offers: {len(offer_list)}")

for offer in offer_list:
    try:
        link = offer.get_attribute("href")
        links_from_current_site.append(link)
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

