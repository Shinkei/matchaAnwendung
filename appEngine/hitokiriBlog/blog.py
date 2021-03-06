import os
import re
import time

from string import letters

import webapp2
import jinja2

from signup import *

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import GqlQuery

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def render_json_blog(post):
    container = ""
    json = '{"content":"%s", "created":"%s", "last_modified":"%s", "subject":"%s"}'
    if post:
        if isinstance(post, GqlQuery):
            container = "["
            coma = 1
            for p in post:
                container += json % (p.content, p.created.strftime("%a %b %d %H:%M:%S %Y"), p.last_modified.strftime("%a %b %d %H:%M:%S %Y"), p.subject)
                container += ","
            container = container[:-1]+"]"
        else:
            # %c in the format has the same representation as the one up
            container = json % (post.content, post.created.strftime("%c"), post.last_modified.strftime("%c"), post.subject)
    return container

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
    def get(self):
        name = self.request.cookies.get("name")
        user = self.request.cookies.get("user")

        if valid_pw(name, user):
            self.response.write("Welcome, %s!" % name)    
        else:
            self.redirect("/blog/signup")

##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        time_cached = memcache.get("time")
        if time_cached:
            now = time.time()
            calculated_time = now - time_cached
        else:
            calculated_time = 0.0
            memcache.set("time", time.time())

        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        if self.request.url.endswith('.json'):
            self.response.headers['Content-Type'] = 'application/json'
            if posts.count() > 0:
                self.response.write(render_json_blog(posts))
            else:
                self.response.write(render_json_blog(None))
        else:
            self.render('front.html', posts = posts, time=int(calculated_time))

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        time_cached = memcache.get(post_id)
        if time_cached:
            now = time.time()
            calculated_time = now - time_cached
        else:
            calculated_time = 0.0
            memcache.set(post_id, time.time())

        if not post:
            self.error(404)
            return
        if self.request.url.endswith('.json'):
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(render_json_blog(post))
        else:
            self.render("permalink.html", post = post, time=int(calculated_time))

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)



###### Unit 2 HW's
class Rot13(BlogHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')

        self.render('rot13-form.html', text = rot13)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):

    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.redirect('/unit2/welcome?username=' + username)

class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')

class FlushHandler(BlogHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/blog')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/welcome', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Signup),
                               ('/unit2/welcome', Welcome),
                               ('/blog/?(?:.json)?', BlogFront),
                               #('/blog/?', BlogFront),
                               #('/blog/.json', BlogFront),
                               ('/blog/([0-9]+)(?:.json)?', PostPage),
                               #('/blog/([0-9]+)', PostPage),
                               #('/blog/([0-9]+).json', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/login',LoginHandler),
                               ('/blog/signup', MainHandler),
                               ('/blog/logout', LogoutHandler),
                               ('/blog/flush', FlushHandler),
                               ],
                              debug=True)
