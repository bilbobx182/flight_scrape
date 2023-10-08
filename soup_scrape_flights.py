import datetime
import requests
from bs4 import BeautifulSoup
import re





def scrape_scanner(url="https://www.skyscanner.ie/transport/flights/DUB/NRT/240725/?adults=1"):

    response = requests.get(url)


    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        pattern = re.compile(r'FqsTabs_tooltipTargetContainer')
        matching_divs = soup.find_all('div', class_=pattern)

        # Extract text from matching divs
        matching_div_text = [div.get_text() for div in matching_divs]

        # Print the text from matching divs
        for text in matching_div_text:
            print(text)
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        "'SkyscannerYou need to enable JavaScript to run this app.'"

scrape_scanner()
