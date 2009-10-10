"""
Provides a protected administrative area for uploading and deleteing images
"""

import os
import datetime

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.api import users

from models import Image


class SatSolve(webapp.RequestHandler):
  
  
  
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write("""
  
    class SolutionFound(BaseException):
    def __init__(self):
      self.s = []

  def assign(clauses, val):
    n = []
    for c in clauses:
      if val in c:
        continue
      elif -val in c:
        n.append([x for x in c if x != -val])
      else:
        n.append(c)
    return n

  def try_sat(clauses, val):
    try:
      solve_sat(assign(clauses, val))
    except SolutionFound, s:
      s.s.append(val)
      raise s

  def solve_sat(clauses):
    if [] in clauses:
      return
    if len(clauses) == 0:
      raise SolutionFound()
    for x in clauses:
      if len(x) == 1:
        try_sat(clauses, x[0])
        return
    smallest = clauses[0]
    for c in clauses:
      if c[0] > 0 and (smallest[0] < 0 or len(smallest) > len(c)):
        smallest = c
    try_sat(clauses, smallest[0])
    try_sat(clauses, -smallest[0])

  svals = [list(range(x, x+9)) for x in range(0, 81, 9)] + \
      [list(range(x, x+81, 9)) for x in range(9)] + \
      [[x,x+1,x+2,x+9,x+10,x+11,x+18,x+19,x+20] for x in [0,3,6,27,30,33,54,57,60]]

  def group(c, p):
    p.append(c)
    for i in range(len(c)):
      for j in range(i):
        p.append([-c[i], -c[j]])

  def groups(c, p):
    for i in range(9):
      group([x + 100 * i + 1 for x in c], p)

  def decode(r):
    r2 = [[0 for x in range(9)] for y in range(9)]
    for v in r:
      if v > 0:
        pos = (v-1) % 100
        r2[pos // 9][pos % 9] = (v // 100) + 1
    return r2

  def solve_sudoku(problem):
    p = []
    for i in range(81):
      group(list(range(i+1, 901, 100)), p)
    for s in svals:
      groups(s, p)
    pre = []
    for x in range(9):
      for y in range(9):
        if problem[x][y]:
          m = x * 9 + y + 100 * (problem[x][y] - 1) + 1
          pre.append(m)
          p = assign(p, m)
    try:
      solve_sat(p)
    except SolutionFound, s:
      return decode(s.s + pre)
    return None

  import sys
  sys.setrecursionlimit(10000)

  if __name__ == '__main__':
    tt = [[0] * 9 for i in range(9)]
    print('\n'.join(' '.join([str(p) for p in q]) for q in solve_sudoku(tt)))
    print(' ')
    tt[0][0] = 6
    tt[3][4] = 1
    print('\n'.join(' '.join([str(p) for p in q]) for q in solve_sudoku(tt)))
    
  """)
  
  
class Index(webapp.RequestHandler):
    """
    Main view for the application.
    Protected to logged in users only.
    """
    def get(self):
        "Responds to GET requets with the admin interface"
        # query the datastore for images owned by
        # the current user. You can't see anyone elses images
        # in the admin
        images = Image.all()
        images.filter("user =", users.get_current_user())
        images.order("-date")

        # we are enforcing loggins so we know we have a user
        user = users.get_current_user()
        # we need the logout url for the frontend
        logout = users.create_logout_url("/")

        # prepare the context for the template
        context = {
            "images": images,
            "logout": logout,
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))

class Deleter(webapp.RequestHandler):
    "Deals with deleting images"
    def post(self):
        "Delete a given image"
        # we get the user as you can only delete your own images
        user = users.get_current_user()
        image = db.get(self.request.get("key"))
        # check that we own this image
        if image.user == user:
            image.delete()
        # whatever happens rediect back to the main admin view
        self.redirect('/')
       
class Uploader(webapp.RequestHandler):
    "Deals with uploading new images to the datastore"
    def post(self):
        "Upload via a multitype POST message"
        
        try:
            # check we have numerical width and height values
            width = int(self.request.get("width"))
            height = int(self.request.get("height"))
        except ValueError:
            # if we don't have valid width and height values
            # then just use the original image
            image_content = self.request.get("img")
        else:
            # if we have valid width and height values
            # then resize according to those values
            image_content = images.resize(self.request.get("img"), width, height)
        
        # get the image data from the form
        original_content = self.request.get("img")
        # always generate a thumbnail for use on the admin page
        thumb_content = images.resize(self.request.get("img"), 100, 100)
        
        # create the image object
        image = Image()
        # and set the properties to the relevant values
        image.image = db.Blob(image_content)
        # we always store the original here in case of errors
        # although it's currently not exposed via the frontend
        image.original = db.Blob(original_content)
        image.thumb = db.Blob(thumb_content)
        image.user = users.get_current_user()
                
        # store the image in the datasore
        image.put()
        # and redirect back to the admin page
        self.redirect('/')
                
# wire up the views
application = webapp.WSGIApplication([
    ('/', SatSolve),#Index),
    ('/upload', Uploader),
    ('/delete', Deleter)
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
