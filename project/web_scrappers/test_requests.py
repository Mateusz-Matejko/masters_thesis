import pprint
import requests
from bs4 import BeautifulSoup
import time

def get_listing_details(url):
    listing_details = {}
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    price_element = soup.find('h2', class_= "css-5ufiv7 er34gjf0")
    price = price_element.text.strip()
    
    title_element = soup.find("h1", class_ = "css-bg3pmc er34gjf0")
    title = title_element.text.strip()
    
    name_element = soup.find("h4", class_= "css-1lcz6o7 er34gjf0")
    name = name_element.text.strip()
        
   # Find the location element with class "css-1c0ed4l"
    location_element = soup.select_one('span.css-1c0ed4l')

    # Extract the location text if the element is found, otherwise return "Location not found"
    location = location_element.text.strip() if location_element else "Location not found"

    # Print or use the location as needed
    print(location)
    
    input()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # Price of listing
    # price = soup.find("span", class_="css-47bkj9")
    # listing_details["rent"] = price.text if price else ""
    
    # # Location
    # location = soup.find("div", class_="css-1cju8pu er34gjf0")
    # listing_details["location"] = location.text if location else ""
    
    # # Username and other details
    # username_attr = soup.find("div", class_="css-1fp4ipz")
    # if username_attr:
    #     username_attr = username_attr.get_text("\n").split("\n")
    #     listing_details["username"] = username_attr[1]
    #     listing_details["on_olx_since"] = username_attr[2].lstrip("Na OLX od ")
    #     listing_details["last_activity"] = username_attr[3]
    
    # # Added date
    # date_of_listing_add = soup.find("span", class_="css-8mfr0h")
    # listing_details["add_date"] = date_of_listing_add.text.lstrip("Dodane") if date_of_listing_add else ""
    
    # # Title
    # title = soup.find("span", class_="css-8mfr0h")
    # listing_details["title"] = title.text if title else ""
    
    # # Link
    # listing_details["link"] = url
    
    # # Description
    # description = soup.find("div", class_="css-1m8mzwg")
    # listing_details["description"] = description.text.lstrip("Opis").replace("\n", '') if description else ""
    
    # # Other options
    # options = soup.find_all("div", class_="css-sfcl1s")
    # for option in options:
    #     try:
    #         k, v = option.text.split(":")
    #         listing_details[k] = v
    #     except ValueError:
    #         listing_details[option.text] = "true"
    
    return listing_details

url = "https://www.olx.pl/d/oferta/kawalerka-nowy-budownictwo-wolna-od-wrzesnia-CID3-IDWkhgl.html"  # Replace with the actual URL of the listing
listing_details = get_listing_details(url)

pprint.pprint(listing_details)