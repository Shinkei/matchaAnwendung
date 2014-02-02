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
import cgi

form = '''
        <form method="post">
        <b>Enter some text to rot13:</b>
        <br>
        <textarea name="text">%(rot13Value)s</textarea>
        <br>
        <input type="submit">
        </form>
'''

class MainHandler(webapp2.RequestHandler):

    def write_form(self, rot13Value = ""):
	    self.response.write(form % {"rot13Value" : cgi.escape(rot13Value, quote = True)})
	
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        userValue  = self.request.get("text")
        self.write_form(rot13(userValue))
        
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        userValue  = self.request.get("text")
        self.write_form(rot13(userValue))    

upper = map(chr, range(65, 91)+range(65, 91))
lower = map(chr, range(97, 123)+range(97,123))

def rot13(text):
    result = ""
    for letter in text:
        result = result+add13(letter)
    return result    

def add13(letter):
    if letter in upper:
        position = upper.index(letter)
        return upper[position + 13]
    elif letter in lower:
        position = lower.index(letter)
        return lower[position + 13]
    else:
        return letter
    
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
