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

form = """
<form method = "post">
    What is your bithday?
    <br>
    <label>
        Month
        <input type="text" name="month" value="%(month)s">
    </label>
    <label>
        Day
        <input type="text" name="day" value="%(day)s">
    </label>
    <label>
        Year
        <input type="text" name="year" value="%(year)s">
    </label>
    <div style="color:ff0000">%(error)s</div>
    <br>
    <input type="submit">
</form>"""


class MainHandler(webapp2.RequestHandler):
    def write_form(self, error="", month="", day="", year=""):
        self.response.write(form % {"error": error, "month": cgi.escape(month, quote=True), "day": cgi.escape(day, quote=True), "year": cgi.escape(year, quote=True)})

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_form()

    def post(self):
        userMonth = self.request.get("month")
        userDay = self.request.get("day")
        userYear = self.request.get("year")

        month = valid_month(userMonth)
        day = valid_day(userDay)
        year = valid_year(userYear)

        if not (month and day and year):
            self.write_form("Something is wrong", userMonth, userDay, userYear)
        else:
            self.redirect("/thanks")


class TestFormHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        q = self.request.get('q')
        self.response.write(q)
        #self.response.write(self.request)

    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        #q = self.request.get('q')
        #self.response.write(q)
        self.response.write(self.request)


class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Valid day Excelent")

    def post(self):
        self.response.write("Valid day Excelent")
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/testform', TestFormHandler),  # le decimos que Clase usar para cada peticion
    ('/thanks', ThanksHandler)
], debug=True)


def valid_year(year):
    if year.isdigit():
        year2 = int(year)
        if year2 > 1899 and year2 < 2021:
            return year2


def valid_day(day):
    if day.isdigit():
        day2 = int(day)
        if (day2 > 0 and day2 < 32):
            return day2

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']


def valid_month(month):
    for i in months:
        if month.upper() == i.upper():
            return i
