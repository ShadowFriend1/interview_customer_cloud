# [START imports]
import json

import webapp2
from google.appengine.ext import ndb


# [END imports]


# [START data definitions]
class Customer(ndb.Model):
    """Sub model for representing a customer"""
    first_name = ndb.StringProperty(indexed=True, required=True)
    email = ndb.StringProperty(indexed=True, required=True)
    cards = ndb.IntegerProperty(indexed=True,
                                repeated=True)

    @classmethod
    def query_customers_card(cls, card_key):
        return cls.query(cards=card_key).order(-cls.first_name)

    @classmethod
    def query_customers_email(cls, email_key):
        return cls.query(email=email_key)


class PartialCreditCard(ndb.Model):
    """Sub model for representing partial credit card information"""
    trailing_digits = ndb.IntegerProperty(indexed=True,
                                          required=True)
    leading_digits = ndb.IntegerProperty(indexed=True)
    card_type = ndb.StringProperty(indexed=True)
    start_date = ndb.DateProperty(indexed=True)
    expiry_date = ndb.DateProperty(indexed=True)
# [END data definitions]


# [START data manipulation]
class DataManip(webapp2.RequestHandler):

    def put(self):
        info_list = json.load(self.request.get('customer info'))
        matches = Customer.query_customers_email(info_list[1])
        if len(matches) > 0:
            for n in matches:
                if not info_list[2] in n.get().cards:
                    temp = n.get()
                    temp.cards = [temp.cards, info_list[2]]
                    temp.put()
        else:
            customer = Customer(first_name=info_list[0],
                                email=info_list[1],
                                cards=info_list[2])
            customer.put()
            card = PartialCreditCard(trailing_digits=info_list[2],
                                     leading_digits=info_list[3],
                                     card_type=info_list[4],
                                     start_date=info_list[5],
                                     expiry_date=info_list[6])
            card.put()

    def get(self):
        customers_key = Customer.query_customers_card(self.request.get("card info"))
        customers = []
        for n in customers_key:
            customers.append(customers_key.get().first_name)
            customers.append(customers_key.get().email)
        self.response.write(json.dump(customers))
# [END data manipulation]


# [START app]
app = webapp2.WSGIApplication([
    ('/', DataManip),
], debug=True)
# [END app]
