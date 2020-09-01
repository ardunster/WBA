# -*- coding: utf-8 -*-
"""
Spyder Editor

Experimental playground for Qt/Pyside tutorials
"""


'''
Order of construction:

pick data handling framework/database
get character, location basics working - default classes - parent class for new custom classes
get event basics working

ui basics 
linking (every "add link" function should be bidirectional !! )
timeline
categories (character, location, event)

no particular order yet:

text editor (with autosave?)
whiteboard/oekaki
image inclusion
character rando question
ui for splash, pick world, new world, etc
analyze
maps
custom datetime
ui for settings/world config. 
    - are there any universal settings or all per world?
automatic db backups, options like - keep the x most recent backups, plus x per month/week, etc

error handling
search functionality
custom category ?

cloud save

verify links - every link has a backlink - do I need this? maybe, if my DB seems error prone
restore view when reopening program
write webpages, load webpages? might facilitate wiki export.

'''



import sys
import random
from PySide2 import QtCore, QtWidgets, QtGui


class HalloWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.hallo = ["Hallo Welt", "hi mailma", "hola mundo", "nibet mop"]
        
        self.button = QtWidgets.QPushButton("Haz cliq aqui")
        self.text = QtWidgets.QLabel("Hallo wurld")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        
        self.button.clicked.connect(self.magic)
        
        
    def magic(self):
        self.text.setText(random.choice(self.hallo))
        console()


class Form(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("teh aqesome")
        
        self.edit = QtWidgets.QLineEdit("write some thing here ish")
        self.button = QtWidgets.QPushButton("Greetin'z")
        self.button.clicked.connect(self.greetings)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
        
        
        
    def greetings(self):
        print(f'Hola {self.edit.text()}')

@QtCore.Slot()
def console():
    print("haz cliq alli.")
    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    
    # widget = HalloWidget()
    # widget.resize(800,600)
    # widget.show()
    
    form = Form()
    form.show()
    
    sys.exit(app.exec_())
    
    


