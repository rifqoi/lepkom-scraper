import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from dotenv import dotenv_values


class Scraper:

    def __init__(self, url):
        self.url = url
        self.session = requests.Session()

    def credentials(self, ):
        load_dotenv()
        dotenv = dotenv_values()
        USERNAME = dotenv.get('USERNAME')
        PASSWORD = dotenv.get('PASSWORD')

        return USERNAME, PASSWORD

    def login(self, ):
        username, password = self.credentials()
        r = self.session.get(self.url)
        token_pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(token_pattern, r.text)
        token = re.findall(r"\w{32}", token[0])

        payload = {
            'username': username,
            'password': password,
            'anchor': '',
            'logintoken': token[0]
        }

        r = self.session.post(self.url, data=payload)

        return self.session


def main():

    url = "https://kursusvmlepkom.gunadarma.ac.id/login/index.php"
    scraper = Scraper(url)
    r = scraper.login()
    r = r.get('https://kursusvmlepkom.gunadarma.ac.id/')
    soup = BeautifulSoup(r.text, 'html.parser')
    soup = soup.find_all("h3", class_="coursename")

    links = []
    for link in soup:
        a = link.find('a')
        url = a.get('href')
        text = a.text
        links.append((url, text))

    print(links)


if __name__ == "__main__":
    main()
