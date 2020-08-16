class Product(object):

    def __init__(self, url='', title='', price=None, img_url='', rating_stars='', review_count=None, bestseller=False, prime=False):

        self.url = url
        self.title = title
        self.price = price
        self.img_url = img_url
        self.rating_stars = rating_stars
        self.review_count = review_count
        self.bestseller = bestseller
        self.prime = prime
