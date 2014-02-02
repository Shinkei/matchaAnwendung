#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainHandler(Handler):

    def render_front(self):
        posts = db.GqlQuery("Select * From Post Order By created DESC")
        self.render("front.html", posts=posts)

    def get(self):
        self.render_front()


class NewEntryHandler(Handler):

    def render_new_post(self, title="",post="",error=""):
        self.render("newpost.html",title=title, post=post, error=error)

    def get(self):
        self.render_new_post()

    def post(self):
        title = self.request.get("subject")
        post = self.request.get("content")

        if title and post:
            a = Post(title=title, post=post)
            a.put()
            #gqlKey = db.GqlQuery("Select * from Post where title = '%s'" %title)
            key =  a.id()  # gqlKey.get().title
            self.redirect("/"+key)
        else:
            error = "Uppss I did it again"
            self.render_new_post(title, post, error)


class LastPostHandler(Handler):

    def get(self):
        key = self.request.get("key")
        self.response.write(key)
        

app = webapp2.WSGIApplication([('/', MainHandler), ('/newpost', NewEntryHandler), ('/\S+',LastPostHandler)], debug=True)
