# -*- coding: utf-8 -*-
import os, sys

"""
 If they don't explicity say they want to use root, and
 are able to actually realise they *have* to type in 'Yes',
 they're probably just running it as root because they're dumb.
 Nothing done here requires root, why should it? Don't let that
 kind of shit happen.
"""

def root_check(no_daemon_key):
	explicity_use_root = False
	starting = 'start' in sys.argv or no_daemon_key in sys.argv

	if '--explicity-use-root' in sys.argv and starting:
		print "Don't run chr as root unless you really, super-duper have to."
		print "If it's so you can use port 80, think about installing a proxy such as nginx."
		print "If you're sure you do, you'll have to type 'Yes', with the capital and all."
		inp = raw_input('Do you really want to run chr as root? ')
		if inp not in ("Yes"):
			print 'Alrighty then!'
			sys.exit(0)
		print "Please, seriously consider why you need to run this as root."
		inp = raw_input('Are you certain? This is your last chance! Type \'Yes\' if you are: ')
		if not inp in ("Yes"):
			print 'Alrighty then!'
			sys.exit(0)
		
		print 'Alright, your loss.'
		explicity_use_root = True

	# If they're starting as root without --explicity-use-root:
	if os.getuid() == 0 and starting and not explicity_use_root:
		print 'Stop! You should never run anything as root unless you absolutely have to.'
		print 'This is not one of those occasions.'
		print 'chr will not function as root, please run it in usermode.'
		print 'If you\'re absolutely sure you want to run as root, use the --explicity-use-root flag.'
		sys.exit(2)