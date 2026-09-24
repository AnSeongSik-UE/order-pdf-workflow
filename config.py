import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5 import uic, QtGui,  uic
import configparser
import login

config_ui = uic.loadUiType("./ui/config.ui")[0]

class ConfigDialog(QDialog, config_ui):

    def __init__(self):
        global setting
        loginClass = login.LoginWindow()

        super().__init__()
        self.setupUi(self)

        config = configparser.ConfigParser()
        config.read('./config.ini')
        setting = config['setting']

        # 폰트크기
        self.lb1.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.lb2.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.lb3.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.regBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        
        self.idTxt.setText(setting['id'])
        self.pwTxt.setText(setting['pw'])
        self.fontTxt.setText(setting['font'])
        self.onlyInt = QtGui.QIntValidator()
        self.fontTxt.setValidator(self.onlyInt)
        self.regBtn.clicked.connect(self.reg) # 등록 클릭

    def reg(self):
        global setting
        config = configparser.ConfigParser()
        config['setting'] = {'id': self.idTxt.text(), 'pw': self.pwTxt.text(), 'font': self.fontTxt.text()}

        try:
            with open('config.ini', 'w') as configfile: #컨피그파일안에 데이터 쓰기
                config.write(configfile)

            if setting['font'] == self.fontTxt.text():
                QmsgBox = QMessageBox()
                QmsgBox.information(self, '확인', '등록이 완료되었습니다.')
                self.close()
            else:
                QmsgBox = QMessageBox()
                QmsgBox.information(self, '확인', '등록이 완료되었습니다.\n폰트는 프로그램 다시 시작 후 적용됩니다.')
                self.close()
        except:
            QmsgBox.warning(self, '오류', '등록에 실패했습니다. 다시 확인해주세요.')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    configDialog = ConfigDialog()
    configDialog.show()
    app.exec_()
