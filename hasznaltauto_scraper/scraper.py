from typing import Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime
from multiprocessing import Pool
import concurrent.futures
import threading


class HasznaltautoScraper():

    def __init__(self, init_link) -> None:
        self.init_link = init_link
        self.page = requests.get(self.init_link)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.last_page = self.get_last_page()
        self.car_type = self.get_car_type()

        self.multiprocess_run = True
        self.thread_local = threading.local()

    def __call__(self) -> pd.DataFrame:

        data = self.executor()

        df_data = self.process_data(data)

        return df_data
    
    def executor(self):

        page_links = [f"{self.init_link}/page{page_num}" for page_num in range(1, self.last_page + 1)]

        if self.multiprocess_run:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                raw_results = list(executor.map(self.visit_page, page_links))
                results = [item for sublist in raw_results for item in sublist]
        else:
            raw_results = []
            for page_link in page_links:
                raw_results.append(self.visit_page(page_link))
            results = [item for sublist in raw_results for item in sublist]

        return results


    def get_last_page(self):
        try:
            return int(self.soup.find("div", {"class": "text-center link-pager-container"}).find("li", {"class": "last"}).text)
        except AttributeError:
            return 1

    def get_car_type(self):
        return self.soup.find("ul", {"class": "breadcrumb"}).find_all("li")[-1].find("a")["title"].replace("Eladó ", "").lower().replace(" ", "_")
    
    def get_session(self):
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session
    
    def visit_page(self, current_url):

        session = self.get_session()
        with session.get(current_url) as current_page:

            data = []

            current_soup = BeautifulSoup(current_page.content, "html.parser")

            paid_ads =  current_soup.find_all("div", {"class": "row talalati-sor kiemelt"})
            paid_border_ads =  current_soup.find_all("div", {"class": "row talalati-sor keretes kiemelt"})
            regular_ads = current_soup.find_all("div", {"class": "row talalati-sor"})

            ads_all = paid_ads + paid_border_ads + regular_ads

            for ad in ads_all:
                info_line = ad.find("div", {"class": "talalatisor-info adatok"}).text.replace(u'\xa0', '').split(", ")
                title = ad.find("h3").text
                try:
                    price = int(ad.find("div", {"class": "pricefield-primary"}).text.replace(u'\xa0', '').replace("Ft",""))
                except:
                    try:
                        price = int(ad.find("div", {"class": "pricefield-primary-highlighted"}).text.replace(u'\xa0', '').replace("Ft",""))
                    except:
                        price = None

                # comfort = "highline" if "highline" in title.lower() else \
                #         "comfortline" if "comfortline" in title.lower() else \
                #         "trendline" if "trendline" in title.lower() else None
                
                # comfort = "essentia" if "essentia" in title.lower() else \
                #         "cosmo" if "cosmo" in title.lower() else \
                #         "enjoy" if "enjoy" in title.lower() else \
                #         "sport" if "sport" in title.lower() else \
                #         "elegance" if "elegance" in title.lower() else None

                link = ad.find("a", href=True)["href"]
                year, month = next((re.split(r'/', item) for item in info_line if re.search(r'\d+/\d+', item)), (None, None))
                age_in_months = self.calculate_car_age(year, month)

                gas_type = next((item for item in info_line if re.search(r'(Benzin|Dízel)', item)), None)
                motor_size = next((int(re.search(r'(\d+) cm³$', item).group(1)) for item in info_line if re.search(r'\d+ cm³$', item)), None)
                motor_kw = next((int(re.search(r'(\d+)kW$', item).group(1)) for item in info_line if re.search(r'\d+kW$', item)), None)
                motor_hp = next((int(re.search(r'(\d+)LE$', item).group(1)) for item in info_line if re.search(r'\d+LE$', item)), None)
                mileage_km = next((int(re.search(r'(\d+)km$', item).group(1)) for item in info_line if re.search(r'\d+km$', item)), None)

                data.append(
                {
                        "price": price,
                        "title": title,
                        # "comfort" : comfort,
                        "gas_type": gas_type,
                        "age_in_months": age_in_months,
                        "motor_size": motor_size,
                        "motor_kw": motor_kw,
                        "motor_hp": motor_hp,
                        "mileage_km": mileage_km,
                        "link": link,
                        }
                )


        return data
        

    def visit_pages(self):

        data = []
        for page_num in range(1, self.last_page + 1):
            current_url = f"{self.init_link}/page{page_num}"

            current_page = requests.get(current_url)
            current_soup = BeautifulSoup(current_page.content, "html.parser")

            paid_ads =  current_soup.find_all("div", {"class": "row talalati-sor kiemelt"})
            paid_border_ads =  current_soup.find_all("div", {"class": "row talalati-sor keretes kiemelt"})
            regular_ads = current_soup.find_all("div", {"class": "row talalati-sor"})

            ads_all = paid_ads + paid_border_ads + regular_ads

            for ad in ads_all:
                info_line = ad.find("div", {"class": "talalatisor-info adatok"}).text.replace(u'\xa0', '').split(", ")
                title = ad.find("h3").text
                try:
                    price = int(ad.find("div", {"class": "pricefield-primary"}).text.replace(u'\xa0', '').replace("Ft",""))
                except:
                    try:
                        price = int(ad.find("div", {"class": "pricefield-primary-highlighted"}).text.replace(u'\xa0', '').replace("Ft",""))
                    except:
                        price = None

                # comfort = "highline" if "highline" in title.lower() else \
                #         "comfortline" if "comfortline" in title.lower() else \
                #         "trendline" if "trendline" in title.lower() else None
                
                # comfort = "essentia" if "essentia" in title.lower() else \
                #         "cosmo" if "cosmo" in title.lower() else \
                #         "enjoy" if "enjoy" in title.lower() else \
                #         "sport" if "sport" in title.lower() else \
                #         "elegance" if "elegance" in title.lower() else None

                link = ad.find("a", href=True)["href"]
                year, month = next((re.split(r'/', item) for item in info_line if re.search(r'\d+/\d+', item)), (None, None))
                age_in_months = self.calculate_car_age(year, month)

                gas_type = next((item for item in info_line if re.search(r'(Benzin|Dízel)', item)), None)
                motor_size = next((int(re.search(r'(\d+) cm³$', item).group(1)) for item in info_line if re.search(r'\d+ cm³$', item)), None)
                motor_kw = next((int(re.search(r'(\d+)kW$', item).group(1)) for item in info_line if re.search(r'\d+kW$', item)), None)
                motor_hp = next((int(re.search(r'(\d+)LE$', item).group(1)) for item in info_line if re.search(r'\d+LE$', item)), None)
                mileage_km = next((int(re.search(r'(\d+)km$', item).group(1)) for item in info_line if re.search(r'\d+km$', item)), None)

                data.append(
                    {
                        "price": price,
                        "title": title,
                        # "comfort" : comfort,
                        "gas_type": gas_type,
                        "age_in_months": age_in_months,
                        "motor_size": motor_size,
                        "motor_kw": motor_kw,
                        "motor_hp": motor_hp,
                        "mileage_km": mileage_km,
                        "link": link,
                    }
                )
        return data

    def calculate_car_age(self, year, month):
        if year and month:
            current_year = datetime.now().year
            current_month = datetime.now().month

            age_in_months = (current_year - int(year)) * 12 + (current_month - int(month))

            return age_in_months
        else:
            return None

    def process_data(self, data):
        df = pd.DataFrame(data)

        return df
            
      

    





       
# df = pd.DataFrame(data)
# df.to_csv(f"{data_folder}/{car_type}_6_1.4_benzin.csv")