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
        info_list = json.load(self.request.PUT.multi['customer info'].file.read())
        matches = Customer.query_customers_email(info_list['email'])
        if len(matches) > 0:
            for n in matches:
                if not info_list['trailing'] in n.get().cards:
                    temp = n.get()
                    temp.cards = [temp.cards, info_list['trailing']]
                    temp.put()
        else:
            customer = Customer(first_name=info_list['name'],
                                email=info_list['email'],
                                cards=info_list['trailing'])
            customer.put()
            card = PartialCreditCard(trailing_digits=info_list['trailing'],
                                     leading_digits=info_list['leading'],
                                     card_type=info_list['type'],
                                     start_date=info_list['start'],
                                     expiry_date=info_list['expiry'])
            card.put()

    def get(self):
        customers_key = Customer.query_customers_card(self.request.get("card info"))
        customer = {}
        customers = []
        for n in customers_key:
            customer['name'] = customers_key.get().first_name
            customer['email'] = customers_key.get().email
            customers.append(customer)
        self.response.write(json.dumps(customers))
# [END data manipulation]


# [START app]
app = webapp2.WSGIApplication([
    ('/', DataManip),
], debug=True)
# [END app]
