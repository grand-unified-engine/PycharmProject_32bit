import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *

import logging
import logging.handlers
from datetime import datetime

form_class = uic.loadUiType("KiwoomConditionTrading.ui")[0]  # ui 파일을 로드하여 form_class 생성


class MyWindow(QMainWindow, form_class):  # MyWindow 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self):  # MyWindow 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출
        self.setupUi(self)  # ui 파일 화면 출력

        global globalPrice  # 전체에서 투입금을 사용하기 위해 global로 선언을 해줌(전역변수)
        globalPrice = '0'  # 투입금에 0을 셋팅해줌

        global logger  # 전체에서 로그를 사용하기 위해 global로 선언을 해줌(전역 변수)
        logger = logging.getLogger('KiwoomConditionTradingLogger')  # 로그 인스턴스를 만든다
        self.set_logger()  # 로그 인스턴스 환경 설정을 셋팅함

        self.kiwoom = QAxWidget(
            "KHOPENAPI.KHOpenAPICtrl.1")  # 키움증권 Open API+의 ProgID를 사용하여 생성된 QAxWidget을 Kiwoom 변수에 할당

        self.btnStart.setDisabled(True)  # 거래시작 버튼을 비활성화 상태로 변경
        self.btnStop.setDisabled(True)  # 거래중지 버튼을 비활성화 상태로 변경
        self.btnReStart.setDisabled(True)  # 재시작 버튼을 비활성화 상태로 변경
        self.lePrice.setDisabled(True)  # 투입금 입력란을 비활성화 상태로 변경
        self.cbAcctNo.setDisabled(True)  # 계좌번호 선택란을 비활성화 상태로 변경
        self.leD2Price.setDisabled(True)  # D2예수금 입력란을 비활성화 상태로 변경
        self.cbCdtNm.setDisabled(True)  # 조건검색명 선택란을 비활성화 상태로 변경
        self.leTotalPrice.setDisabled(True)  # 총투입금 입력란을 비활성화 상태로 변경
        self.leProfits.setDisabled(True)  # 수익금 입력란을 비활성화 상태로 변경
        self.leProfitsPc.setDisabled(True)  # 수익률 입력란을 비활성화 상태로 변경
        self.pteBuyLog.setDisabled(True)  # 매도 종목 노출란을 비활성화 상태로 변경
        self.pteSellLog.setDisabled(True)  # 매수 종목 노출란을 비활성화 상태로 변경
        self.pteLog.setDisabled(True)  # 전체 내역 노출란을 비활성화 상태로 변경

        self.btnLogin.clicked.connect(
            self.btn_login)  # ui 파일을 생성할때 작성한 로그인 버튼의 objectName 으로 클릭 이벤트가 발생할 경우 btn_login 함수를 호출
        self.kiwoom.OnEventConnect.connect(self.event_connect)  # 키움 서버 접속 관련 이벤트가 발생할 경우 event_connect 함수 호출

        self.kiwoom.OnReceiveConditionVer.connect(
            self.receive_condition_var)  # 키움 사용자 조건검색식 수신 관련 이벤트가 발생할 경우 receive_condition_var 함수 호출
        self.kiwoom.OnReceiveTrCondition.connect(
            self.receive_tr_condition)  # 키움 사용자 조건검색식 초기 조회 시 반환되는 값이 있을 경우 receive_tr_condition 함수 호출
        self.kiwoom.OnReceiveRealCondition.connect(
            self.receive_real_condition)  # 키움 사용자 조건검색식 실시간 조회 반환되는 값이 있을 경우 receive_real_condition 함수 호출

        self.kiwoom.OnReceiveMsg.connect(self.on_receive_msg)  # 키움 기타 메시지가 발생할 경우 on_receive_msg 함수 호출

        self.btnStart.clicked.connect(
            self.btn_start)  # ui 파일을 생성할때 작성한 거래시작 버튼의 objectName 으로 클릭 이벤트가 발생할 경우 btn_start 함수를 호출
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)  # 키움 데이터 수신 관련 이벤트가 발생할 경우 receive_trdata 함수 호출

    def set_logger(self):  # 로그 환경을 설정해주는 함수
        fomatter = logging.Formatter(
            '[%(levelname)s|%(lineno)s] %(asctime)s > %(message)s')  # 로그를 남길 방식으로 "[로그레벨|라인번호] 날짜 시간,밀리초 > 메시지" 형식의 포매터를 만든다

        logday = datetime.today().strftime("%Y%m%d")  # 로그 파일 네임에 들어갈 날짜를 만듬 (YYYYmmdd 형태)

        fileMaxByte = 1024 * 1024 * 100  # 파일 최대 용량인 100MB를 변수에 할당 (100MB, 102,400KB)
        fileHandler = logging.handlers.RotatingFileHandler('./log/stock_' + str(logday) + '.log', maxBytes=fileMaxByte,
                                                           backupCount=10)  # 파일에 로그를 출력하는 핸들러 (100MB가 넘으면 최대 10개까지 신규 생성)
        streamHandler = logging.StreamHandler()  # 콘솔에 로그를 출력하는 핸들러

        fileHandler.setFormatter(fomatter)  # 파일에 로그를 출력하는 핸들러에 포매터를 지정
        streamHandler.setFormatter(fomatter)  # 콘솔에 로그를 출력하는 핸들러에 포매터를 지정

        logger.addHandler(fileHandler)  # 로그 인스턴스에 파일에 로그를 출력하는 핸들러를 추가
        logger.addHandler(streamHandler)  # 로그 인스턴스에 콘솔에 로그를 출력하는 핸들러를 추가

        logger.setLevel(logging.DEBUG)  # 로그 레벨을 디버그로 만듬

    def btn_login(self):  # Login 버튼 클릭 시 실행되는 함수
        logger.debug("Login 버튼 클릭")  # debug 레벨 로그를 남김
        ret = self.kiwoom.dynamicCall("CommConnect()")  # 키움 로그인 윈도우를 실행

    def btn_start(self):  # 거래시작 버튼 클릭 시 실행되는 함수
        logger.debug("거래시작 버튼 클릭")  # debug 레벨 로그를 남김
        tempPrice = self.lePrice.text().strip().replace(',', '')  # 입력된 종목당 투입금을 가져옴

        if tempPrice == None or tempPrice == '':  # 투입금이 있는지 체크
            QMessageBox.about(self, "message", "종목당 투입금을 입력해주세요.")  # 투입금이 없다면 안내 얼럿 노출
            return  # 아래 로직을 진행하지 않도록 처리함
        else:
            globalPrice = tempPrice  # 투입금을 전역변수에 셋팅
            logger.debug("투입금(globalPrice): " + str(globalPrice))  # debug 레벨 로그를 남김

        acctNo = self.cbAcctNo.currentText().strip()  # 선택된 계좌번호를 가져옴

        if acctNo == None or acctNo == '':  # 계좌번호가 있는지 체크
            QMessageBox.about(self, "message", "계좌번호를 선택해주세요.")  # 계좌번호가 없다면 안내 얼럿 노출
            return  # 아래 로직을 진행하지 않도록 처리함
        else:
            logger.debug("예수금상세현황요청 시작")  # debug 레벨 로그를 남김
            ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "계좌번호", acctNo)  # 계좌번호 셋팅
            ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "비밀번호", "")  # 비밀번호 셋팅
            ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "비밀번호입력매체구분", "00")  # 비밀번호입력매체구분 셋팅
            ret = self.kiwoom.dynamicCall('SetInputValue(QString, QString)', "조회구분", "1")  # 조회 구분 셋팅
            ret = self.kiwoom.dynamicCall('CommRqData(QString, QString, int, QString)', "opw00001_req", "opw00001", 0,
                                          "0102")  # 키움 dynamicCall 함수를 통해 CommRqData 함수를 호출하여 opw00001 API를 구분명 opw00001_req, 화면번호 0102으로 호출함

    def event_connect(self, err_code):  # 키움 서버 접속 관련 이벤트가 발생할 경우 실행되는 함수
        if err_code == 0:  # err_code가 0이면 로그인 성공 그외 실패
            logger.info("로그인 성공")  # info 레벨 로그를 남김
            self.pteLog.appendPlainText(
                "로그인 성공")  # ui 파일을 생성할때 작성한 plainTextEdit의 objectName 으로 해당 plainTextEdit에 텍스트를 추가함

            account_num = self.kiwoom.dynamicCall("GetLoginInfo(QString)",
                                                  ["ACCNO"])  # 키움 dynamicCall 함수를 통해 GetLoginInfo 함수를 호출하여 계좌번호를 가져옴
            logger.debug("계좌번호: " + account_num.rstrip(';'))  # debug 레벨 로그를 남김
            self.pteLog.appendPlainText("계좌번호: " + account_num.rstrip(
                ';'))  # 키움은 전체 계좌를 반환하며 각 계좌 번호 끝에 세미콜론(;)이 붙어 있음으로 제거하여 plainTextEdit에 텍스트를 추가함

            self.cbAcctNo.addItem(account_num.rstrip(';'))  # 계좌번호 선택 박스에 계좌번호 셋팅

            self.btnStart.setDisabled(False)  # 거래시작 버튼을 활성화 상태로 변경
            self.lePrice.setDisabled(False)  # 투입금 입력란을 활성화 상태로 변경
            self.cbAcctNo.setDisabled(False)  # 계좌번호 선택란을 활성화 상태로 변경
            self.cbCdtNm.setDisabled(False)  # 조건검색명 선택란을 활성화 상태로 변경
            self.pteBuyLog.setDisabled(False)  # 매도 종목 노출란을 활성화 상태로 변경
            self.pteSellLog.setDisabled(False)  # 매수 종목 노출란을 활성화 상태로 변경
            self.pteLog.setDisabled(False)  # 전체 내역 노출란을 활성화 상태로 변경

            self.btnLogin.setDisabled(True)  # 로그인 버튼을 비활성화 상태로 변경

            self.leTotalPrice.setDisabled(True)  # 총투입금 입력란을 비활성화 상태로 변경
            self.leProfits.setDisabled(True)  # 수익금 입력란을 비활성화 상태로 변경
            self.leProfitsPc.setDisabled(True)  # 수익률 입력란을 비활성화 상태로 변경

            self.leTotalPrice.setText('0')  # 총투입금을 0원으로 셋팅
            self.leProfits.setText('0')  # 수익금을 0원으로 셋팅
            self.leProfitsPc.setText('0%')  # 수익률을 0%으로 셋팅

            self.kiwoom.dynamicCall('GetConditionLoad()')  # 키움 서버에 사용자 조건식 목록을 요청

            QMessageBox.about(self, "message", "계좌 비밀번호 입력 및 환경 설정을 진행해주세요.")  # 안내 얼럿 노출
        else:
            logger.info("로그인 실패")  # info 레벨 로그를 남김
            self.pteLog.appendPlainText(
                "로그인 실패")  # ui 파일을 생성할때 작성한 plainTextEdit의 objectName 으로 해당 plainTextEdit에 텍스트를 추가함

    def receive_condition_var(self, bRet, sMsg):  # 사용자 조건검색식 수신 함수
        logger.debug("receive_condition_var bRet: " + str(bRet))  # debug 레벨 로그를 남김
        logger.debug("receive_condition_var sMsg: " + str(sMsg))  # debug 레벨 로그를 남김

        conditionNameList = self.kiwoom.dynamicCall('GetConditionNameList()')  # 수신된 사용자 조건검색식 리스트를 받아옴 (ex. 인덱스^조건명;)
        conditionNameListArray = conditionNameList.rstrip(';').split(';')  # 조건검색식 리스트에 마지막 ";" 기호를 삭제하고 ";" 기호 기준 분리

        logger.info("conditionNameListArray:" + str(conditionNameListArray))  # info 레벨 로그를 남김

        for i in range(0, len(conditionNameListArray)):  # 조건검색식 개수만큼 반복
            self.cbCdtNm.addItem(conditionNameListArray[i])  # 콤보 박스에 조건 셋팅

        index = self.cbCdtNm.findText('000^급등주 찾기')  # 조건검색식 명으로 순번을 찾음
        if index >= 0:  # 해당 순번이 있다면 (해당 조건검색식 명이 있다면)
            self.cbCdtNm.setCurrentIndex(index)  # 해당 순번을 선택 (해당 조검검색식을 선택)

    # sScrNo : 화면번호
    # strCodeList : 종목코드 리스트 (ex:039490;005930;036570;…;)
    # strConditionName: 조건식 이름
    # nIndex: 조건명 인덱스
    # nNext : 연속조회 여부(0:연속조회없음, 2:연속조회 있음)
    def receive_tr_condition(self, sScrNo, strCodeList, strConditionName, nIndex, nNext):  # 조건검색 초기 조회시 반환되는 값을 받는 함수
        logger.info("receive_tr_condition sScrNo: " + str(sScrNo) + ", strCodeList: " + str(
            strCodeList) + ", strConditionName: " + str(strConditionName) + ", nIndex: " + str(
            nIndex) + ", nNext: " + str(nNext))  # info 레벨 로그를 남김

    # strCode : 종목코드
    # strType : 이벤트 종류, "I":종목편입, "D", 종목이탈
    # strConditionName : 조건식 이름
    # strConditionIndex : 조건명 인덱스
    def receive_real_condition(self, strCode, strType, strConditionName,
                               strConditionIndex):  # 조건검색 실시간 조회시 반환되는 값을 받는 함수
        logger.info("receive_real_condition strCode: " + str(strCode) + ", strType: " + str(
            strType) + ", strConditionName: " + str(strConditionName) + ", strConditionIndex: " + str(
            strConditionIndex))  # info 레벨 로그를 남김

        logDateTime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")  # 화면에 노출할 날짜를 만듬 (YYYY-mm-dd HH:MM:SS 형태)
        strCodeName = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [strCode]).strip()  # 종목 코드로 종목 이름을 가져옴

        if str(strType) == "I":  # 편입 종목이라면
            self.pteLog.appendPlainText(
                str(logDateTime) + " 편입 신호 : " + str(strCode) + ", " + str(strCodeName))  # 트레이딩 화면 내역에 로그를 남김
        elif str(strType) == "D":  # 이탈 종목이라면
            self.pteLog.appendPlainText(
                str(logDateTime) + " 이탈 신호 : " + str(strCode) + ", " + str(strCodeName))  # 트레이딩 화면 내역에 로그를 남김

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1,
                       msg2):  # 키움 데이터 수신 함수
        if rqname == "opw00001_req":  # 수신된 데이터 구분명이 opw00001_req 일 경우 (예수금상세현황)
            d2Price = self.kiwoom.dynamicCall('CommGetData(QString, QString, QString, int, QString)', trcode, "",
                                              rqname, 0, "d+2추정예수금")  # d+2추정예수금을 가져옴
            d2Price = self.change_amt_format(d2Price, 0)  # 금액을 천단위 콤마(",")를 추가함
            logger.debug("D2예수금: " + str(d2Price))  # debug 레벨 로그를 남김
            self.leD2Price.setText(str(d2Price))  # 2추정예수금을 D2예수금 입력란에 표기함

            self.btnStop.setDisabled(False)  # 거래중지 버튼을 활성화 상태로 변경
            self.btnStart.setDisabled(True)  # 거래시작 버튼을 비활성화 상태로 변경

            conditionArray = self.cbCdtNm.currentText().strip().split('^')  # 선택한 조건검색명을 가져와서 ^ 기호를 기준 분리
            conditionIndex = conditionArray[0]  # 선택한 조건검색 번호를 가져옴
            conditionName = conditionArray[1]  # 선택한 조검검색 이름을 가져옴

            # 조건검색 종목조회TR송신한다.
            # strScrNo : 화면번호
            # strConditionName : 조건식 이름
            # nIndex : 조건명 인덱스
            # nSearch : 조회구분(0:조건검색, 1:실시간 조건검색)
            # 1:실시간조회의 화면 개수의 최대는 10개
            ret = self.kiwoom.dynamicCall("SendCondition(QString,QString, int, int)", "0156", conditionName,
                                          conditionIndex, 1)  # 선택한 조건검색을 화면번호 0156 실시간 조건검색 타입으로 호출

    def on_receive_msg(self, sScrNo, sRQName, sTrCode, sMsg):  # 키움 기타 메시지 수신 함수
        logger.info(
            "OnReceiveMsg sScrNo: " + sScrNo + ", sRQName: " + sRQName + ", sTrCode: " + sTrCode + ", sMsg: " + sMsg)  # info 레벨 로그를 남김

    def change_amt_format(self, data, percent):  # 금액을 천단위 콤마(",")를 추가하여 반환하는 함수
        is_minus = False  # 마이너스 표기를 거짓으로 지정
        if data.startswith('-'):  # 입력된 금액의 앞자리가 - 일 경우
            is_minus = True  # 마이너스 표기를 참으로 지정
        strip_str = data.lstrip('-0')  # 입력된 금액의 앞자리에 - 기호나 0을 삭제하여 반환
        if strip_str == '':  # 입력된 금액이 공백이라면
            if percent == 1:  # 퍼센트 구분 기호가 1이라면
                return '0.00'  # 0.00 으로 반환
            else:  # 퍼센트 구분 기호가 1이 아니라면
                return '0'  # 0 으로 반환
        if percent == 1:  # 퍼센트 구분 기호가 1이라면
            strip_data = int(strip_str)  # 입력값을 int로 변환 후
            strip_data = strip_data / 100  # 100으로 나눠주고
            form = format(strip_data, ',.2f')  # 소수점 2자리까지 자름
        elif percent == 2:  # 퍼센트 구분 기호가 2이라면
            strip_data = float(strip_str)  # 입력값을 float로 변환 후
            form = format(strip_data, ',.2f')  # 소수점 2자리까지 자름
        else:  # 퍼센트 구분 기호가 1 또는 2가 아니라면
            strip_data = int(strip_str)  # 입력값을 int로 변환 후
            form = format(strip_data, ',d')  # 정수형으로 만듬
        if form.startswith('.'):  # 변환된 금액의 앞자리가 . 으로 시작한다면
            form = '0' + form  # 변환된 금액에 앞에 0을 붙여줌
        if is_minus:  # 입력된 금액이 마이너스 였다면
            form = '-' + form  # 변환된 금액에 앞에 - 기호를 붙여줌
        return form  # 변환됨 금액을 반환함


# py 파일 실행시 제일 먼저 동작
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()  # MyWindow 클래스를 생성하여 myWondow 변수에 할당
    myWindow.show()  # MyWindow 클래스를 노출
    app.exec_()  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기