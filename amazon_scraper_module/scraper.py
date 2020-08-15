import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

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
        self.pages_content_list = []
    
    
    def prepare_url(self, search_word):
        
        return urljoin(base_url, ("/s?k=%s" % (search_word.replace(' ', '+'))))
    
    
    def get_request(self, url):
        response = self.session.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ConnectionError("Error occured, status code:{response.status_code}")
        return response
    
    
    def get_page_content(self, search_url):
        pass
    
    
    def search_result(self, search_word):
        
        search_url = self.prepare_url(search_word)
        
        while (search_url):
            
            response = self.get_page_content(search_url)
            self.pages_content_list.append(response.content)
            next_page_url = self.get_next_page_url(response.content)
            
            if next_page_url:
                search_url = base_url + next_page_url
            
            else:
                search_url = None