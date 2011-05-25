import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import lastfm

key = '087eea10b5cbda43d230f8cb2b9a7272'
secret = '90bcc69c48c50acc5269d588c55aebec'


class Index(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
    self.response.out.write(template.render(path, {}))


class GetFriends(webapp.RequestHandler):
  def get(self):
    from django.utils.simplejson import dumps
    api = lastfm.api.Api(key)
    user = lastfm.user.User(api, name=self.request.get('user'))
    friends = user.get_friends(limit=0)
    friends = [f.name for f in friends]
    self.response.out.write(dumps(friends))


class CompareFriends(webapp.RequestHandler):
  def get(self):
    from django.utils.simplejson import dumps
    api = lastfm.api.Api(key)
    user = lastfm.user.User(api, name=self.request.get('user'))
    score = user.compare(self.request.get('friend')).score * 100
    self.response.out.write(dumps(score))


def main():
  url_mapping = [
      (r'^/$', Index),
      (r'^/friends$', GetFriends),
      (r'^/compare$', CompareFriends),
      ]
  application = webapp.WSGIApplication(url_mapping, debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
