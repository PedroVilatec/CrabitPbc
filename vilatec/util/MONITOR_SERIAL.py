# -*- coding: utf-8 -*-
import binascii
import re
import sys
from pzem_004 import BTPOWER
from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QTextDocumentWriter
from PyQt5.QtCore import QTimer
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *
sys.stdout.write("\x1b]2;%s\x07" % 'Monitor serial')
TITLE = "MONITOR SERIAL"
ABOUT_TITLE = "MONITOR SERIAL V1.0"
ABOUT_STRING = "V0.1\t2015-12-12: 完成基本功能\n"\
    "V0.2\t2016-06-06: 优化串口收发\n"\
    "V0.3\t2016-08-20: 串口能够接收中文\n"\
    "V0.4\t2016-09-03: 移植到PyQt5, 完成十六进制发送\n"\
    "V0.5\t2016-09-22: 串口接收中文OK, 串口十六进制收发OK\n"\
    "\n-------------------------------------------\n"\
    "Todo list:\n"

class PyQt_Serial(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.CreateItems()
        self.CreateLayout()
        self.CreateSignalSlot()

        self.setWindowTitle('MONITOR SERIAL')
        self.setWindowIcon(QIcon('./icon.ico'))
        self.setFont(QFont('arial', 9))
        self.pzem = BTPOWER()

        self.sendCount = 0
        self.receiveCount = 0
        self.encoding = 'utf-8'
        self.updateTimer.start(100)

    def CreateItems(self):
        self.com = QSerialPort()

        self.comNameLabel = QLabel('Porta')
        self.comNameLabel.setFixedWidth(80)
        self.comNameCombo = QComboBox()
        self.on_refreshCom()

        self.comNameCombo.setFixedWidth(80)
        self.baudLabel = QLabel('Baud')
        self.baudLabel.setFixedWidth(80)
        self.baudCombo = QComboBox()
        self.baudCombo.addItems(
            ('1200', '9600', '19200','57600', '74880', '115200', '250000', '256000'))
        self.baudCombo.setEditable(True)
        self.baudCombo.setCurrentIndex(1)
        self.baudCombo.setFixedWidth(80)
        self.bupt = QLabel('')  # BUPT
        self.bupt.setFont(QFont('Arial', 40, italic=True))

        self.comencodingLabel = QLabel('Codificação')
#         self.comencodingCombo = QComboBox()
#         self.comencodingCombo.addItems(('UTF-8', 'GBK'))
        self.UTF8Button = QRadioButton('UTF-8')
        self.GBKButton = QRadioButton('GBK')
        self.encodingGroup = QButtonGroup()
        self.encodingGroup.addButton(self.UTF8Button, 0)
        self.encodingGroup.addButton(self.GBKButton, 1)
        self.UTF8Button.setChecked(True)
        self.openButton = QPushButton('Abrir')
        self.openButton.setFixedWidth(80)
        self.closeButton = QPushButton('Fechar')
        self.closeButton.setFixedWidth(80)
        self.clearReceivedButton = QPushButton('Limpa buffer')
        self.clearReceivedButton.setFixedWidth(165)
        self.stopShowingButton = QPushButton('Parar')
        self.stopShowingButton.setFixedWidth(165)
        self.hexShowingCheck = QCheckBox('Mostra hexadecimal')
        self.hexShowingCheck.setFixedWidth(165)
        self.isPzem = QCheckBox('Ler Pzem')
        self.isPzem.setFixedWidth(165)        
        self.saveReceivedButton = QPushButton('Salvar dados')
        self.saveReceivedButton.setFixedWidth(165)
        self.openButton = QPushButton('Abrir')
        self.openButton.setFocus()
        self.openButton.setFixedWidth(80)
        self.closeButton = QPushButton('Fechar')
        self.closeButton.setFixedWidth(80)
        self.refreshComButton = QPushButton('Atualizar')
        self.aboutButton = QPushButton('Sobre')
        self.aboutButton.setFixedWidth(80)
        self.aboutPyQtButton = QPushButton('Sobre PyQt5')
        self.aboutPyQtButton.setFixedWidth(80)

        self.receivedDataEdit = QPlainTextEdit()
        self.receivedDataEdit.setReadOnly(True)
        self.receivedDataEdit.setFont(QFont('Piboto Condensed', 8))

        self.inputEdit = QLineEdit()
        #~ self.inputEdit.setFixedHeight(70)
        self.inputEdit.setFont(QFont('Piboto Condensed', 11))
        self.sendButton = QPushButton('Enviar')
        self.sendButton.setFixedWidth(105)
        self.sendButton.setFixedHeight(70)
        self.hexSendingCheck = QCheckBox('Enviar hexadecimal')
        self.timerSendCheck = QCheckBox('Ciclo de envio')
        self.timerPeriodEdit = QLineEdit('1000')
        self.spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.clearInputButton = QPushButton('Limpar Entrada')
        self.clearCouterButton = QPushButton('Zerar contador')

        self.comStatus = QLabel('Status：COM  Fechada')
        self.sendCountLabel = QLabel('Enviar contagem：0')
        self.receiveCountLabel = QLabel('Receber contagem：0')

        self.sendTimer = QTimer()
        self.updateTimer = QTimer()

        self.closeButton.setEnabled(False)
        self.sendButton.setEnabled(False)

    def CreateLayout(self):
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.comNameLabel, 0, 0)
        self.mainLayout.addWidget(self.comNameCombo, 0, 1)
        self.mainLayout.addWidget(self.baudLabel, 1, 0)
        self.mainLayout.addWidget(self.baudCombo, 1, 1)
        self.mainLayout.addWidget(self.comencodingLabel, 2, 0)
#         self.mainLayout.addWidget(self.comencodingCombo, 2, 1)
        self.mainLayout.addWidget(self.UTF8Button, 3, 0)
        self.mainLayout.addWidget(self.GBKButton, 3, 1)
        self.mainLayout.addWidget(self.openButton, 5, 0)
        self.mainLayout.addWidget(self.closeButton, 5, 1)
        self.mainLayout.addWidget(self.refreshComButton, 6, 0, 1, 2)
        self.mainLayout.addWidget(self.clearReceivedButton, 7, 0, 1, 2)
        self.mainLayout.addWidget(self.stopShowingButton, 8, 0, 1, 2)
        self.mainLayout.addWidget(self.hexShowingCheck, 9, 0, 1, 2)
        self.mainLayout.addWidget(self.isPzem, 10, 0, 1, 2)
        self.mainLayout.addWidget(self.saveReceivedButton, 11, 0, 1, 2)
        self.mainLayout.addWidget(self.aboutButton, 12, 0)
        self.mainLayout.addWidget(self.aboutPyQtButton, 13, 1)

        self.mainLayout.addWidget(self.receivedDataEdit, 0, 2, 12, 6)

        self.mainLayout.addWidget(self.inputEdit, 13, 0, 1, 7)
        self.mainLayout.addWidget(self.sendButton, 13, 7)
        self.mainLayout.addWidget(self.hexSendingCheck, 14, 0, 1, 2)
        self.mainLayout.addWidget(self.timerSendCheck, 14, 2, 1, 2)
        self.mainLayout.addWidget(self.timerPeriodEdit, 14, 4)
        self.mainLayout.addItem(self.spacer, 14, 5)
        self.mainLayout.addWidget(self.clearInputButton, 14, 6)
        self.mainLayout.addWidget(self.clearCouterButton, 14, 7)
        self.mainLayout.addWidget(self.comStatus, 15, 0, 1, 3)
        self.mainLayout.addWidget(self.sendCountLabel, 15, 4, 1, 2)
        self.mainLayout.addWidget(self.receiveCountLabel, 15, 6, 1, 2)
        self.mainLayout.setSpacing(5)

        self.setLayout(self.mainLayout)
        #~ self.setFixedSize(700, self.height())

    def CreateSignalSlot(self):
        self.openButton.clicked.connect(self.on_openSerial)  # 打开串口
        self.closeButton.clicked.connect(self.on_closeSerial)  # 关闭串口
        self.com.readyRead.connect(self.on_receiveData)  # 接收数据
        self.sendButton.clicked.connect(self.on_sendData)  # 发送数据
        self.refreshComButton.clicked.connect(self.on_refreshCom)  # 刷新串口状态
        self.aboutButton.clicked.connect(self.on_aboutButton)  # 修改记录
        self.aboutPyQtButton.clicked.connect(self.on_aboutPyQtButton)  # 关于PyQt
        self.clearInputButton.clicked.connect(self.inputEdit.clear)  # 清空输入
        self.clearReceivedButton.clicked.connect(
            self.receivedDataEdit.clear)  # 清空接收
        self.stopShowingButton.clicked.connect(self.on_stopShowing)  # 停止显示
        self.clearCouterButton.clicked.connect(self.on_clearCouter)  # 清空计数

        self.saveReceivedButton.clicked.connect(
            self.on_saveReceivedData)  # 保存数据

        self.timerSendCheck.clicked.connect(self.on_timerSendChecked)  # 定时发送开关
        self.sendTimer.timeout.connect(self.on_sendData)  # 定时发送

        self.updateTimer.timeout.connect(self.on_updateTimer)  # 界面刷新
        self.hexShowingCheck.stateChanged.connect(
            self.on_hexShowingChecked)  # 十六进制显示
        self.timerPeriodEdit.textChanged.connect(self.on_timerSendChecked)
        self.UTF8Button.clicked.connect(self.on_setEncoding)
        self.GBKButton.clicked.connect(self.on_setEncoding)

        self.hexSendingCheck.stateChanged.connect(
            self.on_hexSendingChecked)  # 十六进制发送

    def keyPressEvent(self, e):
        print("event", e)
        if e.key()  == Qt.Key_Return or e.key() == Qt.Key_Enter:
            if self.com.isOpen():
                    self.on_sendData()


    def on_refreshCom(self):
        self.comNameCombo.clear()
        com = QSerialPort()
        for info in QSerialPortInfo.availablePorts():
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.comNameCombo.addItem(info.portName())
                com.close()

    def on_setEncoding(self):
        if self.encodingGroup.checkedId() == 0:
            self.encoding = 'utf-8'
        else:
            self.encoding = 'gbk'

    def closePzem(self):
        if hasattr (self, "timer"):
            self.timer.stop()
            self.timer.timeout.disconnect()
        if hasattr (self, "pzem"):
            if hasattr (self.pzem, "ser"):
                self.pzem.ser.close()

    def print_pzem(self):

        for key, value in self.pzem.values.items():
            self.receivedDataEdit.moveCursor(QTextCursor.End)
            self.receivedDataEdit.insertPlainText("{}: {} ".format(key, value))
            self.receivedDataEdit.ensureCursorVisible()  
        self.receivedDataEdit.insertPlainText("\n")          

    def on_openSerial(self):
        comName = self.comNameCombo.currentText()
        if self.isPzem.isChecked():
            self.pzem.serial_port(comName)
            self.timer = QTimer()
            self.timer.timeout.connect(self.print_pzem)
            self.timer.start(2000)    
            
        else:
            comBaud = int(self.baudCombo.currentText())
            self.com.setPortName(comName)

            try:
                if self.com.open(QSerialPort.ReadWrite) == False:
                    QMessageBox.critical(self, 'Erro Grave', 'Falha na abertura da Serial')
                    return
            except:
                QMessageBox.critical(self, 'Erro Grave', 'Falha na abertura da Serial')
                return

            self.com.setBaudRate(comBaud)
            self.comStatus.setText('Status：%s  aberta   a %s' % (comName, comBaud))

        if self.timerSendCheck.isChecked():
            self.sendTimer.start(int(self.timerPeriodEdit.text()))

        self.openButton.setEnabled(False)
        self.closeButton.setEnabled(True)
        self.comNameCombo.setEnabled(False)
        self.baudCombo.setEnabled(False)
        self.sendButton.setEnabled(True)
        self.refreshComButton.setEnabled(False)
        

    def on_closeSerial(self):
        try:
                self.closePzem()
                self.com.close()
                self.openButton.setEnabled(True)
                self.closeButton.setEnabled(False)
                self.comNameCombo.setEnabled(True)
                self.baudCombo.setEnabled(True)
                self.sendButton.setEnabled(False)
                self.refreshComButton.setEnabled(True)
                self.comStatus.setText('Status：%s  fechada' % self.com.portName())
                if self.sendTimer.isActive():
                    self.sendTimer.stop()
        except Exception as e:
                print(e)

    def on_timerSendChecked(self):
        if self.com.isOpen():
            if self.timerSendCheck.isChecked():
                self.sendTimer.start(int(self.timerPeriodEdit.text()))
            else:
                self.sendTimer.stop()
        return

    def on_stopShowing(self):
        if self.stopShowingButton.text() == 'Parar':
            self.stopShowingButton.setText('Mostrar')
        else:
            self.stopShowingButton.setText('Parar')

    def on_clearCouter(self):
        self.sendCount = 0
        self.receiveCount = 0
        pass

    def on_updateTimer(self):
        self.sendCountLabel.setText('Enviar contagem：%d' % self.sendCount)
        self.receiveCountLabel.setText('Receber contagem：%d' % self.receiveCount)
        pass

    def on_sendData(self):
        txData = self.inputEdit.text()+'\r\n'
        if len(txData) == 0:
            return
        if self.hexSendingCheck.isChecked():

            s = txData.replace(' ', '')
            if len(s) % 2 == 1:  # 如果16进制不是偶数个字符,去掉最后一个
                QMessageBox.critical(self, 'Erro', 'Não é hexadecimal')
                return
#             pattern = re.compile('[^0-9a-fA-F]')
#             r = pattern.findall(s)
#             if len(r) != 0:
#                 QMessageBox.critical(self, '错误', '包含非十六进制数')
#                 return

            if not s.isalnum():
                QMessageBox.critical(self, 'Erro', 'Contém números hexadecimais')
                return

            try:
                hexData = binascii.a2b_hex(s)
            except:
                QMessageBox.critical(self, 'Erro', 'Erro de codificação')
                return

            try:
                n = self.com.write(hexData)
            except:
                QMessageBox.critical(self, 'Anormal', 'Erro de envio hexadecimal')
                return
        else:
            txData = txData+"\n"
            n = self.com.write(txData.encode(self.encoding, "ignore"))
        self.sendCount += n

    def on_receiveData(self):
        try:
            receivedData = bytes(self.com.readAll())
        except:
            QMessageBox.critical(self, 'Erro grave', 'A porta serial teve erro de dados')
        if len(receivedData) > 0:
            self.receiveCount += len(receivedData)
            if self.stopShowingButton.text() == 'Parar':
                if self.hexShowingCheck.isChecked() == False:
                    receivedData = receivedData.decode(self.encoding, 'ignore').replace("<", "").replace(">", "")
                    receivedData = receivedData.replace(",", "   ")
                    self.receivedDataEdit.moveCursor(QTextCursor.End)
                    self.receivedDataEdit.insertPlainText(receivedData)
                    self.receivedDataEdit.ensureCursorVisible()


                else:
                    data = binascii.b2a_hex(receivedData).decode('ascii')
                    pattern = re.compile('.{2,2}')
                    hexStr = ' '.join(pattern.findall(data)) + ' '
                    self.receivedDataEdit.insertPlainText(hexStr.upper())
                    self.receivedDataEdit.ensureCursorVisible()

    def on_hexShowingChecked(self):
        self.receivedDataEdit.insertPlainText('\n')

    def on_hexSendingChecked(self):
        if self.hexSendingCheck.isChecked():
            data = self.inputEdit.text().upper()
            self.inputEdit.clear()
            self.inputEdit.setText(data)

    def on_saveReceivedData(self):
        fileName, fileType = QFileDialog.getSaveFileName(
            self, 'Salvar', 'data', "Documento de texto(*.txt);;Todos os arquivos(*.*)")

        if fileName:
            print(fileName)
            writer = QTextDocumentWriter(fileName)
            if writer.write(self.receivedDataEdit.document()):
                print("Documento salvo com sucesso em {}".format(fileName))
            else:
                print("Falha ao salvar o documento")

    def on_aboutButton(self):
        QMessageBox.about(self, ABOUT_TITLE, ABOUT_STRING)

    def on_aboutPyQtButton(self):
        QMessageBox.aboutQt(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PyQt_Serial()
    win.show()
    app.exec_()
    app.exit()
