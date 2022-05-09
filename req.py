import requests
from tabulate import tabulate
import pandas as pd
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

    def print_columns(self, df):
        pdtabulate = lambda df: tabulate(
            df, headers='keys', tablefmt='psql', showindex=False)

        print(pdtabulate(df))

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

    def show_delete_praktikan(self, url) -> None:
        th, td_list = self.get_delete_praktikan(url)

        df = pd.DataFrame(td_list, columns=th)
        self.print_columns(df)

    def get_participants_link(self, url):
        # r = self.session.get(url)
        # soup = BeautifulSoup(r.text, 'html.parser')
        # r = soup.find('nav', {'class': "list-group"})
        # r = r.find('a', {'data-key': 'participants'})
        # r = r.get('href')

        r = re.sub('course/view', 'user/index', url)

        # To list all of the students
        return r + '&perpage=5000'

    def get_participants(self, url):
        url = self.get_participants_link(url)
        r = self.session.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')
        r = soup.find_all('table')
        tr = r[0].find_all('tr')

        th = [
            'Nama', 'Kelas', 'NPM', 'Email', 'Roles', 'Groups', 'Last Access'
        ]

        td_list = []

        for row in tr[1:]:
            td = row.find_all('td')

            praktikan_information = [t.text for t in td if t.text != '']

            # Supaya nggak masukin anggota kosong
            if len(praktikan_information) == 0:
                break

            a = row.find_all('a')

            if praktikan_information[1] == 'Student':
                # Buat praktikan
                member_list = a[0].text.split()
                nama = ' '.join(member_list[:-2])
                kelas = member_list[-2]
                npm = member_list[-1]

            else:
                # Buat PJ, Asisten, Tutor, sama yang laen
                member_list = a[0].text.split()
                nama = ' '.join(member_list[:-1])
                roles = member_list[-1]
                npm = ""
                kelas = ""

                # Roles
                praktikan_information[1] = roles

            praktikan_information.insert(0, nama)
            praktikan_information.insert(1, kelas)
            praktikan_information.insert(2, npm)

            td_list.append(praktikan_information)

        return th, td_list

    def show_participants(self, url):
        th, td_list = self.get_participants(url)

        df = pd.DataFrame(td_list, columns=th)
        self.print_columns(df)


def main():

    url = "https://kursusvmlepkom.gunadarma.ac.id/login/index.php"
    scraper = Scraper(url)

    s = scraper.show_participants(
        'https://kursusvmlepkom.gunadarma.ac.id/course/view.php?id=2127')


if __name__ == "__main__":
    main()
