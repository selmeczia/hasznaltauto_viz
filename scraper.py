from typing import Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime

URL = "https://www.hasznaltauto.hu/talalatilista/PCOG2VGRR3RDADH4S57ADFACW7M4OO5BIM5KDFKO3LL4UUCTIKJRQJLJWWYOFX6PNEFNOVB42WNITY7R3AUYRRM37B3GFHULVQAY6NKZBE56ZMTXY3TCE4ZX2SUK5UD25KQUEZFA2KB3WAJ7JFN2CR6XIEC65FV557CWZOFEMNMICLNVGTQZFGOIWIUQGX3DMYUTE3DNTHSO2XQREHWVTH5LDJIL4PED2VWX7D6I436XOLNSDIWJRAYEEXOYWA3Z5AKBJGIXDTL5ZI2FOVBE6L7IG6I3CPTS2KR7PZNDZTKBNWWA3HB7TALTUND65AEN3JLDIYHTE43GU6AMH2NOK3RMXJLHSFYEWD2HZWJL7EYZ3QKPM6H77DLDP57JHRV7NA5XSQEXDD3XDOS2GKP3FQSBJXHIKD5N6OSP6SHHH4WGT4USZS3IV5FKZ75NZ3QGFNTA6K5E3PMJQI2NXWI4VI4NDEWE5A3NUCKFKOF3MD5YUVMIQJ7VJIKSAPBYFVSF2F54WOK6LZNHORRV3EN6Y6AQ4BJ2HHXAZCUEM5R4DBHAPFXZFX5ZKDFVONLHZD4DH7ZG46675DUXUJSUWKPSZOPFO4A6MCTVOJZVZCT3L4MZJAQL7HAC6U26RJ4YZ4YQ44YV5BDYCHRSFRCFRSLVCJ3LH2Q2TUNW2Y7YJMST6PCSYWU76JIW3YEXAPHTP4ICKJJ7FGXLY4LHFB5NIKDQTSWNWHPQV5MNTK7LSPH4D54BJYI7UDA4G6HEPSMJZOZV7Q7JUMN6BKNUAR7ZSXWAPI5IWDYWDG24BF5QKSKSVCQVUXTXEMT3AR35BG2ZHW72G4NZN6OWSC4XMY4O3VAHPGII5XENBCJM2VRXYHP7IH6GRRZIX6LEMSM5WQNH4IS4BXGRKXLZERNYHURDTX3WQMV7RJPXI2BVTKI5R6Z7QE424UI"
# page = requests.get(URL)






class HasznaltautoScraper():

    def __init__(self, init_link) -> None:
        self.init_link = init_link
        self.page = requests.get(self.init_link)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.last_page = self.get_last_page()
        self.car_type = self.get_car_type()

    def __call__(self) -> pd.DataFrame:
        # data_folder = f"{os.getcwd()}/scraped_data/"
        df_data = self.process_data(self.visit_pages())

        return df_data


    def get_last_page(self):
        return int(self.soup.find("div", {"class": "text-center link-pager-container"}).find("li", {"class": "last"}).text)
    
    def get_car_type(self):
        return self.soup.find("ul", {"class": "breadcrumb"}).find_all("li")[-1].find("a")["title"].replace("Eladó ", "").lower().replace(" ", "_")
    

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