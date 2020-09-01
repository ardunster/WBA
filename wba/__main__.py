#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main interface script

Created on Sun Aug 30 15:05:58 2020

@author: adunster
"""


import sys
from PySide2 import QtCore, QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(self)
        self.setWindowTitle("WorldBuilder Alpha")

class Character(QtWidgets.QWidget):
    """
    Character view window
    """
    pass


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
    