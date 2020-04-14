# -*- coding: utf-8 -*-
''' Widgets with a universal api for getting/setting convenience '''

import sys
import pathlib
import argparse
import typing

try:
	import serial.tools.list_ports
except ImportError:
	pass

from qtpy import QtCore, QtGui, QtWidgets

from . import typeHelpers

def makeWidget(argumentOrType, parent=None, defaultValue=None, choices=None, helpText=None):
	''' Creates and returns a data type-appropriate wrapped-widget

		Arguments with finite choices (including booleans) configured will display as a combo box
		Numeric arguments will display with a spin box
		Text and arguments with no specified data type will display with line edit
	'''
	widget = None
	if isinstance(argumentOrType, argparse.Action):
		argument = argumentOrType
		dataType = argument.type
		defaultValue = argument.default
		choices = choices if choices is not None else argument.choices

		if helpText is None and argument.help is not None:
			helpText = argument.help

		if type(argument) == argparse._StoreConstAction:
			widget = ComboBox([argument.const], [argument.const], parent)

		elif type(argument) in [argparse._StoreTrueAction, argparse._StoreFalseAction]:
			widget = BoolSelector(parent=parent)

	else:
		dataType = argumentOrType

	if widget is None:
		if choices is not None:
			widget = ComboBox(choices, parent=parent)

		elif dataType == int:
			widget = SpinBox(parent=parent)

		elif dataType == float:
			widget = DoubleSpinBox(parent=parent)

		elif dataType == bool:
			widget = BoolSelector(parent=parent)

		elif dataType == typeHelpers.rgb:
			widget = ColorWidget(hasAlpha=False, parent=parent)

		elif dataType == typeHelpers.rgba:
			widget = ColorWidget(hasAlpha=True, parent=parent)

		elif dataType == pathlib.Path:
			widget = FileChooser(parent)

		elif 'serial' in sys.modules and dataType == typeHelpers.Serial:
			widget = SerialPortChooser(parent)

		elif dataType == list or typing.get_origin(dataType) == list:
			widget = ListWidget(dataType, parent)

		else:
			widget = LineEdit(parent)

	if helpText is not None:
		widget.setToolTip(helpText)

	widget = ResetableWidget(widget, defaultValue)
	widget.setValue(defaultValue)

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

		self.setSizePolicy(
			QtWidgets.QSizePolicy.Preferred,
			QtWidgets.QSizePolicy.Fixed,
		)

		resetButton = QtWidgets.QToolButton(self)
		resetButton.setSizePolicy(
			QtWidgets.QSizePolicy.Fixed,
			QtWidgets.QSizePolicy.MinimumExpanding,
		)
		resetButton.pressed.connect(self.reset)
		resetButton.setText('↶')

		if defaultValue is None:
			resetButton.setToolTip('Clear')
		else:
			resetButton.setToolTip('Set default: ' + str(defaultValue))

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(widget)
		self.layout().addWidget(resetButton)

		if hasattr(widget, 'valueChanged'):
			widget.valueChanged.connect(self.clearNull)
			self.valueChanged = widget.valueChanged
		elif hasattr(widget, 'textChanged'):
			widget.textChanged.connect(self.clearNull)
			self.valueChanged = widget.textChanged
		elif hasattr(widget, 'currentTextChanged'):
			self.valueChanged = widget.currentTextChanged

		if not hasattr(widget, 'clearValue') and hasattr(widget, 'clear'):
			widget.clearValue = widget.clear

	def clearNull(self):
		self.nulled = False

	def value(self):
		if self.nullable and self.nulled:
			return None
		else:
			return self.widget.value()

	def setValue(self, value):
		if self.nullable and value is None:
			self.widget.clearValue()
			self.nulled = True
		else:
			self.widget.setValue(value)
			self.nulled = False

	def reset(self):
		self.setValue(self.defaultValue)

	def clearValue(self):
		self.setValue(None)

class ListWidgetItem(QtWidgets.QWidget):
	def __init__(self, widget, parent=None):
		super().__init__(parent)
		self.widget = widget

		self.abandonButton = QtWidgets.QToolButton(self)
		self.abandonButton.setText('🗑️')
		self.abandonButton.pressed.connect(self.abandon)
		self.abandonButton.setSizePolicy(
			QtWidgets.QSizePolicy.Fixed,
			QtWidgets.QSizePolicy.MinimumExpanding,
		)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)

		self.layout().addWidget(self.abandonButton)
		self.layout().addWidget(self.widget)

		patches = ['value', 'setValue', 'clearValue', 'valueChanged']
		for prop in patches:
			setattr(self, prop, getattr(self.widget, prop))

	def abandon(self):
		parentLayout = self.parentWidget().layout()
		idx = parentLayout.indexOf(self)
		parentLayout.takeAt(idx)
		self.setParent(None)

class ListWidget(QtWidgets.QWidget):
	valueChanged = QtCore.Signal(list)

	def __init__(self, dataType, parent=None):
		super().__init__(parent)

		self.dataType = dataType
		self.subDataType = typing.get_args(self.dataType)
		if len(self.subDataType) == 0:
			self.subDataType = str
		else:
			self.subDataType = self.subDataType[0]

		self.childrenContainer = QtWidgets.QWidget(self)
		self.childrenContainer.setLayout(QtWidgets.QVBoxLayout())
		self.childrenContainer.layout().setSpacing(int(self.childrenContainer.layout().spacing()/2))
		self.childrenContainer.layout().setContentsMargins(0, 0, 0, 0)

		self.addItemButton = QtWidgets.QToolButton(self)
		self.addItemButton.setText('➕ Add item')
		self.addItemButton.clicked.connect(self._addKid)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.childrenContainer)
		self.layout().addWidget(self.addItemButton)

	def _addKid(self, v=None):
		listWidgetItem = ListWidgetItem(makeWidget(self.subDataType, self.childrenContainer), self.childrenContainer)
		listWidgetItem.valueChanged.connect(self.onChildValueChanged)

		self.childrenContainer.layout().addWidget(listWidgetItem)

		return listWidgetItem

	def _abandonChildren(self):
		layout = self.childrenContainer.layout()
		while layout.count() > 0:
			w = layout.takeAt(0)
			w.widget().setParent(None)

	def clearValue(self):
		self._abandonChildren()

	def onChildValueChanged(self):
		self.valueChanged.emit(self.value())

	def value(self):
		v = []
		layout = self.childrenContainer.layout()
		for idx in range(layout.count()):
			widget = layout.itemAt(idx).widget()
			v.append(widget.value())

		return v

	def setValue(self, values):
		self._abandonChildren()
		for v in values:
			w = self._addKid(v)
			w.setValue(v)

class FileChooser(QtWidgets.QWidget):
	valueChanged = QtCore.Signal(pathlib.Path)

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(0, 0, 0, 0)

		self.textBox = QtWidgets.QLineEdit()
		self.browseButton = QtWidgets.QToolButton()
		self.browseButton.setText('…')

		self.layout().addWidget(self.textBox)
		self.layout().addWidget(self.browseButton)

		self.browseButton.clicked.connect(self._browse)

		self.clear = self.textBox.clear

	def _browse(self):
		selectedFile = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', str(self.value().parent))
		selectedFile = selectedFile[0]
		if selectedFile is not None and selectedFile != '':
			selectedFile = pathlib.Path(selectedFile)

			self.setValue(selectedFile)
			self.valueChanged.emit(selectedFile)

	def value(self):
		return pathlib.Path(self.textBox.text())

	def setValue(self, val):
		self.textBox.setText(str(val))

class ComboBox(QtWidgets.QComboBox):
	def __init__(self, values, labels=None, parent=None):
		super().__init__(parent)

		self.setOptions(values, labels)
		self.valueChanged = self.currentTextChanged

	def setOptions(self, values, labels=None):
		self.clear()

		if labels is None:
			labels = values

		self.addItem('', None)
		self.insertSeparator(1)
		for i,value in enumerate(values):
			self.addItem(str(labels[i]), value)

	def clearValue(self):
		self.setValue(None)

	def value(self):
		return self.currentData()

	def setValue(self, val):
		for i in range(self.count()):
			if val == self.itemData(i):
				self.setCurrentIndex(i)
				break

class SerialPortChooser(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(0, 0, 0, 0)

		devices, labels = self.getPortsAndLabels()
		self.combobox = ComboBox(devices, labels, parent=self)

		self.refreshButton = QtWidgets.QToolButton(self)
		self.refreshButton.setText('🔍')
		self.refreshButton.setToolTip('Refresh list')
		self.refreshButton.clicked.connect(self.refreshPorts)

		self.layout().addWidget(self.combobox)
		self.layout().addWidget(self.refreshButton)

		self.clearValue = self.combobox.clearValue
		self.valueChanged = self.combobox.valueChanged
		self.value = self.combobox.value
		self.setValue = self.combobox.setValue
		self.currentTextChanged = self.combobox.currentTextChanged
		self.setFocus = self.combobox.setFocus

	def getPortsAndLabels(self):
		deviceList = []
		nameList = []

		for portInfo in serial.tools.list_ports.comports():
			deviceList.append(portInfo.device)
			nameList.append(f'{portInfo.description} ({portInfo.device})')

		return deviceList, nameList

	def refreshPorts(self):
		devices, labels = self.getPortsAndLabels()

		self.combobox.setOptions(devices, labels)
		self.combobox.setFocus()
		self.combobox.showPopup()

class BoolSelector(ComboBox):
	def __init__(self, trueLabel='True', falseLabel='False', parent=None):
		super().__init__(
			values=[True, False],
			labels=[trueLabel, falseLabel],
			parent=parent
		)

class LineEdit(QtWidgets.QLineEdit):
	def value(self):
		return self.text()

	def setValue(self, val):
		self.setText(str(val))

class SpinBox(QtWidgets.QSpinBox):
	minimum = -2**30
	maximum = 2**30

	def __init__(self, minimum=None, maximum=None, parent=None):
		super().__init__(parent)

		minimum = minimum or SpinBox.minimum
		if minimum is not None:
			self.setMinimum(minimum)

		maximum = maximum or SpinBox.maximum
		if maximum is not None:
			self.setMaximum(maximum)

	def setValue(self, val):
		if val is None:
			self.setToNone = True
			self.clear()
		else:
			super().setValue(val)

class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
	decimals = 4
	minimum = -2**30
	maximum = 2**30

	def __init__(self, decimals=None, minimum=None, maximum=None, parent=None):
		super().__init__(parent)

		decimals = decimals or DoubleSpinBox.decimals
		if decimals is not None:
			self.setDecimals(decimals)

		minimum = minimum or DoubleSpinBox.minimum
		if minimum is not None:
			self.setMinimum(minimum)

		maximum = maximum or DoubleSpinBox.maximum
		if maximum is not None:
			self.setMaximum(maximum)

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

		self.clearValue()

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

	def clearValue(self):
		if self.hasAlpha:
			self.setValue((0, 0, 0, 0))
		else:
			self.setValue((0, 0, 0))

	def onColorAdjusted(self, color):
		value = self.toTuple()
		self.setValue(value)
		self.valueChanged.emit(value)
