import datetime
import random
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities
from selenium_stealth import stealth

import pprint

URL = "https://www.skyscanner.ie/transport/flights/DUB/NRT/240725/?adults=1"
WAIT_TIME = 10
ACCEPT_ALL = "OK"

trip = [['DUB_NRT', 'PUS_ICN', 'KIX_DUB'],
        ['DUB_ICN', 'PUS_KIX', 'NRT_DUB'],
        ['DUB_ICN', 'PUS_NRT', 'KIX_DUB'],
        ['DUB_KIX', 'NRT_PUS', 'ICN_DUB']]

# trip = [['DUB_ICN', 'PUS_NRT', 'KIX_DUB'],
#         ['DUB_KIX', 'NRT_PUS', 'ICN_DUB'],
#         ['DUB_ICN', 'PUS_KIX', 'NRT_DUB'],
#         ['DUB_NRT', 'PUS_ICN', 'KIX_DUB']]


def get_dates(month=7, day=25, between=[6, 10]):
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


def generate_flight_query():
    URL = "https://www.skyscanner.ie/transport/flights/{}/{}/{}/?adults=1"
    dates = get_dates()
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
    flights = {}

    def __init__(self):
        self.configure_driver()

    def configure_driver(self):
        """
        We need to fake the user agent otherwise we're a bot
        :return: None
        """


        # options.headless = True  # you're lucky headless works for this site... for now
        # options = uc.ChromeOptions()
        # options.add_argument("start-maximized")
        #
        #
        # options.add_argument(f"user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0")
        # # Chrome is controlled by automated test software
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        # driver = uc.Chrome()
        # # Selenium Stealth settings
        # stealth(driver,
        #         languages=["en-US", "en"],
        #         vendor="Google Inc.",
        #         platform="Intel Mac OS X 10.15",
        #         webgl_vendor="Intel Inc.",
        #         renderer="Intel Iris OpenGL Engine",
        #         fix_hairline=True,
        #         )

        profile = webdriver.FirefoxProfile()
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.149 Safari/537.36")
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
        wait = WebDriverWait(self.driver, 5)

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
            catagory = catagory.replace("€", "").replace("h", "").lower()
            columns = catagory.split("\n")
            self.flights[meta['flight']][columns[0]] = []

            flight_data_formatted = {
                'date': meta['date'],
                "price": columns[1],
                "time_hours": columns[2],
                }
            self.flights[meta['flight']][columns[0]].append(flight_data_formatted)

    def search_flight(self, flight_queries):
        """

        :param url:
        :param flight_meta:
        :return:
        """
        try:

            WebDriverWait(self.driver, random.randint(WAIT_TIME/2, WAIT_TIME))
            self.driver.get(flight_queries['url'])
            self.handle_cookies()
            # Force it to wait for the page to load
            WebDriverWait(self.driver, random.randint(WAIT_TIME/2, WAIT_TIME))
            flight_info = self.get_flight_info()

            self.flights[flight_queries['flight_meta']['flight']] = {}
            self.standardise_flight(flight_info, flight_queries['flight_meta'])
            self.store_results()
        except Exception as e:
            print(f"FUCK {e}")


    def store_results(self):
        pprint.pprint(self.flights)



if __name__ == '__main__':
    flight_queries = generate_flight_query()
    sky = SkyScanner()

    for flight_query in flight_queries:
        sky.search_flight(flight_query)
        sleep(random.randint(5, 30))


