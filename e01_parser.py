# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwin.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import zlib


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 430)
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(160, 50, 421, 331))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setFont(QtGui.QFont('Monaco'))
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setGeometry(QtCore.QRect(10, 50, 141, 331))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemClicked.connect(self.sectionclicked)

        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10, 10, 571, 31))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.selectButton = QtWidgets.QPushButton(self.widget)
        self.selectButton.setObjectName("selectButton")
        self.horizontalLayout.addWidget(self.selectButton)

        self.imageName = QtWidgets.QTextBrowser(self.widget)
        self.imageName.setObjectName("imageName")
        self.horizontalLayout.addWidget(self.imageName)

        # zlib decompress
        self.zlibButton = QtWidgets.QPushButton(Form)
        self.zlibButton.setGeometry(QtCore.QRect(470, 390, 113, 32))
        self.zlibButton.setObjectName("zlibButton")
        self.data = ''
        self.zlibButton.clicked.connect(self.zlib_decom)

        # file dialog control
        self.fileDialog = QtWidgets.QFileDialog()
        self.selectButton.clicked.connect(self.file_select)

        self._translate = QtCore.QCoreApplication.translate
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.filename = ''
        self.data = ''

    def retranslateUi(self, Form):
        Form.setWindowTitle(self._translate("Form", "E01 파서"))
        self.selectButton.setText(self._translate("Form", "이미지 선택"))
        self.zlibButton.setText(self._translate("Form", "zlib 복호화"))

    def zlib_decom(self):
        try:
            tmp = zlib.decompress(self.data)
            self.textBrowser.setText(tmp.decode())
        except:
            self.textBrowser.clear()
            self.textBrowser.setText('Can\'t decompress data')

    def sectionclicked(self, item):
        fp = open(self.filename, 'rb')
        addr = int(item.toolTip(),16)
        fp.seek(addr)
        data = fp.read(0x4c)
        size = int.from_bytes(data[0x18:0x20],byteorder="little")
        fp.seek(addr)
        data = fp.read(size)
        self.data = data[0x4c:]
        clean_data = []
        left_length = len(data) - 0x4c
        line_length = int(left_length / 0x10) + 1
        for i in range(line_length):
            tmp = data[0x4c+0x10*i:0x4c+0x10*(i+1)].hex()
            tmp = map(''.join, zip(*[iter(tmp)]*2))
            tmp = ' '.join(tmp)
            clean_data.append(tmp)
        self.textBrowser.setText( ('\n'.join(clean_data)).upper() )
        fp.close()
        

    def parse_image(self):
        print(self.filename, "Parsing")
        fp = open(self.filename, 'rb')
        curpos = 0xD
        name = ''
        while curpos != 0:
            item = QtWidgets.QListWidgetItem()
            item.setToolTip(self._translate("Form",hex(curpos)))
            curpos, name = section_parse(fp, curpos)
            item.setText(self._translate("Form", name))
            self.listWidget.addItem(item)
        
        fp.close()

        

    def file_select(self):
        _translate = QtCore.QCoreApplication.translate
        if self.fileDialog.exec_():
            self.filename = self.fileDialog.selectedFiles()[0]
            self.imageName.setText(_translate("Form", self.filename))
            self.parse_image()

def section_parse(fp, pos):
    fp.seek(pos)
    cur_pos = pos
    name = fp.read(0x10).rstrip(b'\x00')

    next_section_pos = 0
    tmp = fp.read(0x8)
    
    for i in range(8):
        mul_value = 1
        for j in range(i):
            mul_value *= 0x100
        next_section_pos += mul_value*tmp[i]#ord(tmp[i])
    
    if pos == next_section_pos:
        return 0, name
    
    return next_section_pos, name

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
