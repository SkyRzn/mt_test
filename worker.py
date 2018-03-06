#!/usr/bin/python


import sys, os, requests, json, base58, time
from image import load_image, create_main_image
from log import print_exc, log
from db import DB


def remove_orders(orders):
	cnt = len(orders)
	if cnt == 0:
		return
	log('Remove %d expired orders' % (cnt,))

def orders_split(orders):
	active = []
	expired = []
	cur_t = time.time()*1000
	for order in orders:
		id_, t, sender, payment, period, url, x, y, sx, sy = order
		if t + period <= cur_t:
			active.append(order)
		else:
			expired.append(order)
	return active, expired

def work():
	try:
		with DB() as db:
			address = db.get_var_text('address')
			expired_time = db.get_var_text('expired_time')
			loaded_time = db.get_var_text('loaded_time')

			r = requests.get('https://nodes.wavesplatform.com/transactions/address/%s/limit/10' % address) #FIXME repeat
			if r.status_code != 200:
				err = '%d (%s)' % (r.status_code, r.reason)
				if r.text:
					err += '\nResult: %s' % (r.text,)
				raise Exception(err)

			transactions = json.loads(r.text)[0]

			orders_added = 0
			for tr in transactions:
				try:
					id_ = tr['id'] #FIXME checks

					if db.has_order(id_):
						continue

					type_ = int(tr['type'])
					if type_ != 4: # transfer
						continue
					sender = tr['sender'] #FIXME checks
					payment = float(tr['amount'])/1000
					timestamp = float(tr['timestamp'])
					url = tr['attachment'] #FIXME checks
					url = base58.b58decode(url) #FIXME checks
					coords = url.split(',')
					url = ','.join(coords[2:])
					coords = coords[:2]
					coords = map(int, coords)

					size = load_image(id_, url)

					if size == None:
						size = (0, 0)

					orders_added += db.add_order(id_, timestamp, sender, payment, url, coords, size)

					db.commit()
				except Exception as exc:
					db.rollback()
					print_exc(exc)
					log('Transaction: %s' % (str(tr),))

			if orders_added > 0:
				res = db.execute("SELECT * FROM orders ORDER BY time")
				orders = res.fetchall()

				active, expired = orders_split(orders)
				remove_orders(expired)

				#active.reverse()
				create_main_image(active) #FIXME for changes only
	except Exception as exc:
		print_exc(exc)


if __name__ == '__main__':
	work()

