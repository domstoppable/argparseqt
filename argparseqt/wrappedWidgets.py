# -*- coding: utf-8 -*-
''' Widgets with a universal api for getting/setting convenience '''

import sys
import argparse

from qtpy import QtCore, QtGui, QtWidgets

from . import typeHelpers

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

	elif argument.type == typeHelpers.rgb:
		widget = ColorWidget(hasAlpha=False, parent=parent)

	elif argument.type == typeHelpers.rgba:
		widget = ColorWidget(hasAlpha=True, parent=parent)

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
			self.valueChanged = widget.valueChanged
		elif hasattr(widget, 'textChanged'):
			widget.textChanged.connect(self.clearNull)
			self.valueChanged = widget.textChanged
		elif hasattr(widget, 'currentTextChanged'):
			self.valueChanged = widget.currentTextChanged

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

class ColorWidget(QtWidgets.QPushButton):
	valueChanged = QtCore.Signal(tuple)

	def __init__(self, hasAlpha=True, parent=None):
		super().__init__(parent)

		self.hasAlpha = hasAlpha
		self.dialog = None
		self.clicked.connect(self.onClick)

		self.clear()

	def onClick(self):
		if self.dialog is None:
			self.dialog = QtWidgets.QColorDialog()
			self.dialog.setCurrentColor(QtGui.QColor(*self.colorValue))
			self.dialog.currentColorChanged.connect(self.onColorAdjusted)

		self.dialog.setOption(self.dialog.ColorDialogOption.ShowAlphaChannel, self.hasAlpha)

		preservedValue = self.colorValue
		self.dialog.exec_()

		if self.dialog.result() != QtWidgets.QDialog.Accepted:
			self.setValue(preservedValue)
			self.valueChanged.emit(preservedValue)

	def toTuple(self):
		color = self.dialog.currentColor()
		value = [color.red(), color.green(), color.blue()]
		if self.hasAlpha:
			value.append(color.alpha())

		return tuple(value)

	def value(self):
		return self.colorValue

	def setValue(self, val):
		if isinstance(val, str):
			if self.hasAlpha:
				val = typeHelpers.rgba(val)
			else:
				val = typeHelpers.rgb(val)

		self.colorValue = tuple(val)
		self.setText(' %s' % (self.colorValue,))

		pixmap = QtGui.QPixmap(self.height(), self.height())
		pixmap.fill(QtGui.QColor(*val))
		self.setIcon(QtGui.QIcon(pixmap))

	def clear(self):
		if self.hasAlpha:
			self.setValue((0, 0, 0, 0))
		else:
			self.setValue((0, 0, 0))

	def onColorAdjusted(self, color):
		value = self.toTuple()
		self.setValue(value)
		self.valueChanged.emit(value)
