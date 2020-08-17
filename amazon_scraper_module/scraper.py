# -*- coding: utf-8 -*-
"""
Module to get and parse the product info on Amazon Search
"""

import re
import sys
import time
import uuid
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

from .product import Product


base_url = "https://www.amazon.com"


class Scraper(object):
    """Does the requests with the Amazon servers
    """

    def __init__(self):
        """ Init of the scraper
        """
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
        """Get the Amazon search URL, based on the keywords passed

        Args:
            search_word (str): word passed by the user to search amazon.com for (eg. smart phones)

        Returns:
            search url: Url where the get request will be passed (it will look something like https://www.amazon.com/s?k=smart+phones)
        """
        return urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+'))))

    def get_request(self, url):
        """ Places GET request with the proper headers

        Args:
            url (str): Url where the get request will be placed

        Raises:
            requests.exceptions.ConnectionError: Raised when there is no internet connection while placing GET request

            requests.HTTPError: Raised when response stattus code is not 200

        Returns:
            response or None: returns whatever response was sent back by the server or returns None if requests.exceptions.ConnectionError occurs
        """
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code != 200:
                raise requests.HTTPError(
                    "Error occured, status code:{response.status_code}")
        #  returns None if requests.exceptions.ConnectionError or requests.HTTPError occurs
        except (requests.exceptions.ConnectionError, requests.HTTPError) as e:
            print(e + "while connecting to" + url)
            return None

        return response

    def check_page_validity(self, page_content):
        """Check if the page is a valid result page

        Returns:
            valid_page: returns true for valid page and false for invalid page(in accordance with conditions)
        """

        if "We're sorry. The Web address you entered is not a functioning page on our site." in page_content:
            valid_page = False
        elif "Try checking your spelling or use more general terms" in page_content:
            valid_page = False
        elif "Sorry, we just need to make sure you're not a robot." in page_content:
            valid_page = False
        elif "The request could not be satisfied" in page_content:
            valid_page = False
        else:
            valid_page = True
        return valid_page

    def get_page_content(self, search_url):
        """Retrieve the html content at search_url

        Args:
            search_url (str): Url where the get request will be placed

        Raises:
            ValueError: raised if no valid page is found

        Returns:
            response.text or None: returns html response encoded in unicode or returns None if get_requests function or if the page is not valid even after retries
        """

        valid_page = True
        trial = 0
        # if a page does not get a valid response it retries(5 times)
        max_retries = 5
        while (trial < max_retries):

            response = self.get_request(search_url)

            if (not response):
                return None

            valid_page = self.check_page_validity(response.text)

            if valid_page:
                break

            print("No valid page was found, retrying in 3 seconds...")
            time.sleep(3)
            trial += 1

        if not valid_page:
            print(
                "Even after retrying, no valid page was found on this thread, terminating thread...")
            return None

        return response.text

    def get_product_url(self, product):
        """Retrieves and returns product url

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            url: returns full url of product
        """

        regexp = "a-link-normal a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        product_url = product.find('a', attrs={'class': classes}).get('href')
        return base_url + product_url

    def get_product_asin(self, product):
        """ Retrieves and returns Amazon Standard Identification Number (asin) of a product

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            asin: returns Amazon Standard Identification Number (asin) of a product
        """

        return product.get('data-asin')

    def get_product_title(self, product):
        """Retrieves and returns product title
        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            title: returns product title or empty string if no title is found
        """

        regexp = "a-color-base a-text-normal".replace(' ', '\s+')
        classes = re.compile(regexp)
        try:
            title = product.find('span', attrs={'class': classes})
            return title.text.strip()

        # AttributeError occurs when no title is found and we get back None
        # in that case when we try to do title.text it raises AttributeError
        # because Nonetype object does not have text attribute
        except AttributeError:
            return ''

    def get_product_price(self, product):
        """Retrieves and returns product price
        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            price: returns product price or None if no price is found
        """

        try:
            price = product.find('span', attrs={'class': 'a-offscreen'})
            return float(price.text.strip('$').replace(',', ''))

        # AttributeError occurs when no price is found and we get back None
        # in that case when we try to do price.text it raises AttributeError
        # because Nonetype object does not have text attribute

        # ValueError is raised while converting price.text.strip() into float
        # of that value and that value for some reason is not convertible to
        # float
        except AttributeError:
            return None
        except ValueError:
            return None

    def get_product_image_url(self, product):
        """Retrieves and returns product image url

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            image_url: returns product image url
        """

        image_tag = product.find('img')
        return image_tag.get('src')

    def get_product_rating(self, product):
        """Retrieves and returns product rating

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            rating : returns product rating or returns None if no rating is found
        """

        try:
            rating = re.search(r'(\d.\d) out of 5', str(product))
            return float(rating.group(1))

        # AttributeError occurs when no rating is found and we get back None
        # in that case when we try to do rating.text it raises AttributeError
        # because Nonetype object does not have text attribute

        # ValueError is raised while converting rating.group(1) into float
        # of that value and that value for some reason is not convertible to
        # float
        except AttributeError:
            return None
        except ValueError:
            return None

    def get_product_review_count(self, product):
        """Retrieves and returns number of reviews a product has

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            review count: returns number of reviews a product has or returns None if no reviews are available
        """

        try:
            review_count = product.find(
                'span', attrs={'class': 'a-size-base', 'dir': 'auto'})
            return int(review_count.text.strip().replace(',', ''))

        # AttributeError occurs when no review_count is found and we get back None
        # in that case when we try to do review_count.text it raises AttributeError
        # because Nonetype object does not have text attribute

        # ValueError is raised while converting review_count.text.strip() into
        # int of that value and that value for some reason is not convertible to
        # int
        except AttributeError:
            return None
        except ValueError:
            return None

    def get_product_bestseller_status(self, product):
        """Retrieves and returns if product is best-seller or not

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            bestseller_status: returns if product is best-seller or not
        """

        try:
            bestseller_status = product.find(
                'span', attrs={'class': 'a-badge-text'})
            return bestseller_status.text.strip() == 'Best Seller'

        # AttributeError occurs when no bestseller_status is found and we get back None
        # in that case when we try to do bestseller_status.text it raises AttributeError
        # because Nonetype object does not have text attribute
        except AttributeError:
            return False

    def get_product_prime_status(self, product):
        """Retrieves and returns if product is supported by Amazon prime

        Args:
            product (str): higher level html tags of a product containing all the information about a product

        Returns:
            prime_status: eturns if product is supported by Amazon prime
        """

        regexp = "a-icon a-icon-prime a-icon-medium".replace(' ', '\s+')
        classes = re.compile(regexp)
        prime_status = product.find('i', attrs={'class': classes})
        return bool(prime_status)

    def get_product_info(self, product):
        """Gathers all the information about a product and 
        packs it all into an object of class Product
        and appends it to list of Product objects

        Args:
            product (str): higher level html tags of a product containing all the information about a product
        """

        product_obj = Product()
        product_obj.url = self.get_product_url(product)
        product_obj.asin = self.get_product_asin(product)
        product_obj.title = self.get_product_title(product)
        product_obj.price = self.get_product_price(product)
        product_obj.img_url = self.get_product_image_url(product)
        product_obj.rating_stars = self.get_product_rating(product)
        product_obj.review_count = self.get_product_review_count(product)
        product_obj.bestseller = self.get_product_bestseller_status(product)
        product_obj.prime = self.get_product_prime_status(product)

        self.product_obj_list.append(product_obj)

    def get_page_count(self, page_content):
        """Extracts number of pages present while searching for user-specified word

        Args:
            page_content (str): unicode encoded response

        Returns:
            page count: returns number of search pages for user-specified word if IndexError is raised then function returns 1
        """

        soup = BeautifulSoup(page_content, 'html5lib')
        try:
            pagination = soup.find_all(
                'li', attrs={'class': ['a-normal', 'a-disabled', 'a-last']})
            return int(pagination[-2].text)
        except IndexError:
            return 1

    def prepare_page_list(self, search_url):
        """prepares a url for every page and appends it to page_list in accordance with the page count

        Args:
            search_url (str): url generated by prepare_url function
        """

        for i in range(1, self.page_count + 1):
            self.page_list.append(search_url + '&page=' + str(i))

    def get_products(self, page_content):
        """extracts higher level html tags for each product present while scraping all the pages in page_list

        Args:
            page_content (str): unicode encoded response

        """

        soup = BeautifulSoup(page_content, "html5lib")
        product_list = soup.find_all(
            'div', attrs={'data-component-type': 's-search-result'})

        for product in product_list:
            self.get_product_info(product)

    def wrapper_get_prod(self, page_url):
        """wrapper function that gets contents of a given url and gets products from that url

        Args:
            page_url (str): url of one of search pages
        """

        page_content = self.get_page_content(page_url)
        if (not page_content):
            return

        self.get_products(page_content)

    def generate_output_file(self):
        """generates json file from list of products found in the whole search
        """

        data = []
        # generate random file name
        filename = str(uuid.uuid4()) + '.json'
        # every object gets converted into json format
        for obj in self.product_obj_list:
            data.append(obj.to_json())
        data = ','.join(data)
        string_data = '[' + data + ']'
        with open('./' + filename, mode='w') as f:
            f.write(string_data)

    def search(self, search_word):
        """Initializies that search and puts together the whole class

        Args:
            search_word (str): user given word to be searched
        """

        search_url = self.prepare_url(search_word)
        page_content = self.get_page_content(search_url)
        if (not page_content):
            return

        self.page_count = self.get_page_count(page_content)
        # if page count is 1, then there is no need to prepare page list therefore the condition and
        # we just parse the content recieved above
        if self.page_count <= 1:
            self.get_products(page_content)

        else:
            # if page count is more than 1, then we prepare a page list and start a thread at each page url
            self.prepare_page_list(search_url)
            # creating threads at each page in page_list
            with ThreadPoolExecutor() as executor:
                for page in self.page_list:
                    executor.submit(self.wrapper_get_prod, page)

        # generate a json output file
        self.generate_output_file()
