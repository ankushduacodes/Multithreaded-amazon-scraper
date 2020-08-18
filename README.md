# amazon-search-scraper

# Description
This package allows you to search and scrape for products on [Amazon](https://www.amazon.com) and extract some useful information (price, ratings, number of comments).

# Requirements
- Python 3
- pip3

# Dependencies
```bash
pip3 install -r requirements.txt
```

# Usage
1. Clone this repo or zip download it.
2. Open a terminal or cmd at download folder directory
3. run:
```bash 
python3 example.py -w <word you want to search>
```
4. Above step with create a .json file(in same directory as example.py) with the products that were found.
5. For more help just run:
```bash 
python3 example.py --help
```

### Information fetched

Attribute name      | Description
------------------- | ---------------------------------------
url                 | Product URL
title               | Product title
price               | Product price
rating              | Rating of the products
review_count        | Number of customer reviews
img_url             | Image URL
bestseller          | Tells whether a product is best seller or not
prime               | Tells if product is supported by Amazon prime or not
asin                | Product ASIN ([Amazon Standard Identification Number](https://fr.wikipedia.org/wiki/Amazon_Standard_Identification_Number))

### Output Format
Output is provided in the from of a json file, please refer to the [products.json](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/products.json) as an example file which was produced with search word 'toaster'

# Design Decisions
1. scraper.py, In method [get_page_content](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/amazon_scraper_module/scraper.py#L102), retries were added to make a valid connection with amazon servers even if it connection request was denied.

2. function -> [get_request](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/amazon_scraper_module/scraper.py#L56), returns None when requests.exceptions.ConnectionError occurs and ripples its way down to calling functions to terminate the thread normally instead of abruptly calling sys.exit() which surely will kill the thread but if the thread being killed holds GIL component, in that case it will lead to [Deadlock](https://en.wikipedia.org/wiki/Deadlock).

3. function -> [get_page_content](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/amazon_scraper_module/scraper.py#L102), if no valid page was found even after retries it returns None in addition to returning None for Nonetype response from get_request.

4. Decision number 2 and 3 were made keeping in mind that in a multithreaded program, multiple threads are working simultaneously, while doing that there may be a case where 1 or 2 out of 10 or 20 threads does not get valid response (Please check [check_page_validity](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/amazon_scraper_module/scraper.py#L83[) and [get_request](https://github.com/ankushduacodes/amazon-search-scraper/blob/master/amazon_scraper_module/scraper.py#L56) function for documentation and more), then we terminate only those threads safely while others work to produce the valid output.

# Performance Benchmark
On my network connection (results may vary depending on your connection speed)

Number of pages     | Number of products | Time              |
--------------------|--------------------|-------------------|
 1                  | 22                 | 2.657             |
 3                  | 126                | 4.007 sec         |
 7                  | 390                | 8.094 sec         |
 20                 | 426                | 12.534 sec        |
--------------------------------------------------------------

## Future Imporvements
- [ ] Write Unit tests
- [ ] Implement functionality of sending requests from various differnt proxies
- [ ] Items like Books and DVDs may have multiple prices, Extact all the prices and categorize them into a price dictionary
- [ ] Add a better way to convert list of objects into json
- [ ] To handle special characters in the content scraped from Amazon
