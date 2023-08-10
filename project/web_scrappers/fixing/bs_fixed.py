from bs4 import BeautifulSoup
import requests
import pprint

url = "https://ogloszenia.trojmiasto.pl/nieruchomosci-mam-do-wynajecia/vii-dwor-oliwawrzeszcz-blisko-ug-super-lokalizac-ogl65387890.html"  # Replace with the actual URL
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    listing_details = {}

    elements = soup.find_all(class_='oglField')
    for element in elements:
        key_element = element.find('div', class_='oglField__name')
        value_element = element.find('span', class_='oglField__value')

        if key_element and value_element:
            key = key_element.text.strip()
            value = value_element.text.strip()
            listing_details[key] = value

    pprint.pprint(listing_details)

else:
    print("Failed to fetch the webpage.")
