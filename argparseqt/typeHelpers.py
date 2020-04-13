import argparse

class Serial(str):
	pass

def rgb(val):
	if len(val) != 6:
		raise argparse.ArgumentTypeError('Expected 6 characters but received "%s"' % val)

	try:
		return tuple(int(val[i:i+2], 16) for i in (0, 2, 4))
	except:
		raise argparse.ArgumentTypeError('Invalid hex string: %s' % val)

def rgba(val):
	if len(val) != 8:
		raise argparse.ArgumentTypeError('Expected 8 characters but received "%s"' % val)

	try:
		return tuple(int(val[i:i+2], 16) for i in (0, 2, 4, 6))
	except:
		raise argparse.ArgumentTypeError('Invalid hex string: %s' % val)
