
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

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
  

# wire up the views
application = webapp.WSGIApplication([
    ('/', SatSolve)
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
