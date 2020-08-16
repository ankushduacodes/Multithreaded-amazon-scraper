class Product(object):

    def __init__(self, url='', title='', price=None, img_url='', rating_stars='', num_of_reviews=None, bestseller=False, prime=False):

        _id = count(0)
        self.id = next(self._id)
        self.url = url
        self.title = title
        self.price = price
        self.img_url = img_url
        self.rating_stars = rating_stars
        self.num_of_reviews = num_of_reviews
        self.bestseller = bestseller
        self.prime = prime
