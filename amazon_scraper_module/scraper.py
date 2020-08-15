import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

base_url = "https://www.amazon.com"


class Search():

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
        self.product_dict_list = []
        self.pages_list = []

    def prepare_url(self, search_word):

        return urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+'))))

    def get_request(self, url):
        response = self.session.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ConnectionError(
                "Error occured, status code:{response.status_code}")
        return response

    def get_page_content(self, search_url):

        valid_page = True
        try:
            response = self.get_request(search_url)

        except requests.exceptions.SSLError:
            valid_page = False

        except ConnectionError:
            valid_page = False

        if not valid_page:
            raise ValueError("No valid page was found")

        return response.text

    def get_next_page_url(self, page_content):

        soup = BeautifulSoup(page_content, "html5lib")
        next_page = soup.find("li", class_="a-last")
        try:
            next_page_link = next.a.get('href')
            del(soup)
            return next_page_link
        except AttributeError:
            del(soup)
            return ''
        
    def get_product_url(self, product):
        pass
    
    def get_product_title(self, product):
        pass

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
        product_dict = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            product_dict['url'] = executor.submit(self.get_product_url, product).result()
            product_dict['title'] = executor.submit(self.get_product_title, product).result()
            product_dict['price'] = executor.submit(self.get_product_price, product).result()
            product_dict['img_url'] = executor.submit(self.get_product_image_url, product).result()
            product_dict['rating'] = executor.submit(self.get_product_rating, product).result()
            product_dict['num_of_reviews'] = executor.submit(self.get_product_review_num, product).result()
            product_dict['bestseller'] = executor.submit(self.get_product_bestseller_status, product).result()
            product_dict['prime'] = executor.submit(self.get_product_prime_status, product).result()
        return product_dict

    def get_products(self, page_content):

        soup = BeautifulSoup(page_content, "html5lib")
        regexp = "sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-28-of-32 sg-col-16-of-20 sg-col sg-col-32-of-36 sg-col-12-of-16 sg-col-24-of-28".replace(
            ' ', '\s+')
        classes = re.compile(regexp)
        product_list = soup.find_all('div', attrs={'class': classes})

        with ThreadPoolExecutor() as executor:
            result_list = list(executor.map(self.get_product_info, product_list))
        
        return (result_list)

    def search_result(self, search_word):

        search_url = self.prepare_url(search_word)

        while (search_url):

            response_content = self.get_page_content(search_url)
            self.pages_list.append(response_content)
            next_page_url = self.get_next_page_url(response_content)

            if next_page_url:
                search_url = base_url + next_page_url

            else:
                search_url = next_page_url
                
        all_products = {}
        with ThreadPoolExecutor() as executor:
            for i in range(len(self.pages_list)):
                key = 'page ' + str(i)
                all_products[key] = executor.submit(self.get_products, self.pages_list[i]).result()
