from asyncio.windows_events import NULL
import json
import sys, os, time
from PyQt5.QtCore import QMutex, QWaitCondition, pyqtSignal, QThread
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5 import uic, QtGui, uic
import shutil, json, requests
from datetime import datetime
from pypdf import *
from requests import get
import login

down_ui = uic.loadUiType("./ui/download.ui")[0]
ORDER_API_BASE_URL = os.getenv("ORDER_API_BASE_URL", "").rstrip("/")

global ckdRow, product_id, workcount, content, cover

class DownDialog(QDialog, down_ui):
    
    def __init__(self, ckdRow, product_id, workcount, content, cover):
        loginClass = login.LoginWindow()

        super().__init__()

        self.ckdRow = ckdRow
        self.product_id = product_id
        self.workcount = workcount
        self.content = content
        self.cover = cover
        self.setupUi(self)
    
        self.downThread = DownThread(self)
        self.downThread.change_downTxt.connect(self.downTxt.setText)
        self.downThread.change_pgb.connect(self.pgb.setValue)
        self.downThread.change_percentTxt.connect(self.percentTxt.setText)
        self.downThread.change_stopBtn.connect(self.stopBtn.setText)
        self.stopBtn.clicked.connect(self.downStop)
        self.downThread.start()

        self.closeEvent = self.dialogDownClose

        # 폰트크기
        self.downTxt.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.percentTxt.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.stopBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))

    def downStop(self):
        btnTxt = self.stopBtn.text()
        if(btnTxt == "일시정지"):
            self.downThread.defPause()
        elif(btnTxt == "이어받기"):
            self.downThread.defResume()
            self.stopBtn.setText("일시정지")
        elif(btnTxt == "닫기"):
            self.downThread.stop()
            self.close()
    
    def dialogDownClose(self, event):

        btnTxt = self.stopBtn.text()
        if(btnTxt == "닫기"):
            self.downThread.stop()
            self.close()
            event.accept()
        else :                        
            quit_msg = "다운로드를 중단하시겠습니까?"
            reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.downThread.stop()
                self.close()
                event.accept()
            else:
                event.ignore()

class DownThread(QThread):
    change_downTxt = pyqtSignal(str)
    change_pgb = pyqtSignal(int)
    change_percentTxt = pyqtSignal(str)
    change_stopBtn = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.power = True
        self.sync = QMutex()
        self.pauseCondition = QWaitCondition()
        self.pause = False

    def run(self):

        td = datetime.today().strftime('%Y%m%d') # 날짜
        ckdRow = self.parent().ckdRow
        product_id = self.parent().product_id
        workcount = self.parent().workcount
        content = self.parent().content
        cover =self.parent().cover

        self.change_downTxt.emit(str(ckdRow) + '개의 PDF 중 0개 완료')

        for i in range(ckdRow):
            # 일시정지
            self.sync.lock()
            if(self.pause):
                self.change_stopBtn.emit('이어받기')
                self.pauseCondition.wait(self.sync)
            self.sync.unlock()

            if self.power == False: #쓰레드 정지되어있으면 False 
                break

            self.change_pgb.emit(0) # 디렉토리 생성
            self.change_percentTxt.emit('0%')

            # make dir
            path = '.\\' + td
            if not os.path.isdir(path):
                os.makedirs(path)
            
            if not os.path.exists(path + '\\커버\\' + product_id[i] + '_c-' + str(1) + '.pdf'):
                self.change_pgb.emit(10) # api 확인 후 커버 다운
                self.change_percentTxt.emit('10%')

                url = ORDER_API_BASE_URL + '?mode=dn_succ&product_id=' + product_id[i]
                url_Json = requests.get(url)
                text = url_Json.text
                down_data = json.loads(text)
                isSucc = str(down_data['response'])
                tellWhy = str(down_data['reason'])
                # print(url)
                # print(down_data) # 응답변수 100:성공 099:실패
                # print(down_data['response']) # 응답변수 100:성공 099:실패
                # print(down_data['reason']) # 성공, 실패사유

                if isSucc == '099':
                    self.change_downTxt.emit('서버오류 : ' + tellWhy)
                    self.quit()
                    break

                # cover Download
                # coverDown = open(path + '\\' + str(i) + 'cover.pdf','wb')
                # with coverDown as coverFile:
                #     response = get(cover[i])
                #     coverFile.write(response.content)
                #     coverFile.close()
                
                max_retries = 5
                for retry in range(max_retries):
                    try:
                        response = get(cover[i], timeout=5)  # 5초 동안 응답 기다림
                        response.raise_for_status()

                        with open(path + '\\' + str(i) + 'cover.pdf','wb') as coverDown:
                            coverDown.write(response.content)
                            coverDown.close()
                        print(f'커버 : {cover[i]} 다운로드 완료')
                        break
                    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
                        print(f'[재시도] 커버 {retry + 1}/{max_retries}: {err}')
                else:
                    print(f'{max_retries}번 시도 후에도 파일 다운로드 실패')

                self.change_pgb.emit(20) # 내지 다운
                self.change_percentTxt.emit('20%')

                # contents Download
                # contentsDown = open(path + '\\' + str(i) + 'contents.pdf','wb')
                # with contentsDown as contentsFile:
                #     response = get(content[i])
                #     contentsFile.write(response.content)
                #     contentsFile.close()

                # contents Download
                max_retries = 5
                for retry in range(max_retries):
                    try:
                        response = get(content[i], timeout=5)  # 5초 동안 응답 기다림
                        response.raise_for_status()

                        with open(path + '\\' + str(i) + 'contents.pdf','wb') as contentsDown:
                            contentsDown.write(response.content)
                            contentsDown.close()
                        print(f'컨텐츠 : {content[i]} 다운로드 완료')
                        break
                    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as err:
                        print(f'[재시도] 컨텐츠 {retry + 1}/{max_retries}: {err}')
                else:
                    print(f'{max_retries}번 시도 후에도 파일 다운로드 실패')

                self.change_pgb.emit(30) # 커버 개방
                self.change_percentTxt.emit('30%')

                #(2)커버파일 원본 사이즈490mm를 회전하고, 297x210mm로 줄이고, 텍스트idx 입력한 파일 
                coverPdfR = PdfReader(open(path + '\\' + str(i) + 'cover.pdf','rb'))
                
                covR = coverPdfR.pages[0]

                self.change_pgb.emit(40) # 커버 리사이즈
                self.change_percentTxt.emit('40%')

                #resize
                newHeight = 194 * 2.83464567 #194mm => pt
                newWidth = 152 * 2.83464567 #152mm => pt
                covR.scale_to(newWidth, newHeight) 

                self.change_pgb.emit(50) # 리사이즈pdf 작성
                self.change_percentTxt.emit('50%')

                # 가공한 PDF쓰기
                rotatedC = PdfWriter()
                rotatedC.add_page(covR)
                rotatedCStream = open(path + '\\' + str(i) + 'cover_resized.pdf','wb')
                rotatedC.write(rotatedCStream)
                time.sleep(0.1)
                rotatedCStream.close()
                # new_pdf2.stream.close()
                coverPdfR.stream.close()
                self.change_pgb.emit(60) # 커버 빈페이지
                self.change_percentTxt.emit('60%')

                # add cover blank
                bH = 194 * 2.83464567 # blankpage Height 194mm
                bW = 152 * 2.83464567 # blankpage Weith 152mm

                cC = PdfReader(open(path + '\\' + str(i) + 'cover_resized.pdf','rb')) # completed Cover
                cB = PdfWriter()    # cover Blankpage
                cB.append_pages_from_reader(cC)
                cB.add_blank_page(bW,bH)

                cBStream = open(path + '\\' + str(i) + 'cB.pdf','wb')
                cB.write(cBStream)
                time.sleep(0.1)
                cBStream.close()
                cC.stream.close()

                self.change_pgb.emit(70) # 내지 빈페이지
                self.change_percentTxt.emit('70%')

                # add content blank
                contC = PdfReader(open(path + '\\' + str(i) + 'contents.pdf','rb')) # content
                contPage = len(contC.pages)
                contB = PdfWriter()    # content Blankpage
                contB.append_pages_from_reader(contC)
                if contPage < 106 :
                    for k in range(106 - contPage):
                        contB.add_blank_page(bW,bH)

                contBStream = open(path + '\\' + str(i) + 'contB.pdf','wb')
                contB.write(contBStream)
                time.sleep(0.1)
                contBStream.close()
                contC.stream.close()

                self.change_pgb.emit(80) # pdf 병합
                self.change_percentTxt.emit('80%')

                # merge Pdf
                cP = PdfReader(open(path + '\\' + str(i) + 'cB.pdf','rb')) # coverBlanked
                innerPdf = PdfReader(open(path + '\\' + str(i) + 'contB.pdf','rb')) # contentBlanked
                mergedPdf = PdfMerger()
                mergedPdf.append(cP)
                mergedPdf.append(innerPdf)

                mergedPdf.write(path + '\\' + str(i) + 'completed.pdf')
                time.sleep(0.1)
                mergedPdf.close()
                cP.stream.close()
                innerPdf.stream.close()

                self.change_pgb.emit(90) # pdf 복사
                self.change_percentTxt.emit('90%')

                coverSource = path + '\\' + str(i) + 'cover.pdf'
                contentSource = path + '\\' + str(i) + 'completed.pdf'

                if not os.path.isdir(path + '\\커버'):
                    os.mkdir(path + '\\커버')
                if not os.path.isdir(path + '\\내지'):
                    os.mkdir(path + '\\내지')
                for j in range(int(workcount[i])):
                    shutil.copy(coverSource, path + '\\커버\\' + product_id[i] + '_c-' + str(j+1) + '.pdf')
                    shutil.copy(contentSource, path + '\\내지\\' + product_id[i] + '-' + str(contPage) + '-' + str(j+1) + '.pdf')
                    time.sleep(0.5)

                self.change_pgb.emit(100) # 정크삭제
                self.change_percentTxt.emit('100%')

                os.remove(path + '\\' + str(i) + 'completed.pdf')
                os.remove(path + '\\' + str(i) + 'contB.pdf')
                os.remove(path + '\\' + str(i) + 'cB.pdf')
                os.remove(path + '\\' + str(i) + 'cover_resized.pdf')
                os.remove(path + '\\' + str(i) + 'contents.pdf')
                os.remove(path + '\\' + str(i) + 'cover.pdf')
                self.change_downTxt.emit(str(ckdRow) + '개의 PDF 중 ' + str(i+1) + '개 완료')
            
            else:
                isSucc = '100'
                self.change_downTxt.emit(str(i+1) + '번 파일 존재. 다음 파일로 넘어갑니다.')
                self.change_pgb.emit(100)
                self.change_percentTxt.emit('100%')
                time.sleep(1)

        if isSucc != '099':
            self.change_downTxt.emit('다운로드 완료')

        self.change_stopBtn.emit('닫기')

    def stop(self):
        self.power = False
        self.quit()
        self.wait(5000)  # 5초 대기 (바로 안꺼질수도)

    def defResume(self):
        self.sync.lock()
        self.pause = False
        self.sync.unlock()
        self.pauseCondition.wakeAll()

    def defPause(self):
        self.sync.lock()
        self.pause = True
        self.sync.unlock()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downDialog = DownDialog()
    downDialog.show()
    app.exec_()
