# -*- coding: utf-8 -*-
''' Utility functions for organizing arguments by their groups '''

import argparse

def organizeIntoGroups(parser):
	''' Returns a dict where keys are argparse groups and values are dicts of name/argument pairs '''
	groups = {}

	for group in parser._action_groups:
		groups[group] = {}

		for action in group._group_actions:
			if type(action) != argparse._HelpAction:
				groups[group][action.dest] = action

	return groups

def parseIntoGroups(parser):
	''' Returns a dict where keys are argparse group names and values are dicts of name/value pairs

		Arguments that do not belong to a group will be stored in the top-level dict
	'''
	args = vars(parser.parse_args())
	groups = {}

	for group in parser._action_groups:
		if group.title in ['positional arguments', 'optional arguments']:
			groupDict = groups
		else:
			groupName = group.title
			groupDict = {}
			groups[groupName] = groupDict

		for action in group._group_actions:
			if type(action) != argparse._HelpAction:
				groupDict[action.dest] = args[action.dest]

	return groups