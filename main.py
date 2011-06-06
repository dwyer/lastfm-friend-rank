import os

from google.appengine.api import memcache
from google.appengine.api import taskqueue

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

import lastfm

key = '087eea10b5cbda43d230f8cb2b9a7272'


def get_user(name):
  # TODO: can't pickle lastfm's User; find workaround
  user = None # memcache.get(name)
  if not user:
    api = lastfm.api.Api(key)
    user = lastfm.user.User(api, name=name)
    #memcache.set(name, user)
  return user  


class Index(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
    self.response.out.write(template.render(path, {}))


class GetFriends(webapp.RequestHandler):
  def get(self):
    from django.utils.simplejson import dumps
    user = get_user(self.request.get('user'))
    friends = user.get_friends(limit=0)
    friends = [f.name for f in friends]
    self.response.out.write(dumps(friends))


class CompareFriends(webapp.RequestHandler):
  def get(self):
    from django.utils.simplejson import dumps
    user = get_user(self.request.get('user'))
    score = user.compare(self.request.get('friend')).score * 100
    self.response.out.write(dumps(score))


class XmppHandler(xmpp_handlers.BaseHandler):
  def message_received(self, message=None):
    taskqueue.add(params=self.request.POST)
    message.reply('Hang on a second while we do the math...')


class QueueHandler(xmpp_handlers.BaseHandler):
  def message_received(self, message=None):
    try:
      from urllib import urlencode
      from google.appengine.api import urlfetch
      from django.utils.simplejson import loads
      api = lastfm.api.Api(key)
      user = lastfm.user.User(api, name=message.body)
      friends = user.get_friends(limit=0)
      base_url = 'http://ws.audioscrobbler.com/2.0/'
      params = {
          'format': 'json',
          'method': 'tasteometer.compare',
          'type1': 'user',
          'type2': 'user',
          'value1': user.name,
          'value2': None,
          'api_key': key,
          }
      # make all the necessary RPC calls
      for friend in friends:
        friend.rpc = urlfetch.create_rpc()
        query_string = urlencode(dict(params, value2=friend.name))
        url = '?'.join((base_url, query_string))
        urlfetch.make_fetch_call(friend.rpc, url)
      # start collecting RPC results
      for friend in friends:
        try:
          result = friend.rpc.get_result()
          if result.status_code == 200:
            object = loads(result.content)
            friend.score = float(object['comparison']['result']['score']) * 100
          else:
            raise urlfetch.DownloadError
        except urlfetch.DownloadError:
          friend.score = -1
      friends.sort(lambda a, b: cmp(b.score, a.score))
      lines = ['%s\'s top 10:' % (user.name)]
      for i, friend in enumerate(friends[:10]):
        lines.append('%d. %s (%s%%)' % (i+1, friend.name, friend.score))
      message.reply('\n'.join(lines))
    except Exception, e:
      message.reply(str(e))


def main():
  url_mapping = [
      ('/', Index),
      ('/friends', GetFriends),
      ('/compare', CompareFriends),
      ('/_ah/xmpp/message/chat/', XmppHandler),
      ('/_ah/queue/default', QueueHandler),
      ]
  application = webapp.WSGIApplication(url_mapping, debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
