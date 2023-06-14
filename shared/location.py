import re
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def get_address_number(address: str) -> str:
    patter_number = r"\d+"
    numbers = re.findall(patter_number, address)

    biggest_sequence = ""
    
    for number in numbers:
        if len(number) > len(biggest_sequence):
            biggest_sequence = number

    if (numbers):
        return biggest_sequence
    else:
        return None

def get_info_address(address: str) -> tuple[str, str, str, str]:
    number = get_address_number(address)

    url = f"https://www.google.com/search?q={address}"
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random}
    response = requests.head(url, headers=headers)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all('a')

        try:
            link = [(_["href"]) for _ in links if "maps.google" in _["href"]]
            link = link[0]

            latitude = None
            longitude = None
            patter_latitude_longitude = r"ll=([-+]?\d+\.\d+),([-+]?\d+\.\d+)"
            match = re.search(patter_latitude_longitude, link)
            if match:
                latitude = match.group(1)
                longitude = match.group(2)

            cep = None
            patter_cep = r"q=.*?(\d{5}-\d{3})"
            match = re.search(patter_cep, link)
        
            if match:
                cep = match.group(1)

            return latitude, longitude, cep, number
        except:
            return None, None, None, number