#!/usr/bin/python


from image import load_main_image, image_stream, NEW_MAIN_IMAGE_PATH, MAIN_IMAGE_PATH
import cherrypy, os
from cherrypy.lib import file_generator
from db import DB
from log import log


def table(data):
	trs = []
	for row in data:
		tds = []
		for cell in row:
			tds.append('<td>%s</td>' % (str(cell),))
		trs.append('\t<tr> %s </tr>' % (' '.join(tds)))
	return '<table width="100%%" border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">\n%s\n</table>\n' % ('\n'.join(trs))

class CounterServer(object):
	def __init__(self):
		object.__init__(self)
		self._lastTime = None
		self._im = None

	@cherrypy.expose
	def db(self):
		with DB() as db:
			res = db.execute('SELECT * FROM orders')
			res = res.fetchall()
			res = table(res)
		client = cherrypy.request.remote
		cherrypy.response.headers['Content-type'] = 'text/html'
		return res

	def default(self, attr=''):
		if os.path.isfile(NEW_MAIN_IMAGE_PATH):
			log('New main image')
			try:
				os.remove(MAIN_IMAGE_PATH)
			except:
				pass
			os.rename(NEW_MAIN_IMAGE_PATH, MAIN_IMAGE_PATH)
			self._im = None
		if not self._im:
			log('Load main image')
			try:
				self._im = load_main_image(MAIN_IMAGE_PATH)
			except:
				self._im = None
		if self._im:
			cherrypy.response.headers['Content-type'] = 'image/png'
			return file_generator(image_stream(self._im))

		return 'Oops!'

	default.exposed = True

if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host':'0.0.0.0', 'server.socket_port': 80})
	cherrypy.quickstart(CounterServer())

