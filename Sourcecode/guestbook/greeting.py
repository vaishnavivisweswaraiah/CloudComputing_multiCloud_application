from google.appengine.ext import ndb


# [START greeting]

class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    gid = ndb.IntegerProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


