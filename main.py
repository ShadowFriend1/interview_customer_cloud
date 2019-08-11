# [START imports]
import json
from datetime import datetime
import webapp2
from google.appengine.ext import ndb
# [END imports]


# [START data definitions]
class PartialCreditCard(ndb.Model):
    """Sub model for representing partial credit card information"""
    trailing_digits = ndb.IntegerProperty(indexed=True,
                                          required=True)
    leading_digits = ndb.IntegerProperty(indexed=True)
    card_type = ndb.StringProperty(indexed=True)
    start_date = ndb.DateProperty(indexed=True)
    expiry_date = ndb.DateProperty(indexed=True)


class Customer(ndb.Model):
    """Sub model for representing a customer"""
    first_name = ndb.StringProperty(indexed=True, required=True)
    email = ndb.StringProperty(indexed=True, required=True)
    cards = ndb.StructuredProperty(PartialCreditCard, indexed=True, repeated=True)
# [END data definitions]


# [START data manipulation]
class DataManip(webapp2.RequestHandler):

    def put(self):
        info_list = json.loads(self.request.body)

        card = PartialCreditCard(trailing_digits=info_list['trailing'])
        try:
            card.leading_digits = info_list['leading']
        except KeyError:
            self.response.write("no leading digits /n")
        try:
            card.card_type = info_list['type']
        except KeyError:
            self.response.write("no card type /n")
        try:
            card.start_date = datetime.strptime(info_list['start'], '%Y %m %d')
        except KeyError:
            self.response.write("no start date /n")
        try:
            card.expiry_date = datetime.strptime(info_list['expiry'], '%Y %m %d')
        except KeyError:
            self.response.write("no expiry date /n")
        self.response.write(card.trailing_digits)
        matches = Customer.query(Customer.email == info_list['email']).fetch()
        if len(matches) > 0:
            for n in matches:
                if not len(Customer.query(
                        Customer.cards == PartialCreditCard(trailing_digits=info_list['trailing'])).fetch()) > 0:
                    n.cards = [n.cards, card]
                    n.put()
                    self.response.write("card added to customer /n")
            self.response.write("added to matching customers /n")
        else:
            customer = Customer(first_name=info_list['name'],
                                email=info_list['email'],
                                cards=[card])
            customer.put()
            self.response.write("created new customer /n")

    def get(self):
        card_info = self.request.get("card info")
        card_info = int(card_info)
        customers_key = Customer.query(
            Customer.cards == PartialCreditCard(trailing_digits=card_info)).order(Customer.first_name).fetch()
        customer = {}
        customers = []
        for n in customers_key:
            customer['name'] = n.first_name
            customer['email'] = n.email
            customers.append(customer)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(customers))
# [END data manipulation]


# [START app]
app = webapp2.WSGIApplication([
    ('/', DataManip),
], debug=True)
# [END app]
