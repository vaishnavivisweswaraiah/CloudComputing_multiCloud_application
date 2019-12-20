
import abc
import random
import json
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from greeting import Greeting

"""
command to execute:python2 /Users/vaishnaviv/CC_GCP/google-cloud-sdk/platform/google_appengine/dev_appserver.py app.yaml
"""

DEFAULT_GUESTBOOK_NAME = 'mydefault-guestbook'

Dynamo_DB_name="Greetings"
#IF running locally use as is.For test purpose run locally
HOST="http://127.0.0.1:5001"

#IF running on ec2 instance uncomment below code
#HOST = "http://ec2-54-91-119-236.compute-1.amazonaws.com"

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

# the base class
class GreetingModel:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getGreetings(self):
        pass
    @abc.abstractmethod
    def addGreeting(self, gid, date, content):
        pass



class GAEGreeting(GreetingModel):
    def __init__(self, guestbook_name):
        # constructor, initialize anything you need
        # Initialize the guestbook_name which is specific to each type Datastore model(GAE datastore ndb name or Dynamodb table name)
        self.guestbook_name=guestbook_name
        pass

    def getGreetings(self):
        # Fetch the greetings from GAE guestbook entry and return greetings and guestbook name 
        greetings_query = Greeting.query(
        ancestor=guestbook_key(self.guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        
        return greetings,self.guestbook_name

    def addGreeting(self, gid, date, content):
        # to do
        greeting = Greeting(parent=guestbook_key(self.guestbook_name))
        greeting.gid = gid
        greeting.content = content
        #greeting.date=date
        greeting.put()
        return greeting.date

class DynamoGreeting(GreetingModel):
    def __init__(self, guestbook_name):
        # to do
        self.guestbook_name=guestbook_name

    def getGreetings(self):
        # to do
            #fetch reponse from microservice and returns guetbookname and content as greeting items from dynamo DB
            
            #url="http://127.0.0.1:5001/greetings"
            #url="http://ec2-54-165-158-186.compute-1.amazonaws.com/greetings"
            url = HOST+"/greetings"
            get_response=urlfetch.fetch(url=url,method=urlfetch.GET)
            #print(get_response)
            if get_response.status_code==200:
                    greetings=json.loads(get_response.content)
            else:
                greetings="Error"+str(get_response.status_code)

            return greetings,self.guestbook_name

    def addGreeting(self, gid, date, content):
        # Content entered in guestbook form is passed into the post request and status of request is returned.
        
            #url="http://127.0.0.1:5001/addgreeting/"+str(gid)+"/"+urllib.pathname2url(date)+"/"+urllib.pathname2url(content)
            #url="http://ec2-54-165-158-186.compute-1.amazonaws.com/addgreeting/"+str(gid)+"/"+urllib.pathname2url(date)+"/"+urllib.pathname2url(content)
            url = HOST+"/addgreeting/"+str(gid)+"/"+urllib.pathname2url(date)+"/"+urllib.pathname2url(content)
            post_response=urlfetch.fetch(url, method="POST")
            if post_response.status_code==200:
                    greetings=json.loads(post_response.content)
                    #self.response.headers['Content-type'] = "application/json"
                    #self.response.out.write(dynamo_post_reponse.content)
            else:
                greetings="Error"+str(post_response.status_code)
            
            #here greetings is a  status of the request which is used for test purpose.
            return greetings

class UnifiedGreeting(GreetingModel):
    def __init__(self, guestbook_name):
        # create both GAE and Dynamo Models
        # the UnifiedGreeting model will be used by the GAE main program
        # to do
        self.guestbook_name=guestbook_name


    def getGreetings(self):
        # pick one model to get all greetings
        # to do
        #return greeting items to GAE main program(or where function is called based on type of model(DynamoDb or GAE datamodel) the data is requested from.)
        # if guestbook_name is "Greetings" then dynamo DB will be picked
        if self.guestbook_name==Dynamo_DB_name:
            Dynamo_obj=DynamoGreeting(Dynamo_DB_name)
            greeting_data=Dynamo_obj.getGreetings()

        #if guestbook_name is  "mydefault-guestbook"  GAE DB data will be picked
        if self.guestbook_name==DEFAULT_GUESTBOOK_NAME:
            GAE_obj=GAEGreeting(DEFAULT_GUESTBOOK_NAME)
            greeting_data=GAE_obj.getGreetings()

        return greeting_data

    def addGreeting(self, gid, date, content):
        # append the new record to both models
        # Adds record to both Models any exceptions during these operations is handled in GAE "Guestbook.py"

        GAE_obj=GAEGreeting(DEFAULT_GUESTBOOK_NAME)
        gae_date=GAE_obj.addGreeting(gid,date,content)

        Dynamo_obj=DynamoGreeting(Dynamo_DB_name)
        greetings_response = Dynamo_obj.addGreeting(gid,str(gae_date),content)

        return greetings_response
