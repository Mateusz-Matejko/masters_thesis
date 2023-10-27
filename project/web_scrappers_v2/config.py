import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Config:
    def __init__(self) -> None:
        self.folder = "collected_10_25"
        self.path_to_chrome = ""
    
    def get_driver(self):
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

        driver = webdriver.Chrome(options=options)
        return driver
    
    def path_generator(self, folder, portal, city, path_type = "original", ending="json"):
        return f"../original_data_2023/{portal}/{folder}/{city}_{path_type}.{ending}"
        
    def save_collected_data(self, what="data"):
        if what == "data":
            with open(self.output_data, "w") as collected_data_destination:
                json.dump(self.all_listings, collected_data_destination, indent=2)

        if what == "links":
            with open(self.output_links, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                for link in self.all_links:
                    url = ''.join(link)
                    csv_writer.writerow([url])

        if what == "errors":
            if self.errored_links:
                with open(self.output_errors, "w") as occured_errors_destination:
                    json.dump(self.errored_links, occured_errors_destination, indent=2)