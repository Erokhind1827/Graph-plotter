import socket
import sys
import pickle
import datetime
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

MSG_CONNECT = '!Connect'
MSG_DISCONNECT = '!Disconnect'

class function():
    def __init__(self, fun = '', var = '', cr = 'rect', rl = 'dir', st = -20, en = 20):
        self.funcEquation = fun
        self.varEquation = var
        self.cord = cr
        self.rel = rl
        self.start = st
        self.end = en

    def setData(self, data):
        props = data.split('//')
        self.cord = props[0]
        self.rel = props[1]        
        self.start = int(props[3])
        self.end = int(props[4])
        if self.rel == 'par':
            self.funcEquation, self.varEquation = props[2].split('&')
        elif self.rel == 'dir':
            self.funcEquation == props[2]
        else:
            self.varEquation == props[2]

    def getCord(self):
        return self.cord

    def getRel(self):
        return self.rel

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getFuncEquation(self):
        return self.funcEquation

    def getVarEquation(self):
        return self.varEquation

    def getData(self):
        data = self.cord + '//' + self.rel + '//'
        # data = ''
        if self.rel == 'par':
            data += self.funcEquation + '&' + self.varEquation + '//'
        elif self.rel == 'dir':
            data += self.funcEquation + '//'
        else:
            data += self.varEquation + '//'
        data += str(self.start) + '//' + str(self.end)
        return data
    
    def saveFunction(self):
        n=0

    def __add__(self, other):
        if self.cord == other.cord and self.rel == other.rel:
            if self.rel == 'par':
                fun = self.funcEquation + '+(' + other.funcEquation + ')'
                var = self.varEquation + '+(' + other.varEquation + ')'
            elif self.rel == 'dir':
                fun = self.funcEquation + '+(' + other.funcEquation + ')'
                var = ''
            else:
                fun = ''
                var = self.varEquation + '+(' + other.varEquation + ')'
            return function(fun, var, cr = self.cord, rl = self.rel, st = self.start, en = self.end), True
        else:
            return self, False
    
    def __sub__(self,other):
        if self.cord == other.cord and self.rel == other.rel:
            if self.rel == 'par':
                fun = self.funcEquation + '-(' + other.funcEquation + ')'
                var = self.varEquation + '-(' + other.varEquation + ')'
            elif self.rel == 'dir':
                fun = self.funcEquation + '-(' + other.funcEquation + ')'
                var = ''
            else:
                fun = ''
                var = self.varEquation + '-(' + other.varEquation + ')'
            return function(fun, var, cr = self.cord, rl = self.rel, st = self.start, en = self.end), True
        else:
            return self, False


class Menu(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent = parent)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.activeLineEdit = 'func'
        self.connected = False

        self.func = function()
        self.color = 'r'
        self.grid = True
        self.widthValue = 2
        self.type = 'solid'

        lay = QHBoxLayout(self)
        left = QVBoxLayout()
        gBoxCord = QGroupBox('Coordinates:')
        self.rectan = QRadioButton('Rectangular')
        self.polar = QRadioButton('Polar')
        self.rectan.setChecked(True)
        gbcLay = QVBoxLayout()
        gbcLay.addWidget(self.rectan)
        gbcLay.addWidget(self.polar)
        gBoxCord.setLayout(gbcLay)
        self.rectan.toggled.connect(self.setCord)
        self.polar.toggled.connect(self.setCord)

        gBoxRel = QGroupBox('Relation:')
        self.dir = QRadioButton('Direct')
        self.inv = QRadioButton('Inverse')
        self.par = QRadioButton('Parametrical')
        self.dir.setChecked(True)
        gbrLay = QVBoxLayout()
        gbrLay.addWidget(self.dir)
        gbrLay.addWidget(self.inv)
        gbrLay.addWidget(self.par)
        gBoxRel.setLayout(gbrLay)
        self.dir.toggled.connect(self.setRel)
        self.inv.toggled.connect(self.setRel)
        self.par.toggled.connect(self.setRel)

        domainLbl = QLabel('Domain:')
        domainHLay = QHBoxLayout()
        domainSVLay = QVBoxLayout()
        domainEVLay = QVBoxLayout()
        self.startLbl = QLabel('xStart:')
        self.startSBox = QSpinBox()
        self.startSBox.setRange(-100,100)
        self.startSBox.setValue(-20)       
        domainSVLay.addWidget(self.startLbl)
        domainSVLay.addWidget(self.startSBox)
        self.endLbl = QLabel('xEnd:')
        self.endSBox = QSpinBox()
        self.endSBox.setRange(-20,100)
        self.endSBox.setValue(20)        
        domainEVLay.addWidget(self.endLbl)
        domainEVLay.addWidget(self.endSBox)
        domainHLay.addLayout(domainSVLay)
        domainHLay.addLayout(domainEVLay)
        self.startSBox.valueChanged.connect(self.startValueChanged)
        self.endSBox.valueChanged.connect(self.endValueChanged)

        left.addWidget(gBoxCord)
        left.addWidget(gBoxRel)
        left.addWidget(domainLbl)
        left.addLayout(domainHLay)
        left.addSpacing(50)

        center = QVBoxLayout()
        funcLay = QHBoxLayout()
        self.funcLbl = QLabel('y(x) =')
        self.funcEquation = QLineEdit()
        validatorRegEx = QRegExp("[.()0-9a-eg-qs-xz\*\/\+\-\^]+")
        validator = QRegExpValidator(validatorRegEx,self.funcEquation)
        self.funcEquation.setValidator(validator)
        self.funcEquation.textChanged.connect(self.changeFuncEquation)
        funcLay.addWidget(self.funcLbl)
        funcLay.addWidget(self.funcEquation)

        varLay = QHBoxLayout()
        self.varLbl = QLabel('x =')
        self.varEquation = QLineEdit()
        self.varEquation.textChanged.connect(self.changeVarEquation)
        self.varEquation.setEnabled(False)
        varLay.addWidget(self.varLbl)
        varLay.addWidget(self.varEquation)

        self.openButton = QPushButton('Open')
        self.openButton.clicked.connect(self.open)

        self.saveButton = QPushButton('Save')
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.save)

        soLay = QHBoxLayout()
        soLay.addWidget(self.openButton)
        soLay.addWidget(self.saveButton)

        self.plusButton = QPushButton('+')
        self.plusButton.clicked.connect(self.add)

        self.minusButton = QPushButton('-')
        self.minusButton.clicked.connect(self.subtract)

        pmLay = QHBoxLayout()
        pmLay.addWidget(self.plusButton)
        pmLay.addWidget(self.minusButton)

        self.connectButton = QPushButton('Connect')
        self.connectButton.setAccessibleName('c')
        self.connectButton.setDisabled(False)
        self.connectButton.clicked.connect(self.updateConnection)

        self.graphButton = QPushButton('Graph!')
        self.graphButton.setDisabled(True)
        self.graphButton.clicked.connect(self.graph)

        center.addLayout(funcLay)
        center.addLayout(varLay)
        center.addLayout(soLay)
        center.addLayout(pmLay)
        center.addWidget(self.connectButton)
        center.addWidget(self.graphButton)

        right = QVBoxLayout()
        self.adress = QLineEdit()
        self.adress.setText('127.0.0.1')
        adressLbl = QLabel('Adress:')
        gBoxCol = QGroupBox('Color:')
        self.red = QRadioButton('Red')
        self.green = QRadioButton('Green')
        self.blue = QRadioButton('Blue')
        self.red.setChecked(True)
        gbcolLay = QVBoxLayout()
        gbcolLay.addWidget(self.red)
        gbcolLay.addWidget(self.green)
        gbcolLay.addWidget(self.blue)
        gBoxCol.setLayout(gbcolLay)
        self.red.toggled.connect(self.setColor)
        self.green.toggled.connect(self.setColor)
        self.blue.toggled.connect(self.setColor)

        gBoxType = QGroupBox('Type:')
        self.solid = QRadioButton('Solid')
        self.dashed = QRadioButton('Dashed')
        self.dotted = QRadioButton('Dotted')
        self.solid.setChecked(True)
        gbtypeLay = QVBoxLayout()
        gbtypeLay.addWidget(self.solid)
        gbtypeLay.addWidget(self.dashed)
        gbtypeLay.addWidget(self.dotted)
        gBoxType.setLayout(gbtypeLay)
        self.solid.toggled.connect(self.setType)
        self.dashed.toggled.connect(self.setType)
        self.dotted.toggled.connect(self.setType)

        widthLbl = QLabel('Width:')
        widthLay = QHBoxLayout()
        self.widthSl = QSlider(Qt.Orientation.Horizontal)
        self.widthSl.setRange(1,7)
        self.widthSl.setSingleStep(1)
        self.widthSl.setValue(2)
        self.widthValueLbl = QLabel('2')
        widthLay.addWidget(self.widthSl)
        widthLay.addWidget(self.widthValueLbl)
        self.widthSl.valueChanged.connect(self.updateLbl)

        self.gridChB = QCheckBox('Grid')
        self.gridChB.setChecked(True)
        self.gridChB.toggled.connect(self.setGrid)
        right.addWidget(adressLbl)
        right.addWidget(self.adress)
        right.addWidget(gBoxCol)
        right.addWidget(gBoxType)
        right.addWidget(widthLbl)
        right.addLayout(widthLay)
        right.addWidget(self.gridChB)

        lay.addLayout(left,1)
        lay.addLayout(center,1)
        lay.addLayout(right,1)
        
        self.setLayout(lay)

    def updateMenu(self):
        fE = self.func.funcEquation
        vE = self.func.varEquation
        if self.func.cord == 'rect':
            self.rectan.setChecked(True)
        else:
            self.polar.setChecked(True)
        if self.func.rel == 'dir':
            self.dir.setChecked(True)
        elif self.func.rel == 'inv':
            self.inv.setChecked(True)
        else:
            self.par.setChecked(True)
        self.startSBox.setValue(self.func.getStart())
        self.endSBox.setValue(self.func.getEnd())
        # print(self.func.funcEquation)
        self.funcEquation.setText(fE)
        self.varEquation.setText(vE)
        self.func.funcEquation = fE
        self.func.varEquation = vE

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", ".", "Pickle Files (*.pkl);;All Files (*)")
        if fileName:
            with open(fileName,'rb') as file:
                self.func = pickle.load(file)
                self.updateMenu()

    def save(self):
        fileName, _ = QFileDialog.getSaveFileName(None, "Save File", ".", "Pickle Files (*.pkl);;All Files (*)")
        if fileName:
            if os.path.exists(fileName):
                os.remove(fileName)
            with open(fileName,'wb') as file:
                pickle.dump(self.func,file)

    def add(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", ".", "Pickle Files (*.pkl);;All Files (*)")
        if fileName:
            with open(fileName,'rb') as file:
                addfun = pickle.load(file)
                self.func,added = self.func + addfun
                if added:
                    self.updateMenu()
                else:
                    Mb = QMessageBox()
                    Mb.setText("Parameters of two functions aren't the same")
                    Mb.exec()

    def subtract(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", ".", "Pickle Files (*.pkl);;All Files (*)")
        if fileName:
            with open(fileName,'rb') as file:
                addfun = pickle.load(file)
                self.func, subtracted = self.func - addfun
                if subtracted:
                    self.updateMenu()
                else:
                    Mb = QMessageBox()
                    Mb.setText("Parameters of two functions aren't the same")
                    Mb.exec()

    def updateConnection(self):
        try:
            ip = self.adress.text()
            self.socket.connect((ip, 5050))
            self.socket.sendall('connect'.encode())
            self.graphButton.setDisabled(False)
            self.connectButton.setDisabled(True)
            self.connected = True
        except:
            Mb = QMessageBox()
            Mb.setText('Unable to connect')
            Mb.exec()
            print('Unable to connect')

    def graph(self):
        data = self.func.cord + '//' + self.func.rel + '//'
        
        if self.func.rel == 'par':
            data += self.func.funcEquation + '&' + self.func.varEquation + '//'
        elif self.func.rel == 'dir':
            data += self.func.funcEquation + '//'
        else:
            data += self.func.varEquation + '//'
        data += str(self.func.start) + '//' + str(self.func.end) + '//'
        data += self.color + '//' + str(self.widthValue) + '//' + str(self.grid) + '//' + self.type + '//'
        time = datetime.datetime.now()
        time = str(time.time())
        dot = time.find('.')
        time = time[0:dot]
        time = time.replace(':','-')
        data += time
        # print(time)
        sent = data.encode()
        data = ''
        if self.func.rel == 'par' and (self.func.funcEquation == '' or self.func.varEquation == ''):
            Mb = QMessageBox()
            Mb.setText('input both equations')
            Mb.exec()
        else:
            self.socket.sendall(sent)
            received = self.socket.recv(1024)
            received = received.decode()
            if received != 'Ok':
                Mb = QMessageBox()
                Mb.setText(received)
                Mb.exec()

    def updateLbl(self, value):
        self.widthValue = value
        self.widthValueLbl.setText(str(value))

    def changeLbls(self):
        self.funcEquation.clear()
        self.varEquation.clear()
        self.func.funcEquation = ''
        self.func.varEquation = ''

        if self.func.rel == 'par':
            self.funcEquation.setEnabled(True)
            self.varEquation.setEnabled(True)

            validatorRegEx = QRegExp("[.()0-9a-eg-qs-wz\*\/\+\-\^]+")
            validator = QRegExpValidator(validatorRegEx,self.funcEquation)
            self.funcEquation.setValidator(validator)
            self.varEquation.setValidator(validator)

            self.startLbl.setText('tStart:')
            self.endLbl.setText('tEnd:')
            self.startSBox.setRange(-100,99)
            self.endSBox.setRange(-99,100)
            if self.func.cord == 'rect':
                self.funcLbl.setText('y(t) =')
                self.varLbl.setText('x(t) =')
            else:
                self.funcLbl.setText('r(t) =')
                self.varLbl.setText('f(t) =')

        elif self.func.rel == 'dir':
            self.activeLineEdit = 'func'
            self.funcEquation.setEnabled(True)
            self.varEquation.setEnabled(False)   

            if self.func.cord == 'rect':
                validatorRegEx = QRegExp("[.()0-9a-eg-qs-xz\*\/\+\-\^]+")
                validator = QRegExpValidator(validatorRegEx,self.funcEquation)
                self.funcEquation.setValidator(validator)

                self.startLbl.setText('xStart:')
                self.endLbl.setText('xEnd:')
                self.startSBox.setRange(-100,99)
                self.endSBox.setRange(-99,100)
                self.funcLbl.setText('y(x) =')
                self.varLbl.setText('x =')
            else:
                validatorRegEx = QRegExp("[.()0-9a-qs-wz\*\/\+\-\^]+")
                validator = QRegExpValidator(validatorRegEx,self.funcEquation)
                self.funcEquation.setValidator(validator)

                self.startLbl.setText('fStart(Pi/12):')
                self.endLbl.setText('fEnd(Pi/12):')
                self.startSBox.setRange(-100,99)
                self.endSBox.setRange(-99,100)
                self.funcLbl.setText('r(f) =')
                self.varLbl.setText('f =')

        else:
            self.activeLineEdit = 'var'
            self.funcEquation.setEnabled(False)
            self.varEquation.setEnabled(True)  
                    
            if self.func.cord == 'rect':
                validatorRegEx = QRegExp("[.()0-9a-eg-qs-wyz\*\/\+\-\^]+")
                validator = QRegExpValidator(validatorRegEx,self.varEquation)
                self.varEquation.setValidator(validator)

                self.startLbl.setText('yStart:')
                self.endLbl.setText('yEnd:')
                self.startSBox.setRange(-100,99)
                self.endSBox.setRange(-99,100)
                self.funcLbl.setText('y =')
                self.varLbl.setText('x(y) =')
            else:
                validatorRegEx = QRegExp("[.()0-9a-eg-wz\*\/\+\-\^]+")
                validator = QRegExpValidator(validatorRegEx,self.varEquation)
                self.varEquation.setValidator(validator)

                self.startLbl.setText('rStart:')
                self.endLbl.setText('rEnd:')
                self.startSBox.setRange(0,99)
                self.endSBox.setRange(1,100)
                self.funcLbl.setText('r =')
                self.varLbl.setText('f(r) =')
    
    def setCord(self):
        if self.rectan.isChecked():
            self.func.cord = 'rect'
        else:
            self.func.cord = 'polar'
        self.changeLbls()

    def setRel(self):
        if self.inv.isChecked():
            self.func.rel = 'inv'
        elif self.dir.isChecked():
            self.func.rel = 'dir'
        else:
            self.func.rel = 'par'
        self.changeLbls()

    def startValueChanged(self, value):
        self.func.start = value
        self.endSBox.setRange(value,100)

    def endValueChanged(self, value):
        self.func.end = value

    def setColor(self):
        if self.red.isChecked():
            self.color = 'r'
        elif self.green.isChecked():
            self.color = 'g'
        else:
            self.color = 'b'

    def setType(self):
        if self.solid.isChecked():
            self.type = 'solid'
        elif self.dashed.isChecked():
            self.type = 'dashed'
        else:
            self.type = 'dotted'

    def setGrid(self):
        self.grid = self.gridChB.isChecked()

    def changeFuncEquation(self, str):
        self.func.funcEquation = str
        if self.func.funcEquation != '' or self.func.varEquation != '':
            self.saveButton.setDisabled(False)
        else:
            self.saveButton.setDisabled(True)

    def changeVarEquation(self, str):
        self.func.varEquation = str
        if self.func.funcEquation != '' or self.func.varEquation != '':
            self.saveButton.setDisabled(False)
        else:
            self.saveButton.setDisabled(True)

    def closeEvent(self, event):
        if self.connected:
            self.socket.sendall(MSG_DISCONNECT.encode())
        

app = QApplication(sys.argv)
w = Menu()
w.resize(600,325)
w.show()
sys.exit(app.exec_())