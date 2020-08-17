import re
import sys
import time
import requests
from product import Product
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


base_url = "https://www.amazon.com"


class Scraper(object):

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
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
        try:
            response = self.session.get(url, headers=self.headers)
        except requests.exceptions.SSLError as e:
            print(e)
            sys.exit()
        except requests.exceptions.ConnectionError as e:
            print(e)
            sys.exit()

        if response.status_code != 200:
            raise ConnectionError(
                "Error occured, status code:{response.status_code}")
        return response

    def check_page_validity(self, page_content):

        if "We're sorry. The Web address you entered is not a functioning page on our site." in page_content:
            valid_page = False
        elif "Try checking your spelling or use more general terms" in page_content:
            valid_page = False
        elif "Sorry, we just need to make sure you're not a robot." in page_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page

    def get_page_content(self, search_url):

        valid_page = True
        trail = 0
        max_retries = 5
        while (trail < max_retries):
            
            response = self.get_request(search_url)
            valid_page = self.check_page_validity(response.text)
            
            if valid_page:
                break

            print("Something went wrong, retrying...")
            time.sleep(1)
            trail += 1

        if not valid_page:
            print("No valid page was found or validate capcha page was given")
            sys.exit()

        return response.text

    def get_product_url(self, product):
        regexp = "a-link-normal a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        product_url = product.find('a', attrs={'class': classes}).get('href')
        return base_url + product_url

    def get_product_title(self, product):
        regexp = "a-color-base a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        try:
            title = product.find('span', attrs={'class': classes})
            return title.text.strip()
        except AttributeError:
            return ''

    def get_product_price(self, product):
        try:
            price = product.find('span', attrs={'class': 'a-offscreen'})
            return float(price.text.strip('$').replace(',', ''))
        except AttributeError:
            return None

    def get_product_image_url(self, product):
        image_tag = product.find('img')
        return image_tag.get('src')

    def get_product_rating(self, product):
        try:
            rating = re.search(r'(\d.\d) out of 5', str(product))
            return float(rating.group()[:3])
        except AttributeError:
            return None

    def get_product_review_count(self, product):
        try:
            review_count = product.find(
                'span', attrs={'class': 'a-size-base', 'dir': 'auto'})
            return int(review_count.text.strip().replace(',', ''))
        except AttributeError:
            return None
        except ValueError:
            return None

    def get_product_bestseller_status(self, product):

        bestseller_status = product.find(
            'span', attrs={'class': 'a-badge-text'})
        return bool(bestseller_status)

    def get_product_prime_status(self, product):
        regexp = "a-icon a-icon-prime a-icon-medium".replace(' ', '\s+')
        classes = re.compile(regexp)
        prime_status = product.find('i', attrs={'class': classes})
        return bool(prime_status)

    def get_product_info(self, product):
        product_obj = Product()
        product_obj.url = self.get_product_url(product)
        product_obj.title = self.get_product_title(product)
        product_obj.price = self.get_product_price(product)
        product_obj.img_url = self.get_product_image_url(product)
        product_obj.rating_stars = self.get_product_rating(product)
        product_obj.review_count = self.get_product_review_count(product)
        product_obj.bestseller = self.get_product_bestseller_status(product)
        product_obj.prime = self.get_product_prime_status(product)

        self.product_obj_list.append(product_obj)

    def get_page_count(self, page_content):
        soup = BeautifulSoup(page_content, 'html5lib')
        try:
            pagination = soup.find_all(
                'li', attrs={'class': ['a-normal', 'a-disabled', 'a-last']})
            return int(pagination[-2].text)
        except IndexError:
            return 1

    def prepare_page_list(self, search_url):
        for i in range(1, self.page_count + 1):
            self.page_list.append(search_url + '&page=' + str(i))

    def get_products(self, page_content):

        soup = BeautifulSoup(page_content, "html5lib")
        product_list = soup.find_all(
            'div', attrs={'data-component-type': 's-search-result'})

        result_list = list(map(self.get_product_info, product_list))
        return result_list

    def wrapper_get_prod(self, page_url):
        response_content = self.get_page_content(page_url)
        self.get_products(response_content)

    def search(self, search_word):

        search_url = self.prepare_url(search_word)
        response_content = self.get_page_content(search_url)

        self.page_count = self.get_page_count(response_content)
        if self.page_count <= 1:
            self.get_products(response_content)
            return self.product_obj_list

        self.prepare_page_list(search_url)
        with ThreadPoolExecutor() as executor:
            executor.map(self.wrapper_get_prod, self.page_list)

        return self.product_obj_list