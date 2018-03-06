#!/usr/bin/python


import sys
from syslog import syslog


def log(msg):
	syslog(msg)

def print_exc(exc):
	tb = sys.exc_info()[-1]
	lineno = tb.tb_lineno
	filename = tb.tb_frame.f_code.co_filename
	log('%s (%d): %s' % (filename, lineno, exc))
