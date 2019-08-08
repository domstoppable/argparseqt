# -*- coding: utf-8 -*-
''' Widgets with a universal api for getting/setting convenience '''

import sys
import argparse

from qtpy import QtCore, QtWidgets


def makeWidget(argument, parent=None):
	''' Creates and returns a data type-appropriate wrapped-widget

		Arguments with finite choices (including booleans) configured will display as a combo box
		Numeric arguments will display with a spin box
		Text and arguments with no specified data type will display with line edit
	'''
	if type(argument) == argparse._StoreConstAction:
		widget = ComboBox([argument.const], [argument.const], parent)

	elif type(argument) in [argparse._StoreTrueAction, argparse._StoreFalseAction]:
		widget = ComboBox([True, False], parent=parent)

	elif argument.choices is not None:
		widget = ComboBox(argument.choices, parent=parent)

	elif argument.type == int:
		widget = SpinBox(parent)

	elif argument.type == float:
		widget = DoubleSpinBox(parent)

	else:
		widget = LineEdit(parent)

	if argument.help is not None:
		widget.setToolTip(argument.help)

	widget = ResetableWidget(widget, argument.default)

	return widget

class ResetableWidget(QtWidgets.QWidget):
	''' Wraps a widget in a horizontal box layout which also includes a reset button

		Also adds the ability for text and spinbox widgets to accept and return `None` as a value
	'''
	def __init__(self, widget, defaultValue):
		super().__init__(widget.parent())
		self.widget = widget
		self.defaultValue = defaultValue
		self.nullable = not isinstance(widget, QtWidgets.QComboBox)
		self.nulled = True

		resetButton = QtWidgets.QToolButton(self)
		resetButton.pressed.connect(self.reset)
		resetButton.setText('↶')

		if defaultValue is None:
			resetButton.setToolTip('Clear')
		else:
			resetButton.setToolTip('Set default: ' + str(defaultValue))

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().addWidget(widget)
		self.layout().addWidget(resetButton)

		self.layout().setContentsMargins(0, 0, 0, 0)

		if hasattr(widget, 'valueChanged'):
			widget.valueChanged.connect(self.clearNull)
		elif hasattr(widget, 'textChanged'):
			widget.textChanged.connect(self.clearNull)

	def clearNull(self):
		self.nulled = False

	def value(self):
		if self.nullable and self.nulled:
			return None
		else:
			return self.widget.value()

	def setValue(self, value):
		if self.nullable and value is None:
			self.widget.clear()
			self.nulled = True
		else:
			self.widget.setValue(value)
			self.nulled = False

	def reset(self):
		self.setValue(self.defaultValue)

class ComboBox(QtWidgets.QComboBox):
	def __init__(self, values, labels=None, dataType=None, parent=None):
		super().__init__(parent)
		self.dataType = dataType

		if labels is None:
			labels = values

		self.addItem('', None)
		self.insertSeparator(1)
		for i,value in enumerate(values):
			self.addItem(str(labels[i]), value)

	def value(self):
		return self.currentData()

	def setValue(self, val):
		for i in range(self.count()):
			if val == self.itemData(i):
				self.setCurrentIndex(i)
				break

class BoolComboBox(ComboBox):
	def __init__(self, trueLabel='Enabled', falseLabel='disabled', parent=None):
		self.labelValueMap = {
			trueLabel: True,
			falseLabel: False
		}

	def value(self):
		return self.labelValueMap[self.currentText()]

	def setValue(self, val):
		for i in range(self.count()):
			if str(val) == self.labelValueMap[self.itemText(i)]:
				self.setCurrentIndex(i)
				break

'''
class NullableWidget():
	def __init__(self):
		self.setToNone = True
		self.valueChanged.connect(self.clearNone)

		# Can't monkeypatch the value function until *after* construction
		def override():
			self._value = self.value
			self.value = self._valueOverride

			self._setValue = self.setValue
			self.setValue = self._setValueOverride

		QtCore.QTimer.singleShot(1, override)

	def clearNone(self):
		self.setToNone = False

	def _valueOverride(self):
		if self.setToNone:
			return None
		else:
			return self._value()

	def _setValueOverride(self, value):
		if value is None:
			self.setToNone = True
			self.clear()
		else:
			self()._setValue(val)
'''

class LineEdit(QtWidgets.QLineEdit):
	def value(self):
		return self.text()

	def setValue(self, val):
		self.setText(str(val))

class SpinBox(QtWidgets.QSpinBox):
	def __init__(self, parent=None):
		QtWidgets.QSpinBox.__init__(self, parent)
		#ClearableSpinBox.__init__(self)

		self.setRange(-2**30, 2**30)

	def setValue(self, val):
		if val is None:
			self.setToNone = True
			self.clear()
		else:
			super().setValue(val)

class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
	def __init__(self, parent=None):
		QtWidgets.QDoubleSpinBox.__init__(self, parent)
		#ClearableSpinBox.__init__(self)

		self.setRange(-2**30, 2**30)
		self.setDecimals(15)

	def setValue(self, val):
		if val is None:
			self.setToNone = True
			self.clear()
		else:
			super().setValue(val)

def makeNullable(widget):
	def clearNull():
		widget.nulled = False

	def value(self):
		if self.nulled:
			return None
		else:
			return self._value()

	def setValue(self, value):
		if value is None:
			self.setToNone = True
			self.clear()
		else:
			self()._setValue(val)


	widget.nulled = True
	if hasattr(widget, 'valueChanged'):
		widget.valueChanged.connect(clearNull)

	widget._value = widget.value
	widget._setValue = widget.setValue

	widget.value = value
	widget.setValue = setValue

class NullableWidget(QtWidgets.QWidget):
	def __init__(self, widget):
		super().__init__(widget.parent())

		self.widget = widget
		self.nulled = True

		if hasattr(widget, 'valueChanged'):
			widget.valueChanged.connect(self.clearNull)
		elif hasattr(widget, 'textChanged'):
			widget.textChanged.connect(self.clearNull)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().addWidget(self.widget)

	def clearNull(self):
		self.nulled = False

	def value(self):
		if self.nulled:
			return None
		else:
			return self.widget.value()

	def setValue(self, value):
		if value is None:
			self.nulled = True
			self.widget.clear()
		else:
			self.widget.setValue(value)


