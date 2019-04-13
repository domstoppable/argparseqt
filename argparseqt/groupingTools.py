# -*- coding: utf-8 -*-
''' Utility functions for organizing arguments by their groups '''

import argparse

def organizeIntoGroups(parser):
	''' Returns a dict where keys are argparse group names and keys are dicts of name/argument pairs '''
	groups = {}

	for group in parser._action_groups:
		groups[group] = {}

		for action in group._group_actions:
			if type(action) != argparse._HelpAction:
				groups[group][action.dest] = action

	return groups

def parseIntoGroups(parser):
	''' Returns a dict where keys are argparse group names and keys are dicts of name/value pairs '''
	args = vars(parser.parse_args())
	groups = {}

	for group in parser._action_groups:
		if group.title in ['positional arguments', 'optional arguments']:
			groupName = ''
		else:
			groupName = group.title

		groups[groupName] = {}

		for action in group._group_actions:
			if type(action) != argparse._HelpAction:
				groups[groupName][action.dest] = args[action.dest]

	return groups