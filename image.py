#!/usr/bin/python


from PIL import Image
import requests, os
from log import print_exc, log
import StringIO


SIZE = (1024, 1024)
MAX_IMAGE_FILE_SIZE = 1024*1024
NEW_MAIN_IMAGE_PATH = 'newmap.png'
MAIN_IMAGE_PATH = 'map.png'


def get_fn(id_):
	return 'images/%s.png' % (id_,)

def load_image(id_, url):
	fn = get_fn(id_)
	if not os.path.isfile(fn):
		r = requests.get(url)
		if r.status_code != 200:
			raise Exception('%d (%s)' % (r.status_code, r.reason))

		l = int(r.headers['Content-Length'])
		if l > MAX_IMAGE_FILE_SIZE:
			raise Exception('Too big image (%d)' % (l,))

		ct = r.headers['Content-Type']
		if ct == 'image/png':
			f = open(fn, 'w')
			f.write(r.content)
			f.close()
		else:
			raise Exception('Wrong Content-Type (%s)' % (ct,))
	im = Image.open(fn, 'r')
	return im.size

def create_main_image(orders):
	log('Create main image')
	main_im = Image.new('RGBA', SIZE, 'white')
	for id_, t, sender, payment, period, url, x, y, sx, sy in orders:
		try:
			fn = get_fn(id_)
			im = Image.open(fn, 'r')
			sim = im.split()
			print len(sim)
			if len(sim) == 4:
				main_im.paste(im, (x, y), mask=sim[3])
			else:
				main_im.paste(im, (x, y))
		except Exception as exc:
			print_exc(exc)

	main_im.save(NEW_MAIN_IMAGE_PATH)

def image_stream(im, fmt = 'png'):
	res = StringIO.StringIO()
	im.save(res, fmt)
	res.seek(0)
	return res

def load_image(fn):
	return Image.open(fn, 'r')

