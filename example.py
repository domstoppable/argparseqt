# -*- coding: utf-8 -*-
''' An example of how to use argparseqt with the standard argparse module '''

import argparse
import pathlib
import typing

from qtpy import QtCore, QtWidgets

import argparseqt.gui
import argparseqt.groupingTools
import argparseqt.typeHelpers

def runDemo():
	# Add parser settings like normal
	parser = argparse.ArgumentParser(description='Settings are grouped, but ungrouped items appear here.')
	parser.add_argument('--orphanedSetting', help='This setting does not belong to a group :(')

	textSettings = parser.add_argument_group('Strings', description='Text input')
	textSettings.add_argument('--freetext', type=str, default='Enter freetext here', help='Type anything you want here')
	textSettings.add_argument('--pickText', default='I choo-choo-choose you', choices=['Bee mine', 'I choo-choo-choose you'], help='Choose one of these')

	numericSettings = parser.add_argument_group('Numbers', description='Numeric input')
	numericSettings.add_argument('--int', type=int, default=100, help='Decimals are not allowed')
	numericSettings.add_argument('--float', type=float, help='Decimals are allowed')
	numericSettings.add_argument('--pickInt', type=int, choices=[1, 2, 3], help='Choose one of these')
	numericSettings.add_argument('--pickFloat', type=float, choices=[1.1, 22.22, 333.333], default=333.333, help='You can only pick one')

	booleanSettings = parser.add_argument_group('Booleans', description='Booleans and consts')
	booleanSettings.add_argument('--storeTrue', action='store_true')
	booleanSettings.add_argument('--storeFalse', action='store_false')
	booleanSettings.add_argument('--storeConst', action='store_const', const=999)

	exoticSettings = parser.add_argument_group('Exotic types', description='Fancy data types')
	exoticSettings.add_argument('--rgb', type=argparseqt.typeHelpers.rgb)
	exoticSettings.add_argument('--rgba', type=argparseqt.typeHelpers.rgba)
	exoticSettings.add_argument('--path', type=pathlib.Path, default=pathlib.Path.home() / 'file.txt')

	try:
		import serial
		exoticSettings.add_argument('--serialPort', type=argparseqt.typeHelpers.Serial)
	except ImportError:
		pass

	listTypes = parser.add_argument_group('List types', description='Lists of types')
	listTypes.add_argument('--textList', type=typing.List, default=['Hello', 'world!'])
	listTypes.add_argument('--intList', type=typing.List[int])
	listTypes.add_argument('--floatList', type=typing.List[float])
	listTypes.add_argument('--boolList', type=typing.List[bool])
	listTypes.add_argument('--colorList', type=typing.List[argparseqt.typeHelpers.rgba])
	listTypes.add_argument('--pathList', type=typing.List[pathlib.Path])
	listTypes.add_argument('--ListList', type=typing.List[typing.List], default=[['1a', '1b', '1c'], ['2a', '2b', '2c']])

	# Now make it a GUI
	app = QtWidgets.QApplication()

	# Create a dialog box for our settings
	dialog = argparseqt.gui.ArgDialog(parser)

	# Parse command line arguments and organize into groups
	cliSettings = argparseqt.groupingTools.parseIntoGroups(parser)

	# Set dialog values based on command line arguments
	dialog.setValues(cliSettings)

	# Show the dialog
	dialog.exec_()

	if dialog.result() == QtWidgets.QDialog.Accepted:
		values = dialog.getValues()
		print('Values:', values)
	else:
		print('User cancelled')

if __name__ == '__main__':
	runDemo()