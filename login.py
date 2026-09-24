import sys
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5 import uic, QtGui
import main
import configparser

login_ui = uic.loadUiType("./ui/login.ui")[0]

class LoginWindow(QMainWindow, login_ui):
    fontSize = 8
    def __init__(self):
        global setting
        
        try:
            config = configparser.ConfigParser()
            config.read('./config.ini')
            setting = config['setting']
            self.fontSize = int(setting['font'])
        except:
            QmsgBox = QMessageBox()
            QmsgBox.warning(self, '오류', 'INI 파일을 찾을수 없습니다.')
            self.exit(0)

        super().__init__()
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.lgn)# 로그인
        self.pwInput.returnPressed.connect(self.enter)

        # 폰트크기
        self.titleTxt.setFont(QtGui.QFont("돋움", self.fontSize+17,QtGui.QFont.Bold))
        self.idTxt.setFont(QtGui.QFont("돋움", self.fontSize))
        self.pwTxt.setFont(QtGui.QFont("돋움", self.fontSize))
        self.loginBtn.setFont(QtGui.QFont("돋움", self.fontSize))
    
    def enter(self):
        self.lgn()

    def lgn(self):
        global setting
        self.mainWindow = main.MainWindow()
        if (self.idInput.text() == setting['id']) & (self.pwInput.text() == setting['pw']):
            self.mainWindow.show()
            self.close()
        else:
            QmsgBox = QMessageBox()
            QmsgBox.information(self, '확인', 'ID/PW 확인해주세요.')                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    loginWindow.show()
    app.exec_()  
