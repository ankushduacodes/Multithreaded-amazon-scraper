import re
import requests
import Product
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


base_url = "https://www.amazon.com"


class Search(object):

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        self.product_obj_list = []
        self.page_list = []

    def prepare_url(self, search_word):

        return urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+'))))

    def get_request(self, url):

        response = self.session.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ConnectionError(
                "Error occured, status code:{response.status_code}")
        return response

    def check_page_validity(self, page_content):

        if "We're sorry. The Web address you entered is not a functioning page on our site." in page_content:
            valid_page = False
        elif "Try checking your spelling or use more general terms" in page_content:
            valid_page = False
        elif "Sign in for the best experience" in html_content:
            valid_page = False
        elif "The request could not be satisfied." in html_content:
            valid_page = False
        elif "Robot Check" in html_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page

    def get_page_content(self, search_url):

        valid_page = True
        try:
            response = self.get_request(search_url)
            valid_page = self.check_page_validity(response.text)

        except requests.exceptions.SSLError:
            valid_page = False

        except ConnectionError:
            valid_page = False

        if not valid_page:
            raise ValueError("No valid page was found")

        return response.text

    def get_product_url(self, product):
        regexp = "a-link-normal a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        product_url = product.find('a', attrs={'class': classes}).get('href')
        return base_url + product_url

    def get_product_title(self, product):
        regexp = "a-size-medium a-color-base a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        title = product.find('span', attrs={'class': classes})
        return title.text.strip()

    def get_product_price(self, product):
        pass

    def get_product_image_url(self, product):
        pass

    def get_product_rating(self, product):
        pass

    def get_product_review_num(self, product):
        pass

    def get_product_bestseller_status(self, product):
        pass

    def get_product_prime_status(self, product):
        pass

    def get_product_info(self, product):
        product_obj = Product()
        product_obj.url = self.get_product_url(product)
        product_obj.title = self.get_product_title(product)
        product_obj.price = self.get_product_price(product)
        product_obj.image_url = self.get_product_image_url(product)
        product_obj.rating_stars = self.get_product_rating(product)
        product_obj.num_of_reviews = self.get_product_review_num(product)
        product_obj.bestseller = self.get_product_bestseller_status(product)
        product_obj.prime = self.get_product_prime_status(product)

        self.product_obj_list.append(product_obj)

    def get_page_count(self, page_content):
        soup = BeautifulSoup(page_content, 'html5lib')
        try:
            pagination = soup.find_all(
                'li', attrs={'class': ['a-normal', 'a-disabled', 'a-last']})
            return int(list(pagination)[-2].text)
        except IndexError:
            return 1

    def prepare_page_list(self, page_count, search_url):
        for i in range(1, page_count + 1):
            page_list.append(search_url + '&page=' + str(i))

    def get_products(self, page_content):

        soup = BeautifulSoup(page_content, "html5lib")
        regexp = "sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-28-of-32 sg-col-16-of-20 sg-col sg-col-32-of-36 sg-col-12-of-16 sg-col-24-of-28".replace(
            ' ', '\s+')
        classes = re.compile(regexp)
        product_list = soup.find_all('div', class_=[classes, 'AdHolder'])

        with ThreadPoolExecutor() as executor:
            result_list = list(executor.map(
                self.get_product_info, product_list))

        return (result_list)

    def search_result(self, search_word):

        search_url = self.prepare_url(search_word)
        response_content = self.get_page_content(search_url)
        self.page_count = self.get_page_count(response_content)
        if self.page_count <= 1:
            self.get_products(response_content)
            return product_obj_list
        else:
            pass
