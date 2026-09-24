import sys, os
from turtle import down
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog, QHBoxLayout, QWidget, QCheckBox, QTableWidgetItem
from PyQt5 import uic,QtCore, QtGui, QtWidgets, uic
import requests, json
import pandas as pd
from PySide2.QtCore import QDate
from datetime import datetime
import download, config, login

from PyQt5.QtCore import QFile, QFileInfo, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableView

main_ui = uic.loadUiType("./ui/main.ui")[0]
ORDER_API_BASE_URL = os.getenv("ORDER_API_BASE_URL", "").rstrip("/")

class MainWindow(QMainWindow, main_ui):
    resized = QtCore.pyqtSignal()

    def __init__(self):
        loginClass = login.LoginWindow()
        
        super().__init__()
        self.setupUi(self)
        self.t1_table.hideColumn(13)
        self.t1_table.hideColumn(14)
        
        self.resized.connect(self.resizeWidget) # 창 크기따라 사이즈변경

       # self.resized.connect(self.resizeWidget1) # 창 크기따라 사이즈변경

        self.t1_searchBtn.clicked.connect(self.SelectData) # 검색 클릭시 이벤트
        self.t1_excelDownBtn.clicked.connect(self.Xls_export) #엑셀 내려받기
        self.t1_filterBtn.clicked.connect(self.filterData) #필터
        self.t1_pdfDownBtn.clicked.connect(self.pdfDown)    # pdf 다운
        self.t1_configBtn.clicked.connect(self.cfg)         # config
        self.t2_searchExcelBtn.clicked.connect(self.Load_xls) #운송장 엑셀 업로드
        self.t2_oneSendBtn.clicked.connect(self.TrackingNumber_submit) #운송장 전송
        self.t2_excelSendBtn.clicked.connect(self.Xls_TrackingNumber_submit) #엑셀운송장 전송
        self.t2_seeTaxcodeBtn.clicked.connect(self.Delivery_Code) #엑셀운송장 전송

        self.t1_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)# 스크롤 항상 켜져있기 
        self.t1_Check_choice_Button.clicked.connect(self.ckbox_choice) #선택체크
        #합성일 FIX 동시 스크롤  Strat
        #self.tableWidget.verticalScrollBar().valueChanged.connect(self.t1_table.verticalScrollBar().setValue)
        #self.t1_table.verticalScrollBar().valueChanged.connect(self.tableWidget.verticalScrollBar().setValue)
       
        #self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        #End

        


        pix = QPixmap(".\\ui\\excelEx.png")
        item = QtWidgets.QGraphicsPixmapItem(pix)
        scene = QtWidgets.QGraphicsScene(self)
        scene.addItem(item)
        self.t2_gb2_imageView.setScene(scene)

        ##오늘날짜로 날짜 세팅 S##
        now = QDate.currentDate()    
        yyyy = now.toString('yyyy')
        mm = now.toString('M')
        dd = now.toString('d')  
        self.t1_preDate.setDate(QtCore.QDate(int(yyyy), int(mm), int(dd)))
        self.t1_afterDate.setDate(QtCore.QDate(int(yyyy), int(mm), int(dd)))
        self.t2_sendDate.setDate(QtCore.QDate(int(yyyy), int(mm), int(dd)))
        ##오늘날짜로 날짜 세팅 E ##  

        # AlignDelegate 가운데 정렬 Class 나중에 분리 하기
        delegate = AlignDelegate(self.t1_table)
        self.t1_table.setItemDelegateForColumn(1, delegate)
        self.t1_table.setItemDelegateForColumn(2, delegate)
        self.t1_table.setItemDelegateForColumn(3, delegate)
        self.t1_table.setItemDelegateForColumn(4, delegate)
        self.t1_table.setItemDelegateForColumn(5, delegate)
        self.t1_table.setItemDelegateForColumn(6, delegate)
        self.t1_table.setItemDelegateForColumn(7, delegate)
        self.t1_table.setItemDelegateForColumn(10, delegate)
        self.t1_table.setItemDelegateForColumn(11, delegate)
        self.t1_table.setItemDelegateForColumn(12, delegate) 
        self.t1_table.setItemDelegateForColumn(13, delegate)

        self.t1_table.setItemDelegateForColumn(14, delegate)  

        #합성일자 Fix 가운데 정렬
        #delegate1 = AlignDelegate(self.tableWidget)
        #self.tableWidget.setItemDelegateForColumn(0, delegate1)           

        self.t1_table.setItemDelegateForColumn(14, delegate)               

        
        #달력팝업
        self.t1_preDate.setCalendarPopup(True)
        self.t1_afterDate.setCalendarPopup(True)
        self.t2_sendDate.setCalendarPopup(True)

        #체크박스 전체체크
        self.t1_checkAll.stateChanged.connect(self.ckbox_sw)
        
        # 폰트크기
        self.t1_lb1.setFont(QtGui.QFont("돋움", loginClass.fontSize)) # 날짜
        self.t1_preDate.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb2.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_afterDate.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_searchBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb3.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 검색건수
        self.searchResultNum.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb4.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb9.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 검색건수
        self.searchBookNum.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb10.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_excelDownBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize)) # 엑셀저장 삭제 환경설정
#        self.t1_delBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_configBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb5.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # PDF 다운
        self.t1_pdfCombo.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_pdfDownBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb6.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 필터
        self.t1_filterCombo.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_filterTxt.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_filterBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
#        self.t1_lb7.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 최대페이지
#        self.t1_maxPage.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t1_lb8.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 전체선택
        self.t2_gb1_lb1.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 개별전송
        self.t2_productNum.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_gb1_lb2.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_taxNum.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_gb1_lb3.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_taxCombo.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_gb1_lb4.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_sendDate.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_oneSendBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_gb2_lb1.setFont(QtGui.QFont("돋움", loginClass.fontSize))  # 엑셀 전송
        self.t2_excelPath.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_searchExcelBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_excelSendBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.t2_seeTaxcodeBtn.setFont(QtGui.QFont("돋움", loginClass.fontSize))
        self.label.setFont(QtGui.QFont("돋움", loginClass.fontSize))

        self.mainTab.setCurrentIndex(0) #첫번째 탭 선택

    def Delivery_Code(self):
        QmsgBox = QMessageBox()
        QmsgBox.information(self, '택배 코드 도움말', '대한통운 : 1    \n 한진택배 : 2    \n 아주택배 : 3    \n 하나로택배 : 4    \n CJ택배 : 5    \n 우체국택배 : 6    \n 로젠택배 : 7    \n 용마로지스 : 8    \n 현대택배 : 9    \n 옐로우캡 : 10    \n  KGB택배 : 11    \n 동부택배 : 12    \n KG로지스: 13   \n 직접배송 : 0   ') 
    
    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def Xls_TrackingNumber_submit(self):#엑셀 운송장 전송
        counting = 0
        try: 
            data_np = pd.DataFrame.to_numpy(dataset3)
            for i in range(0,dataset3.shape[0]):
                mode      = "deli_ins"           # 고정
                order_id  = str(data_np[i][0]) #상품번호
                order_id  = order_id.replace(" " , "") #상품번호 공백제거
                deli_no   = str(data_np[i][1]) #송장번호
                deli_com  = str(data_np[i][2]) #택배번호
                deli_date = str(data_np[i][3]) #발송날짜
                if(deli_no == 'nan'):
                    deli_no = ''
                Update_URL = ORDER_API_BASE_URL + "?mode=deli_ins&order_id="+order_id+"&deli_no="+deli_no+"&deli_com="+deli_com+"&deli_date=" + deli_date
                #print(Update_URL)
                url_Json = requests.get(Update_URL)
                text = url_Json.text                 
                tables_data = json.loads(text)
                if tables_data['response'] == '100' : # 응답변수 100:성공   
                    counting = counting +1
                else :
                    QmsgBox.warning(self, '오류', '파일 및 데이터를 확인 해주세요')

            QmsgBox = QMessageBox()
            QmsgBox.information(self, '확인', str(dataset3.shape[0]) + "개 중 " + str(counting) + "개 업데이트 완료")
            
        except NameError : #참조할 변수가 없을경우 예외처리
            print("파일확인요망")

    #운송장 전송
    def TrackingNumber_submit(self): 
        order_id=self.t2_productNum.text() #상품번호
        deli_no=self.t2_taxNum.text() #송장번호
        deli_date=self.t2_sendDate.text() #발송날짜 Y-m-d 로 확인하기
        deli_com=self.t2_taxCombo.currentText() #택배코드
        
        if order_id == '' or deli_no == '' or deli_date == '' or deli_com == '':
            QmsgBox = QMessageBox()
            QmsgBox.warning(self, '오류', '운송장 정보를 모두 입력해주세요.')
            return

        data = '{ "대한통운": 1, "한진택배": 2, "아주택배": 3, "하나로택배":4, "CJ택배": 5, "우체국택배": 6,"로젠택배": 7, "용마로지스": 8, "현대택배": 9, "옐로우캡": 10, "KGB택배": 11, "동부택배": 12, "KG로지스": 13, "직접배송": 0}'
        json_data = json.loads(data)
        deliver_code = str(json_data[deli_com]) # 택배코드를 Json 형태로 만들어서 사용함
        url = ORDER_API_BASE_URL + "?mode=deli_ins&order_id="+order_id+"&deli_no="+deli_no+"&deli_com="+deliver_code+"&deli_date=" + deli_date
        url_Json = requests.get(url)
        text = url_Json.text                 
        tables_data = json.loads(text)     

        if(tables_data['response'] == '100'):
            QmsgBox = QMessageBox()
            QmsgBox.information(self, '확인', '전송이 완료되었습니다.')
        else :
            QmsgBox = QMessageBox()
            QmsgBox.warning(self, '오류', '전송 실패, 다시 확인해주세요.')
        
        print(tables_data['response']) # 응답변수 100:성공

    def resizeWidget(self):
        mw = self.width()
        mh = self.height()
        tw = self.width()-50
        th = self.height()-200
        self.mainTab.resize(mw, mh)
        self.t1_table.resize(tw, th)
 
        #self.resizeWidget1()
        
    # def resizeWidget1(self): # 고정 컬럼 사이즈 조절

    #     th = self.height()-200   

    #     self.tableWidget.resize(78, th) # 합성일 FIX 
    #     self.tableWidget.setColumnWidth(0,78) # 합성일 FIX 컬럼사이즈 조절
         
       
    #체크박스 선택체크
    def ckbox_choice(self) :  

        if self.t1_table.rowCount() == 0:
            QMessageBox.information(self, "알림", "행이 없습니다.")
            return        

        selected_rows = [item.row() for item in self.t1_table.selectedItems()]        
        for i in selected_rows:
            self.checkBoxList[i].setChecked(True)                
    


 

    #체크박스 전체선택   
    def ckbox_sw(self) :

        if self.t1_table.rowCount() == 0:
            QMessageBox.information(self, "알림", "행이 없습니다.")
            return        
                
        # count = int(self.searchResultNum.text())
        count = self.t1_table.rowCount()
        if self.t1_checkAll.isChecked() :
            for i in range(count):
                self.checkBoxList[i].setChecked(True)
        else :
            for i in range(count):
                self.checkBoxList[i].setChecked(False)    
    
    #필터적용
    def filterData(self):
        global row_count

        filterText = self.t1_filterTxt.text()
        if filterText == '':
            QmsgBox = QMessageBox()
            QmsgBox.warning(self, '오류', '필터값을 입력해주세요.')
            return
        if self.t1_table.rowCount() == 0:
            QmsgBox = QMessageBox()
            QmsgBox.warning(self, '오류', '검색 결과가 없습니다.')
            return

        self.t1_table.clearContents()
        filtered_list = []
        count=0
        row_count=0
        book_cnt = 0

        if self.t1_filterCombo.currentText() == '주문자':
            filtered_list = [data for data in tables_data['data'] if filterText in data['name']]
        elif self.t1_filterCombo.currentText() == '주문번호':
            filtered_list = [data for data in tables_data['data'] if filterText in data['order_id']]
        elif self.t1_filterCombo.currentText() == '상품번호':
            for d1 in tables_data['data']:
                for d2 in d1['product']:
                    if d2['product_id'] == filterText:
                        filtered_list.append({'state': d1['state'], 'order_id': d1['order_id'], 'order_date': d1['order_date'], 'pdf_date': d1['pdf_date'], 'name': d1['name'], 'phone': d1['phone'], 'addr': d1['addr'], 'addr1': d1['addr1'], 'addr2': d1['addr2'], 'deli_no': d1['deli_no'], 'deli_com': d1['deli_com'], 'deli_date': d1['deli_date'], 'product': [d2]})
        elif self.t1_filterCombo.currentText() == '송장번호':
            filtered_list = [data for data in tables_data['data'] if filterText in data['deli_no']]
        elif self.t1_filterCombo.currentText() == '권수':
            for d1 in tables_data['data']:
                for d2 in d1['product']:
                    if str(d2['workcount']) == filterText:
                        filtered_list.append({'state': d1['state'], 'order_id': d1['order_id'], 'order_date': d1['order_date'], 'pdf_date': d1['pdf_date'], 'name': d1['name'], 'phone': d1['phone'], 'addr': d1['addr'], 'addr1': d1['addr1'], 'addr2': d1['addr2'], 'deli_no': d1['deli_no'], 'deli_com': d1['deli_com'], 'deli_date': d1['deli_date'], 'product': [d2]})

        for author in filtered_list:           
            for product in author['product']:
                row_count=row_count+1
        self.t1_table.setRowCount(row_count) #table row 결정

        #self.tableWidget.setRowCount(row_count) #합성일자 Fix table row 결정



        for author in filtered_list:           
            for product in author['product']:
                item_name = QTableWidgetItem(author['pdf_date'])  #1 합성일 pdf_date
                self.t1_table.setItem(count,1,item_name)  
                item_name = QTableWidgetItem(author['order_date'])  #2 주문일 'order_date': 
                self.t1_table.setItem(count,2,item_name)  
                item_name = QTableWidgetItem(author['deli_date'])  #3 발송일  deli_date
                self.t1_table.setItem(count,3,item_name)  
                item_name = QTableWidgetItem(author['order_id'])  #4 주문번호 'order_id': 
                self.t1_table.setItem(count,4,item_name)  
                item_name = QTableWidgetItem(product['product_id'])   #5 상품번호 'product':  ->'product_id': : 
                self.t1_table.setItem(count,5,item_name)  
                item_name = QTableWidgetItem(author['name'])  #6 주문자 'name': 
                self.t1_table.setItem(count,6,item_name)                      
                item_name = QTableWidgetItem(author['phone'])  #7 연락처 'phone': 
                self.t1_table.setItem(count,7,item_name)  
                item_name = QTableWidgetItem(author['addr']) #8 주소  'addr': 
                self.t1_table.setItem(count,8,item_name)  
                item_name = QTableWidgetItem(product['p_name'])  #9 상품명 'product':  ->  'p_name':  
                self.t1_table.setItem(count,9,item_name)  
                item_name = QTableWidgetItem(author['deli_no'])  #10 송장번호 deli_no
                self.t1_table.setItem(count,10,item_name) 
                if author['state'] == 3:
                    item_name = QTableWidgetItem(author['deli_com'])  #11 택배코드 deli_com
                    if (author['deli_com'] == '0') :
                        item_name = QTableWidgetItem('직접배송')
                    if (author['deli_com'] == '1') :
                        item_name = QTableWidgetItem('대한통운')
                    if (author['deli_com'] == '2') :
                        item_name = QTableWidgetItem('하나로택배')    
                    if (author['deli_com'] == '3') :
                        item_name = QTableWidgetItem('아주택배') 
                    if (author['deli_com'] == '4') :
                        item_name = QTableWidgetItem('한진택배') 
                    if (author['deli_com'] == '5') :
                        item_name = QTableWidgetItem('CJ택배') 
                    if (author['deli_com'] == '6') :
                        item_name = QTableWidgetItem('우체국택배')     
                    if (author['deli_com'] == '7') :
                        item_name = QTableWidgetItem('로젠택배') 
                    if (author['deli_com'] == '8') :
                        item_name = QTableWidgetItem('용마로지스') 
                    if (author['deli_com'] == '9') :
                        item_name = QTableWidgetItem('현대택배') 
                    if (author['deli_com'] == '10') :
                        item_name = QTableWidgetItem('옐로우캡') 
                    if (author['deli_com'] == '11') :
                        item_name = QTableWidgetItem('KGB택배') 
                    if (author['deli_com'] == '12') :
                        item_name = QTableWidgetItem('동부택배')     
                    if (author['deli_com'] == '13') :
                        item_name = QTableWidgetItem('KG로지스')
                else:
                    item_name = QTableWidgetItem('')
                self.t1_table.setItem(count,11,item_name) 
                item_name = QTableWidgetItem(str(product['workcount']))  #12 권수 'product': -> 'workcount':  
                self.t1_table.setItem(count,12,item_name) 
                item_name = QTableWidgetItem(product['files'][0])  #13 내지  
                self.t1_table.setItem(count,13,item_name) 
                self.t1_table.hideColumn(13)
                item_name = QTableWidgetItem(product['files'][1])  #14 표지  
                self.t1_table.setItem(count,14,item_name) 
                self.t1_table.hideColumn(14)
                count=count+1
                book_cnt=book_cnt+product['workcount']
        
        # 체크 박스 생성 (x,0)Start
        self.checkBoxList = []        
        for i in range(count):
            ckbox = QCheckBox()
            cellWidget = QWidget()
            self.checkBoxList.append(ckbox)  
            layoutCB = QHBoxLayout(cellWidget)
            layoutCB.addWidget(self.checkBoxList[i])
            layoutCB.setAlignment(QtCore.Qt.AlignCenter)            
            layoutCB.setContentsMargins(0,0,0,0)
            cellWidget.setLayout(layoutCB)     
            self.t1_table.setCellWidget(i,0,cellWidget)

            
        # 고정 컬럼 스크롤, 인덱스 삭제  Strat
        # self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableWidget.verticalHeader().hide()
        #End            


        self.searchResultNum.setText(str(row_count))
        self.searchBookNum.setText(str(book_cnt))
        self.t1_table.resizeColumnToContents(row_count) ##컬럼 넓이 자동정렬   

        # self.tableWidget.resizeColumnToContents(row_count) #합성일자 Fix 컬럼 넓이 자동정렬 


    def Load_xls(self): ##엑셀 운송장 읽기
        global dataset3
        FileOpen = QFileDialog.getOpenFileName(self, 'Open file', '', 'xlsx File(*.xlsx)') #파일
        if FileOpen[0] != '' : # 파일 취소시 예외처리
            self.t2_excelPath.setText(FileOpen[0]) 
            dataset3 = pd.read_excel(FileOpen[0]) 
            
            self.label.setText(str(dataset3))
            #print(dataset3.shape) # (row수, col수) 
            #print(dataset3) # 전체 출력
            #print(FileOpen[0]) # 파일경로
        else :
            print ("파일 확인")                        

    #엑셀 내려받기
    def Xls_export(self, filename=None):
        now = datetime.now()
        now_result = now.strftime("%Y%m%d %H%M%S")

        #order_lists 폴더가 없으면 폴더 생성해줌
        if not os.path.exists(os.getcwd()+"\order_lists"):
            os.makedirs(os.getcwd()+"\order_lists")

        Ex_path= os.getcwd()+"\order_lists\orders_("+ now_result  +").xlsx"     
        
        QmsgBox = QMessageBox(self)
        execel_save = QmsgBox.information(self, '엑셀 저장', Ex_path + ' 저장하시겠습니까?', QmsgBox.Yes | QmsgBox.No)
        if execel_save == QmsgBox.Yes:
           
            columnHeaders = []
            # create column header list
            for j in range(1, 13):
                a=columnHeaders.append(self.t1_table.horizontalHeaderItem(j).text())        

            df = pd.DataFrame(columns=columnHeaders)
            
            # create dataframe object recordset
            for row in range(0,self.t1_table.rowCount()):
                for col in range(0, 12):
                    if col == 11:
                        df.at[row, columnHeaders[col]] = int(self.t1_table.item(row, col+1).text())
                    else:
                        df.at[row, columnHeaders[col]] = self.t1_table.item(row, col+1).text()
                    
            writer = pd.ExcelWriter(Ex_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)

            #셀서식을 숫자로 변경
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format' : '0'})
            worksheet.set_column('L:L', None, format1)
            writer.close()


    def SelectData(self):
        global row_count
        global text
        global tables_data
        book_cnt = 0

        dateFRYMD =self.t1_preDate.text()
        dateTOYMD =self.t1_afterDate.text()

        #API 조회
        url = ORDER_API_BASE_URL + "?mode=5& sdate=" + dateFRYMD + "&edate=" + dateTOYMD
        url_Json = requests.get(url)
        text = url_Json.text                 
        tables_data = json.loads(text)
        row_count=tables_data['total'] #row 행
        self.t1_table.setRowCount(row_count)

        #self.tableWidget.setRowCount(row_count) #컬럼 넓이 자동정렬 table row 결정

        #print(row_count) # row 카운트        
        #print(tables_data['response']) # 응답변수 100:성공
        #print(tables_data['reason']) #성공 실패 사유
        #print(tables_data['total']) #주문수
        #print ("--------------------")

        # 체크 박스 생성 (x,0)Start
        self.checkBoxList = []        
        for i in range(row_count):
            ckbox = QCheckBox()
            cellWidget = QWidget()
            self.checkBoxList.append(ckbox)  
            layoutCB = QHBoxLayout(cellWidget)
            layoutCB.addWidget(self.checkBoxList[i])
            layoutCB.setAlignment(QtCore.Qt.AlignCenter)            
            layoutCB.setContentsMargins(0,0,0,0)
            cellWidget.setLayout(layoutCB)     
            self.t1_table.setCellWidget(i,0,cellWidget)
        # End    
        
        self.searchResultNum.setText(str(row_count))    
        count=0

        # 고정 컬럼 스크롤, 인덱스 삭제  Strat
        # self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.tableWidget.verticalHeader().hide()
        #End


        for author in tables_data['data']:           
            for product in author['product']:

                #0 체크박스
                #1 합성일 pdf_date
                #2 주문일 'order_date': 
                #3 발송일  deli_date
                #4 주문번호 'order_id': 
                #5 상품번호 'product':  ->'product_id': : 
                #6 주문자 'name': 
                #7 연락처 'phone': 
                #8 주소  'addr': 
                #9 상품명 'product':  ->  'p_name':  
                #10 송장번호 deli_no
                #11 택배코드 deli_com
                #12 권수 'product': -> 'workcount':
                #13 내지
                #14 표지      
                
                item_name = QTableWidgetItem(author['pdf_date'])  #1 합성일 pdf_date
                self.t1_table.setItem(count,1,item_name)  

                item_name1 = QTableWidgetItem(author['pdf_date'])  #1 합성일 pdf_date
                # self.tableWidget.setItem(count,0,item_name1)  # 컬럼 넓이 자동정렬  고정컬럼

                item_name = QTableWidgetItem(author['order_date'])  #2 주문일 'order_date': 
                self.t1_table.setItem(count,2,item_name)  
                item_name = QTableWidgetItem(author['deli_date'])  #3 발송일  deli_date
                self.t1_table.setItem(count,3,item_name)  
                item_name = QTableWidgetItem(author['order_id'])  #4 주문번호 'order_id': 
                self.t1_table.setItem(count,4,item_name)  
                item_name = QTableWidgetItem(product['product_id'])   #5 상품번호 'product':  ->'product_id': : 
                self.t1_table.setItem(count,5,item_name)  
                item_name = QTableWidgetItem(author['name'])  #6 주문자 'name': 
                self.t1_table.setItem(count,6,item_name)                      
                item_name = QTableWidgetItem(author['phone'])  #7 연락처 'phone': 
                self.t1_table.setItem(count,7,item_name)  
                item_name = QTableWidgetItem(author['addr']) #8 주소  'addr': 
                self.t1_table.setItem(count,8,item_name)  
                item_name = QTableWidgetItem(product['p_name'])  #9 상품명 'product':  ->  'p_name':  
                self.t1_table.setItem(count,9,item_name)  
                item_name = QTableWidgetItem(author['deli_no'])  #10 송장번호 deli_no
                self.t1_table.setItem(count,10,item_name) 
                if author['state'] == 3:
                    item_name = QTableWidgetItem(author['deli_com'])  #11 택배코드 deli_com
                    if (author['deli_com'] == '0') :
                        item_name = QTableWidgetItem('직접배송')
                    if (author['deli_com'] == '1') :
                        item_name = QTableWidgetItem('대한통운')
                    if (author['deli_com'] == '2') :
                        item_name = QTableWidgetItem('하나로택배')    
                    if (author['deli_com'] == '3') :
                        item_name = QTableWidgetItem('아주택배') 
                    if (author['deli_com'] == '4') :
                        item_name = QTableWidgetItem('한진택배') 
                    if (author['deli_com'] == '5') :
                        item_name = QTableWidgetItem('CJ택배') 
                    if (author['deli_com'] == '6') :
                        item_name = QTableWidgetItem('우체국택배')     
                    if (author['deli_com'] == '7') :
                        item_name = QTableWidgetItem('로젠택배') 
                    if (author['deli_com'] == '8') :
                        item_name = QTableWidgetItem('용마로지스') 
                    if (author['deli_com'] == '9') :
                        item_name = QTableWidgetItem('현대택배') 
                    if (author['deli_com'] == '10') :
                        item_name = QTableWidgetItem('옐로우캡') 
                    if (author['deli_com'] == '11') :
                        item_name = QTableWidgetItem('KGB택배') 
                    if (author['deli_com'] == '12') :
                        item_name = QTableWidgetItem('동부택배')     
                    if (author['deli_com'] == '13') :
                        item_name = QTableWidgetItem('KG로지스')
                else:
                    item_name = QTableWidgetItem('')
                self.t1_table.setItem(count,11,item_name) 
                item_name = QTableWidgetItem(str(product['workcount']))  #12 권수 'product': -> 'workcount':  
                self.t1_table.setItem(count,12,item_name) 
                item_name = QTableWidgetItem(product['files'][0])  #13 내지
                self.t1_table.setItem(count,13,item_name)  
                self.t1_table.hideColumn(13)
                item_name = QTableWidgetItem(product['files'][1])  #14 표지
                self.t1_table.setItem(count,14,item_name)
                self.t1_table.hideColumn(14)
        

                self.t1_table.resizeColumnToContents(count) ##컬럼 넓이 자동정렬                   
                self.t1_table.setColumnWidth(8,120) ## 주소1 컬럼FIX
                               
               # self.tableWidget.resizeColumnToContents(row_count) # 합성일 Fix 컬럼 고정컬럼 넓이 자동정렬  

                
                
                self.t1_table.resizeColumnToContents(count) ##컬럼 넓이 자동정렬  
                self.t1_table.setColumnWidth(3,self.t1_table.columnWidth(1)) ## 발송일 컬럼FIX   
                self.t1_table.setColumnWidth(8,self.t1_table.columnWidth(7)) ## 주소1 컬럼FIX   
                self.t1_table.setColumnWidth(10,self.t1_table.columnWidth(7)) ## 송장 컬럼FIX
               

                count=count+1
                book_cnt=book_cnt+product['workcount']
            
        self.searchBookNum.setText(str(book_cnt))     
    
    def pdfDown(self):

        ckdRow = 0
        product_id = [] # 상품번호 5
        workcount = []  # 권수 12
        content = []    # 내지 13
        cover = []      # 표지 14
        
        if self.t1_pdfCombo.currentText() == '선택':
            for i in range(row_count):
                if self.checkBoxList[i].isChecked():
                    product_id.append(self.t1_table.item(i,5).text())
                    workcount.append(self.t1_table.item(i,12).text())
                    content.append(self.t1_table.item(i,13).text())
                    cover.append(self.t1_table.item(i,14).text())
                    ckdRow += 1
        elif self.t1_pdfCombo.currentText() == '전체':
            for i in range(row_count):
                product_id.append(self.t1_table.item(i,5).text())
                workcount.append(self.t1_table.item(i,12).text())
                content.append(self.t1_table.item(i,13).text())
                cover.append(self.t1_table.item(i,14).text())
                ckdRow += 1

        if ckdRow == 0:
            QmsgBox = QMessageBox(self)
            QmsgBox.raise_()
            QmsgBox.information(self, '알림', '선택된 값이 없습니다.')
        else:
            self.downDialog = download.DownDialog(ckdRow, product_id, workcount, content, cover)
            self.downDialog.show()
    
    def cfg(self):
        self.cfgDialog = config.ConfigDialog()
        self.cfgDialog.show()

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
