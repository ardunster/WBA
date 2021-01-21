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
        super().__init__()
        print(super())
        self.setWindowTitle("WorldBuilder Alpha")
        
        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        
        # Exit QAction
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        
        self.file_menu.addAction(exit_action)
        
        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Stuff and things")
        
        

class Character(QtWidgets.QWidget):
    """
    Character view window
    """
    pass


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)
    # Create and show the form
    # form = Form()
    main = MainWindow()
    main.show()
    # form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
    print('Successfully run __main__.py')

