from bs4 import BeautifulSoup
import requests
import pprint

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
            # print("xd", element)
            
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
                print("XD", element)
                key = element.find('span').text
                val = element.find("div", class_= 'parameters__value').text.replace("\n", "").strip()
                listing_details[key] = val
                if key and val:
                    listing_details[key] = val
            except:
                pass
    except AttributeError:
        pass
    
    return listing_details
    
    # pprint.pprint(listing_details)
    
link = 'https://gratka.pl/nieruchomosci/mieszkanie-gdansk-wrzeszcz-ul-hemara/ob/31373561'
get_from_gratka(site_url=link)