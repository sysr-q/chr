# -*- coding: utf-8 -*-
import settings

import os
from time import strftime, gmtime

_file_info = settings.log_dir + os.sep + "info.log"
_file_debug = settings.log_dir + os.sep + "debug.log"
_file_warning = settings.log_dir + os.sep + "warning.log"
_file_error = settings.log_dir + os.sep + "error.log"

if not os.path.exists(settings.log_dir):
	os.makedirs(settings.log_dir)


def info(*args):
	args_ = fix(args)
	out(_file_info, ' '.join(args_))

def debug(*args):
	args_ = fix(args)
	out(_file_debug, ' '.join(args_), print_=settings.debug)	

def warning(*args):
	args_ = fix(args)
	out(_file_warning, ' '.join(args_))

def error(*args):
	args_ = fix(args)
	out(_file_error, ' '.join(args_))

def fatal(*args):
	args_ = fix(args)
	out(_file_error, ' '.join(['!!FATAL!!'] + args_))

def out(file_, text, time_=True, print_=True):
	if time_:
		text = '[{0}] {1}'.format(strftime("%m/%d/%Y %H:%M:%S", gmtime()), text)
	if print_:
		print text
	touch(file_)
	with open(file_, 'a+b') as f:
		f.write(text + "\n")

def touch(file_):
	"""Create a missing file.
	"""
	if not os.path.exists(file_):
		with open(file_, 'w+'):
			pass

def fix(args):
	return [str(arg) for arg in args]