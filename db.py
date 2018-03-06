#!/usr/bin/python


import sqlite3
from log import log


ADDRESS = '3P7YwoaysVfUAEVvBGWJvseg7nUXPdonVgz'
DB_NAME = 'modern_token.db'
PIXEL_SECOND_PRICE = 0.01/(3600.0*24) # mt for pixel per day


class DB:
	global DB_NAME, PIXEL_SECOND_PRICE
	def __init__(self):
		self._conn = None
		self._cur = None

	def __enter__(self):
		self._conn = sqlite3.connect(DB_NAME)
		self._cur = self._conn.cursor()
		return self

	def __exit__(self, type, value, tb):
		self._conn.close()

	def commit(self):
		self._conn.commit()

	def rollback(self):
		self._conn.rollback()

	def execute(self, sql, args = ()):

		return self._cur.execute(sql, args)

	def get_var_text(self, key):
		res = self.execute('SELECT * FROM vars_text WHERE key=?', (key,))
		res = res.fetchone()
		return res[1] if res else None

	def set_var_text(self, key, val):
		return self.execute('INSERT INTO vars_text VALUES (?,?)', (key, val))

	def get_var_int(self, key):
		res = self.execute('SELECT * FROM vars_int WHERE key=?', (key,))
		res = res.fetchone()
		return res[1] if res else None

	def set_var_int(self, key, val):
		return self.execute('INSERT INTO vars_int VALUES (?,?)', (key, val))

	def cursor(self):
		return self._cur

	def has_order(self, id_):
		try:
			res = self._cur.execute("SELECT COUNT(*) FROM orders WHERE id=?", (id_,))
			if res.fetchone()[0] > 0:
				return 1
		except Exception as exc:
			log('db_has_order error %s' % (exc,))
		return 0

	def add_order(self, id_, timestamp, sender, payment, url, coords, size):
		try:
			pixels_count = size[0]*size[1]
			if pixels_count > 0:
				period = int(payment/(pixels_count*PIXEL_SECOND_PRICE))
			else:
				period = 0
		except:
			return 0

		self._cur.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)",
							(id_, timestamp, sender, payment, period, url, coords[0], coords[1], size[0], size[1]))
		return 1


def create_tables(db):
	db.execute('DROP TABLE IF EXISTS vars_int')
	db.execute('DROP TABLE IF EXISTS vars_text')
	db.execute('DROP TABLE IF EXISTS orders')

	db.execute('CREATE TABLE vars_int (key text, value integer)')
	db.execute('CREATE TABLE vars_text (key text, value integer)')
	db.execute('CREATE TABLE orders (id text, time integer, sender text, payment real, period integer, url text,'
				' x integer, y integer, sx integer, sy integer)')

def init_vars(db):
	db.set_var_text('address', ADDRESS)
	db.set_var_int('expired_time', 0)
	db.set_var_int('loaded_time', 0)


if __name__ == '__main__':
	print 'Create DB'
	with DB() as db:
		cur = db.cursor()
		create_tables(db)
		init_vars(db)
		db.commit()

