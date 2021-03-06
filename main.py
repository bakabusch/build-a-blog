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

import os
import webapp2
import jinja2
import cgi
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

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")


class Blogger(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, blog=blog, error=error, blogs=blogs )

    def get(self):
        self.render_front()

    #def post(self):
    #    title = self.request.get("title")
    #    blog = self.request.get("blog")

    #    if title and blog:
    #        a = Blog(title = title, blog = blog)
    #        a.put()
    #        self.redirect("/blog")
    #    else:
    #        error = "We need both a title and blogpost bro"
    #        self.render_front(title, blog, error)

class NewPage(Handler):
    def render_front(self, title="", blog="", error=""):
#        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("newpage.html", title=title, blog=blog, error=error)
#, blogs=blogs taken out from above
    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()
            self.redirect("/blog/%s" % str(a.key().id()))
        else:
            error = "We need both a title and a blogpost bro"
            self.render_front(title, blog, error)

class ViewPostHandler(Handler): #trying to display individual blogpost
    def get(self, id):
        idint= int(id)
        idiot= Blog.get_by_id(idint)
        idiot.key().id()

        if idiot:
            self.render("singleblog.html", idiot=idiot)
        else:
            error= "going no where fast buddy"
            self.response.write(error)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blogger),
    ('/newpost', NewPage),
     webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
