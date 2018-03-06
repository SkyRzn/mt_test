#!/usr/bin/python


from image import load_image, image_stream, NEW_MAIN_IMAGE_PATH, MAIN_IMAGE_PATH
import cherrypy, os
from cherrypy.lib import file_generator


class CounterServer(object):
	def __init__(self):
		object.__init__(self)
		self._lastTime = None
		self._im = None

	def default(self, attr=''):
		if os.path.isfile(NEW_MAIN_IMAGE_PATH):
			os.remove(MAIN_IMAGE_PATH)
			os.rename(NEW_MAIN_IMAGE_PATH, MAIN_IMAGE_PATH)
			self._im = None
		if not self._im:
			im = load_image(MAIN_IMAGE_PATH)
		cherrypy.response.headers['Content-type'] = 'image/png'
		return file_generator(image_stream(self._im))

	default.exposed = True

if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host':'0.0.0.0', 'server.socket_port': 80})
	cherrypy.quickstart(CounterServer())

