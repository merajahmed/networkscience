import os, os.path
import cherrypy
import json
import sys


class BasketBall(object):

    @cherrypy.expose
    def index(self):
        return file('index.html')

    @cherrypy.expose
    def get_game_list(self):
        return json.dumps({})

    @cherrypy.expose
    def get_game_graph(self, **kwargs):
        return




if __name__ == '__main__':
    conf = {
         '/': {
             'tools.sessions.on': True,
         },
         '/generator': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/plain')],
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.root': '/home/meraj/Dropbox/github_repos/networkscience/nbaparsing',
             'tools.staticdir.dir': '/home/meraj/Dropbox/github_repos/networkscience/nbaparsing/static/'
         }
    }
webapp = BasketBall()
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.quickstart(webapp, '/', conf)

