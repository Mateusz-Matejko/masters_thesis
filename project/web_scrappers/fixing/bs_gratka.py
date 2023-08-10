from bs4 import BeautifulSoup
import requests
import pprint

def get_from_gratka():
    try:
        response = requests.get('https://gratka.pl/nieruchomosci/mieszkanie-gdansk-wrzeszcz-ul-hemara/ob/31373561')
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
    
    pprint.pprint(listing_details)
    
get_from_gratka()