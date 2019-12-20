#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
#from urlparse.urlparse import quote
#import boto3
import time
from datetime import datetime
import json

from google.appengine.api import users,urlfetch
from google.appengine.ext import ndb


import jinja2
import webapp2
from greeting import Greeting
from datamodel import UnifiedGreeting
import random

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# PORT=5001
# HOST="http://127.0.0.1:{}/".format(PORT)
# FETCH_ALL_GREETINGS = HOST + "greetings"

DEFAULT_GUESTBOOK_NAME = 'mydefault-guestbook'

Dynamo_DB_name="Greetings"

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

Display_table="DB"

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        template_values={}
        if Display_table=="DB":
            try:
                UnifiedGreeting_obj=UnifiedGreeting(Dynamo_DB_name)
                greetings,guestbook_name=UnifiedGreeting_obj.getGreetings()
                template_values["greetings"] = greetings
                template_values["guestbook_name"] = guestbook_name
                #print(greetings)
            except urlfetch.InvalidURLError:
                self.response.write("URL is invalid or empty")
            except urlfetch.DownloadError as err:
                self.response.write("Service is unavailable {}".format(err))

        if Display_table=="GAE":
            UnifiedGreeting_obj=UnifiedGreeting(DEFAULT_GUESTBOOK_NAME)
            greetings,guestbook_name=UnifiedGreeting_obj.getGreetings()
            template_values["greetings"] = greetings
            template_values["guestbook_name"] = guestbook_name

        # template_values ={
        #     'greetings':greetings,
        #     'guestbook_name':guestbook_name
        # }
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))




    # def get(self):
    #     guestbook_name = self.request.get('guestbook_name',
    #                                       DEFAULT_GUESTBOOK_NAME)
    #     greetings_query = Greeting.query(
    #         ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
    #     greetings = greetings_query.fetch(10)

    #     template_values = {
    #         'greetings': greetings,
    #         'guestbook_name': guestbook_name
    #     }

    #     template = JINJA_ENVIRONMENT.get_template('index.html')
    #     self.response.write(template.render(template_values))

    # get() for microservices hosted using DynamoDB
    #  def get(self):
    #     try:
    #         url="http://127.0.0.1:5001/greetings"
    #         get_response=urlfetch.fetch(url=url,method=urlfetch.GET)
    #         if get_response.status_code==200:
    #             greetings=json.loads(get_response.content)
    #             #url_content=get_response.content['uri']
    #             #self.response.headers['Content-type'] = "application/json"
    #             #self.response.write(url_content)
    #         else:
    #             self.response.write("Error"+str(get_response.status_code))
    #     except urlfetch.InvalidURLError:
    #         self.response.write("URL is invalid or empty")
    #     except urlfetch.DownloadError:
    #         self.response.write("Service is unavailable")

    #     template_values = {
    #         'greetings': greetings
    #     }
    #     template = JINJA_ENVIRONMENT.get_template('index.html')
    #     #self.response.headers['Content-type'] = "application/json"
    #     self.response.write(template.render(template_values))

# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        gid=random.randint(0, 1000000)
        content=self.request.get('content')
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            UnifiedGreeting_obj=UnifiedGreeting(DEFAULT_GUESTBOOK_NAME)
            greetings_response=UnifiedGreeting_obj.addGreeting(gid,date,content)
            #self.response.out.write(greetings)
        except urlfetch.InvalidURLError:
            self.response.write("URL is invalid or empty")
        except urlfetch.DownloadError:
            self.response.write("Service is unavailable")

        self.redirect("/?")



    # def post(self):
    #     # We set the same parent key on the 'Greeting' to ensure each
    #     # Greeting is in the same entity group. Queries across the
    #     # single entity group will be consistent. However, the write
    #     # rate to a single entity group should be limited to
    #     # ~1/second.
    #     guestbook_name = self.request.get('guestbook_name',
    #                                       DEFAULT_GUESTBOOK_NAME)
    #     greeting = Greeting(parent=guestbook_key(guestbook_name))
    #     greeting.gid = random.randint(0, 1000000)
    #     greeting.content = self.request.get('content')
    #     greeting.put()

    #     query_params = {'guestbook_name': guestbook_name}
    #     self.redirect('/?' + urllib.urlencode(query_params))

    #  def post(self):
    #     gid=random.randint(0, 1000000)
    #     content=self.request.get("content")
    #     date=time.strftime("%Y-%m-%d", time.gmtime())
    #     #date="2019-11-18 23:00:10.969668"
    #     try:
    #         url="http://127.0.0.1:5001/addgreeting/"+str(gid)+"/"+urllib.pathname2url(date)+"/"+urllib.pathname2url(content)
    #         #url="http://127.0.0.1:5001/addgreeting"
    #         #headers = {"Content-Type": "application/json"}
    #         #print(json.dumps({"gid": gid, "date":date, "content":content}))
    #         print(url)

    #         #post_response=urlfetch.fetch(url, method=urlfetch.POST, payload = json.dumps({"gid": gid, "date":date, "content":content}), headers=headers)
    #         post_response=urlfetch.fetch(url, method=urlfetch.POST)
    #         print(post_response.content)
    #         if post_response.status_code==200:
    #             url_content=json.loads(post_response.content)
    #             #self.response.headers['Content-type'] = "application/json"
    #             #self.response.out.write(post_response.content)
    #         else:
    #             self.response.write("Error"+str(post_response.status_code)+str(url))
    #             #pass
    #     except urlfetch.InvalidURLError:
    #         self.response.write("URL is invalid or empty")
    #         #pass
    #     except urlfetch.DownloadError:
    #         self.response.write("Service is unavailable")
    #     self.redirect("/?")
# [END guestbook]


# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
# [END app]
