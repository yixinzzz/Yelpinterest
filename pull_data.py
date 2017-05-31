from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from bs4 import BeautifulSoup
import re
import urllib
from flask import Flask

app = Flask(__name__)

def connect_API(consumer_key=None, consumer_secret=None, token=None, token_secret=None):
    """ Yelp API authorization
    :param consumer_key: Yelp API consumer_key
    :param consumer_secret: Yelp API consumer_secret
    :param token: Yelp API token
    :param token_secret: Yelp API token_secret
    :return: Yelp API client object
    """
    auth = Oauth1Authenticator(consumer_key, consumer_secret, token, token_secret)
    return Client(auth)

def get_businesses(client, keywords, location):
    """
    get Yelp business objects
    :param client: Yelp API client object
    :param keywords: name of a dish
    :param location: city name
    :return: a list of Yelp business object from responses
    """
    params = {
        'term': keywords
    }
    return client.search(location, **params).businesses

def get_data(business_id, keywords):
    """
    pull reviews and photos
    :param business_id: a Yelp business id
    :param keywords: name of a dish
    :return: a list of reviews and a list of photos relative to the keywords
    """

    # data in 1st page
    reviews = []
    photos = []
    SearchURL = 'https://www.yelp.com/biz_photos/%s?tab=food' % business_id
    try:
        yelppage = BeautifulSoup(urllib.urlopen(SearchURL).read(), "lxml")
        total_pages = yelppage.find_all('div', {'class': "page-of-pages arrange_unit arrange_unit--fill"})[0].get_text()
        total_pages = int(re.findall('of ([0-9]*)', total_pages)[0])
        reviews, photos = get_data_single_page(yelppage, keywords)
        # data in other pages (only get data from first 5 pages; otherwise, it's going to be super slow)
        if total_pages > 5:
            total_pages = 5
        for page in range(1, total_pages):
            num = 30*page
            SearchURL = 'https://www.yelp.com/biz_photos/%s?start=%s&tab=food' % (business_id, str(num))
            yelppage = BeautifulSoup(urllib.urlopen(SearchURL).read(), "lxml")
            r, p = get_data_single_page(yelppage, keywords)
            reviews += r
            photos += p
    except UnicodeError:
        pass
    return reviews, photos

def get_data_single_page(yelppage, keywords):
    """
    helper method for get_data
    :param yelppage: BeautifulSoup object
    :return: a list of reviews and a list of photos relative to the keywords
    """
    results = yelppage.find_all('img', {'alt': re.compile(" " + keywords + " ", re.IGNORECASE)})
    reviews = []
    photos = []
    for result in results:
        r = result.get("alt").split(".")
        if len(r) > 1:
            reviews.append(r[1])
            photos.append(result.get("src"))
    return reviews, photos

@app.route("/search/<keywords>")
def find_food(keywords, location = "San Francisco, CA"):
    """
    get restaurant information from searching results
    :param keywords: keywords for the dish
    :param location: city name
    :return: a dictionary of result (key - business_id, value - review list, photo list, business object)
    """
    consumer_key = "8WhklGO_09rGkQZy9xMBQQ"
    consumer_secret = "aSYhuXHB0U__JcYxWmBU-qm5a5k"
    token = "ud25l_lGjq4PJPqxX_NXhSQHCbXWdZjq"
    token_secret = "n4jTgD1PzwiWCSVg-hHac8WHx8o"
    client = connect_API(consumer_key, consumer_secret, token, token_secret)
    businesses_list = get_businesses(client, keywords, location)

    info_dict = {}
    for business in businesses_list:
        id = business.id
        # print id
        reviews, photos = get_data(id, keywords)
        if len(reviews) > 0:
            info_dict[id] = {"reviews": reviews}
            info_dict[id]["photos"] = photos
            info_dict[id]["business_obj"] = business
    return "\n".join(info_dict.keys())

@app.route("/search", methods = ["POST"])
def search_app():
    keywords = request.form.get('food name')
    return find_food(keywords)

@app.route("/")
def welcome():
    return "Welcome to Yelpinterest!"

# main
if __name__ == "__main__":
    app.run()


