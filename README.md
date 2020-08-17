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

### Attributes of the `Product` object

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
