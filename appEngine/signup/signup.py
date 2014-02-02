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
import cgi
import hashlib
import re
import random
import string
import webapp2

from google.appengine.ext import db

form='''
<form method="post">
    <b>Sign Up!</b>
    <br>
    <label>  
        Username
        <input type="text" name="username" value="%(username)s">
        
    </label>
    <div style="color:ff0000">%(usernameError)s</div>
    <br>
    <label>
        Password
        <input type="password" name="password" value="%(password)s">
        
    </label>
    <div style="color:ff0000">%(passwordError)s</div>
    <br>    
    <label>
        Verify
        <input type="password" name="verify" value="%(verify)s">
        
    </label>
    <div style="color:ff0000">%(verifyError)s</div>
    <br>    
    <label>
        Email (optional)
        <input type="text" name="email" value="%(mail)s">
        
    </label>
    <div style="color:ff0000">%(mailError)s</div>
    <br>
    <br>        
    <input type="submit">
</form>'''

login='''
<form method="post">
    <b>login!</b>
    <br>
    <label>  
        Username
        <input type="text" name="username" value="%(username)s">
        
    </label>
    <div style="color:ff0000">%(usernameError)s</div>
    <br>
    <label>
        Password
        <input type="password" name="password" value="%(password)s">
        
    </label>
    <div style="color:ff0000">%(passwordError)s</div>
    <br>
    <br>        
    <input type="submit">
</form>
'''

UserRe = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PassRe = re.compile(r"^.{3,20}$")
MailRe = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


class User(db.Model):
    name = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    mail = db.StringProperty(required=False)

class MainHandler(webapp2.RequestHandler):

    def write_form(self, username = "", usernameError = "", passwordError = "", verifyError = "", mail = "", mailError = "", password = "", verify = ""):
	    self.response.write(form % {"username" : cgi.escape(username, quote = True), "usernameError" : cgi.escape(usernameError, quote = True), "passwordError" : cgi.escape(passwordError, quote = True), "verifyError" : cgi.escape(verifyError, quote = True), "mail" : cgi.escape(mail, quote = True), "mailError" : cgi.escape(mailError, quote = True), "password" : cgi.escape(password, quote = True), "verify" : cgi.escape(verify, quote = True) })
	    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        cookie = self.request.cookies.get("user")
        if cookie:
            self.redirect("/welcome")
        else:
            self.write_form()
            
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        userName = self.request.get("username")
        userPass = self.request.get("password")
        userVeri = self.request.get("verify")
        userMail = self.request.get("email")
        usernameError = ""
        passwordError = ""
        mailError = ""
        verifyError = ""
        # Check the user cookie
        cookie = self.request.cookies.get("user")
        if cookie:
            self.redirect("/welcome")

        if not validUserName(userPass):
            usernameError = "That's not a valid username."
        if not validPassWord(userPass):
            passwordError = "That wasn't a valid password."    
        if not validMail(userMail):
            mailError = "That's not a valid email."
        if userPass != userVeri:
            verifyError = "Your passwords didn't match."
            
        if usernameError or passwordError or verifyError:
            self.write_form(userName, usernameError, passwordError, verifyError, userMail, mailError)
        elif mailError:
            self.write_form(userName, usernameError, passwordError, verifyError, userMail, mailError)
        else:
            hashKey = make_pw_hash(userName)
            hashPass = make_pw_hash(userPass)
            newUser = User(name=userName, password=hashPass)
            self.response.headers.add_header("Set-Cookie", "name=%s" % str(userName))
            self.response.headers.add_header("Set-Cookie", "user=%s" % hashKey)
            db.put(newUser)
            self.redirect("/welcome")


def validUserName(userName):
    return UserRe.match(userName)
    
def validPassWord(password):
    return PassRe.match(password)
    
def validMail(mail):
    if mail:
        return MailRe.match(mail)
    else:
        return True

def checkUser(user, password):
    dbUser = db.GqlQuery("Select * From User where name='%s'" % user)
    if dbUser.get():
        print password
        print dbUser.get().password
        return valid_pw(password, dbUser.get().password)
    else:
        return False

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, salt=""):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, h):
    salt = h.split("|")[1]
    hashValue = make_pw_hash(name, salt)
    if h == hashValue:
        return True
    else:
        return False

class SignedUpHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.cookies.get("name")
        user = self.request.cookies.get("user")

        if valid_pw(name, user):
            self.response.write("Welcome, %s!" % name)    
        else:
            self.redirect("/signup")

class LoginHandler(webapp2.RequestHandler):

    def write_login(self, username = "", usernameError = "", passwordError = "", password = ""):
        self.response.write(login % {"username" : cgi.escape(username, quote = True), "usernameError" : cgi.escape(usernameError, quote = True), "passwordError" : cgi.escape(passwordError, quote = True), "password" : cgi.escape(password, quote = True)})


    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        name = self.request.cookies.get("name")
        user = self.request.cookies.get("user")

        #if user:
        #    if valid_pw(name, user):
        #        self.response.write("Welcome, %s!" % name)    
        #else:
        #    self.write_login()
        self.write_login()

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        userName = self.request.get("username")
        userPass = self.request.get("password")

        usernameError = ""
        passwordError = ""

        if not validUserName(userName):
            usernameError = "That's not a valid username."
        if not validPassWord(userPass):
            passwordError = "That wasn't a valid password." 

        resp = checkUser(userName, userPass)

        if resp:
            hashKey = make_pw_hash(userName)
            self.response.headers.add_header("Set-Cookie", "name=%s" % str(userName))
            self.response.headers.add_header("Set-Cookie", "user=%s" % hashKey)
        else:
            usernameError += " Error validating user"

        if usernameError or passwordError:
            self.write_login(userName, usernameError, passwordError)
        else:
            self.redirect("/welcome")

class LogoutHandler(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.delete_cookie('name')
        self.response.delete_cookie('user')
        self.redirect("/signup")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login',LoginHandler),
    ('/signup', MainHandler),
    ('/logout', LogoutHandler),
    ('/welcome', SignedUpHandler)
], debug=True)
