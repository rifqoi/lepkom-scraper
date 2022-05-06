import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from dotenv import dotenv_values


class Scraper:

    def __init__(self, url):
        self.url = url
        self.session = self.login()

    def credentials(self, ):
        load_dotenv()
        dotenv = dotenv_values()
        USERNAME = dotenv.get('USERNAME')
        PASSWORD = dotenv.get('PASSWORD')

        return USERNAME, PASSWORD

    def login(self, ) -> requests.Session:
        username, password = self.credentials()
        session = requests.Session()
        r = session.get(self.url)
        token_pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(token_pattern, r.text)
        token = re.findall(r"\w{32}", token[0])

        payload = {
            'username': username,
            'password': password,
            'anchor': '',
            'logintoken': token[0]
        }

        r = session.post(self.url, data=payload)

        return session

    def get_courses(self) -> list:
        r = self.session.get('https://kursusvmlepkom.gunadarma.ac.id/')
        soup = BeautifulSoup(r.text, 'html.parser')

        h3 = soup.find_all('h3', class_='coursename')
        links = []
        for link in h3:
            a = link.find('a')
            url = a.get('href')
            text = a.text
            links.append((url, text))

        return links

    def get_delete_praktikan(self, url) -> tuple:
        r = self.session.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')
        r = soup.find_all('table')
        tr = r[0].find_all('tr')
        th = tr[0].find_all('th')
        th = [t.text for t in th]

        td_list = []

        for row in tr[1:]:
            td = row.find_all('td')
            td = [t.text for t in td]
            td_list.append(td)

        return th, td_list


def main():

    url = "https://kursusvmlepkom.gunadarma.ac.id/login/index.php"
    scraper = Scraper(url)


if __name__ == "__main__":
    main()
