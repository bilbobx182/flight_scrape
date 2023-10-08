import datetime
import random
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities

import pprint

MONTH = 7
DAY = 27
WAIT_TIME = 30
ACCEPT_ALL = "OK"


flights = {}

trip = [['DUB_ICN', 'PUS_NRT', 'KIX_DUB'],
        ['DUB_KIX', 'NRT_PUS', 'ICN_DUB'],
        ['DUB_ICN', 'PUS_KIX', 'NRT_DUB'],
        ['DUB_NRT', 'PUS_ICN', 'KIX_DUB']]


def get_dates(month=MONTH, day=DAY, between=[6, 10]):
    """
    Method to get the dates in skyscanner format.
    :param month: date of the month ie August = 8
    :param day: number of the day in the month
    :param between: an array of how many days between each we want to get. So 3 days, then 10 days until return.
    :return: [start holiday date, middle date, return date]
    """
    date_format = "%y%m%d"
    start_date = datetime.datetime(2024, month, day)
    start = start_date.strftime(date_format)
    # Todo could be better, but idk
    mid = ((start_date + datetime.timedelta(days=between[0])).strftime(date_format))
    end = ((start_date + datetime.timedelta(days=between[1])).strftime(date_format))
    return [start, mid, end]


def generate_flight_query(dates):
    URL = "https://www.skyscanner.ie/transport/flights/{}/{}/{}/?adults=1"
    result = []

    for journey in trip:
        for flight in journey:
            flight_result = {}
            flight_date = dates[journey.index(flight)]

            flight_codes = flight.split("_")

            flight_result['url'] = URL.format(flight_codes[0], flight_codes[1], flight_date)
            flight_result['flight_meta'] = {
                'flight': flight,
                'date': "20" + flight_date
            }
            result.append(flight_result)

    return result




class SkyScanner:
    driver = None

    def __init__(self):
        # self.configure_driver()
        print("Starting")

    def configure_driver(self):
        """
        We need to fake the user agent otherwise we're a bot
        :return: None
        """

        # Exit early, force reset to avoid bot detection.
        if self.driver:
            self.driver.quit()
            self.driver = None
            return None


        profile = webdriver.FirefoxProfile()


        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference("general.useragent.override",
                               f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/{random.randint(5, 500)}.{random.randint(5, 100)} (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.{random.randint(5, 5000)}.{random.randint(100, 120)} Safari/{random.randint(100, 520)}.{random.randint(1, 120)}")
        profile.update_preferences()
        desired = DesiredCapabilities.FIREFOX

        driver = webdriver.Firefox(
            firefox_profile=profile,
            desired_capabilities=desired
        )

        self.driver = driver


    def handle_cookies(self):
        """
        Method to accept Click the OK to the cookies
        :return:
        """
        wait = WebDriverWait(self.driver, random.randint(WAIT_TIME/2, WAIT_TIME))
        but = "BpkButtonBase_bpk-button__ZWUyM CookieBanner_cookie-banner__button__YmNkM CookieBanner_cookie-banner__button-accept__YmYyZ"
        before = f"//button[@class='{but}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, before))).click()

    def get_flight_info(self):
        """
        Pattern match and find the elements at the top of the page that have best cheapest and fastest.
        :return:
        """
        # Find elements with wildcard class "*FqsTabs_tooltipTargetContainer*"
        matching_elements = self.driver.find_elements(By.XPATH,
                                                      "//*[contains(@class, 'FqsTabs_tooltipTargetContainer')]")

        return matching_elements

    def standardise_flight(self, flight_info, meta):
        """
        We want to convert it all to being a consistent format
        {'date':'YYYY-MM-DD',"price":number without euro,"time_hours":hours number,"time_minutes":minute number},
        :param flight:
        :return:
        """

        for catagory in flight_info:
            catagory = catagory.text
            catagory = catagory.replace("€", "").lower()
            columns = catagory.split("\n")
            flights[meta['flight']][columns[0]] = []

            flight_data_formatted = {'date': meta['date'],"price": columns[1],"time_hours": columns[2]}
            print(f"Adding {meta['flight']} {columns[0]} {flight_data_formatted}")
            flights[meta['flight']][columns[0]].append(flight_data_formatted)

    def search_flight(self, flight_queries):
        """
        Search for a single flight, get the info from it.
        :param url:
        :param flight_meta:
        :return:
        """
        try:
            self.configure_driver()
            WebDriverWait(self.driver, random.randint(WAIT_TIME/2, WAIT_TIME))
            self.driver.get(flight_queries['url'])
            self.handle_cookies()
            # Force it to wait for the page to load
            WebDriverWait(self.driver, random.randint(WAIT_TIME/2, WAIT_TIME))
            sleep(random.randint(1, 6))
            flight_info = self.get_flight_info()
            flights[flight_queries['flight_meta']['flight']] = {}
            self.standardise_flight(flight_info, flight_queries['flight_meta'])
            self.configure_driver()
        except Exception as e:
            print(f"FUCK {e}")
            self.configure_driver()



if __name__ == '__main__':

    # I want a bunch of flight to compare prices between start and end of the month
    day_numbers = [1, 10, 20, 29]


    for day in day_numbers:
        dates = get_dates(day=day, month=7)
        sleep(random.randint(45, 120))
        try:
            flight_queries = generate_flight_query(dates)
            sky = SkyScanner()
            for flight_query in flight_queries:
                sky.search_flight(flight_query)
                sleep(random.randint(45, 120))
        except Exception as error:
            print(error)
        finally:
            pprint.pprint(flights)


