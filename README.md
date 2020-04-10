# argparseqt
An easy way to make Qt GUIs using the argparse standard module

## Installation
Via pip:
```bash
pip install argparseqt
```

From source:
```bash
git clone https://github.com/domstoppable/argparseqt.git
cd argparseqt.git
python setup.py install
```

## Dependencies
Requires:
* [qtpy](https://github.com/spyder-ide/qtpy)
* Qt bindings for Python (either `PySide2`, `PyQt5`, `PySide`, or `PyQt`)

## Usage
### Quick start
```python
import argparse
import argparseqt.gui

parser = argparse.ArgumentParser(description='Main settings')
parser.add_argument('--storeConst', action='store_const', const=999)

textSettings = parser.add_argument_group('Strings', description='Text input')
textSettings.add_argument('--freetext', type=str, default='Enter freetext here', help='Type anything you want here')
textSettings.add_argument('--pickText', default='I choo-choo-choose you', choices=['Bee mine', 'I choo-choo-choose you'], help='Choose one of these')

app = QtWidgets.QApplication()
dialog = argparseqt.gui.ArgDialog(parser)
dialog.exec_()

if dialog.result() == QtWidgets.QDialog.Accepted:
	values = dialog.getValues()
	print('Values:', values)
else:
	print('User cancelled')
```

See [example.py](https://github.com/domstoppable/argparseqt/blob/master/example.py) for more.
