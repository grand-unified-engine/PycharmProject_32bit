import sys
import os
import pandas as pd

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from errorCode import *
from kiwoomException import *
from kiwoomType import *
from log_class import *

TR_REQ_TIME_INTERVAL = 0.2

# slot 함수 앞에 _를 붙인다.

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        self.realType = RealType()
        # self.logging = Logging()
        #
        # self.logging.logger.debug("Kiwoom() class start.")

        ########## 계좌 관련된 변수
        # self.account_stock_dict = {}  # 보유한 종목
        # self.non_account_stock_dict = {}  # 미체결 종목
        # self.account_num = None #계좌번호 담아줄 변수
        # self.deposit = 0 #예수금
        # self.use_money = 0 #실제 투자에 사용할 금액
        # self.use_money_percent = 0.5 #예수금에서 실제 사용할 비율
        # self.output_deposit = 0 #출력가능 금액
        # self.total_eval_profit_loss_price = 0 #총평가손익금액
        # self.total_earning_rate = 0.0 #총수익률(%)
        #######################################################

        ########## 실시간 종목
        # self.portfolio_stock_dict = []
        ####################################
        
        ########## 포트폴리오 종목
        # self.jango_dict = {}
        ####################################

        ########### 전체 종목 관리
        # self.all_stock_dict = {}
        ###########################

        ########## 종목 분석 용
        # self.calcul_data = []
        #######################################################

        ########## 요청 스크린 번호
        self.screen_my_info = "2000" #계좌 관련 스크린 번호
        # self.screen_calculation_stock = "4000"  # 계산용 스크린 번호
        # self.screen_real_stock = "5000" #지정한 항목의 실시간 정보용 스크린 번호
        # self.screen_meme_stock = "6000" #주문용 스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린 번호
        #######################################################

        ########## 초기 셋팅 함수들
        self.get_ocx_instance()
        self.set_event_loop()
        self.set_signal_slots() #키움과 연결하기 위한 시그널 / 슬롯
        # self.real_event_slot()  # 실시간 이벤트 시그널 / 슬롯 연결
        self.comm_connect()
        # self.account_num = self.get_login_info("ACCNO").strip(';')
        # print("계좌번호 : %s" % self.account_num)

        # self.detail_account_info() #예수금 요청 시그널
        # self.detail_account_mystock() #계좌평가잔고내역 시그널
        # Qtimer.singleShot(5000, self.not_concluded_account) #실시간미체결요청 시그널(미완성)
        # self.calculator_fnc() #종목 골라서 텍스트파일에 저장
        # self.condition_event_slot()
        # self.condition_signal()
        #######################################################

        # QTest.qWait(10000)
        # self.read_code() #텍스트 파일에 저장된 종목 불러오기
        # self.screen_number_setting()
        #
        QTest.qWait(5000)
        #
        # # 실시간 수신 관련 함수
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',
                         self.realType.REALTYPE['장시작시간']['장운영구분'], "0")
        #
        # for code in self.portfolio_stock_dict.keys():
        #     screen_num = self.portfolio_stock_dict[code]['스크린번호']
        #     fids = self.realType.REALTYPE['주식체결']['체결시간']
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")    # 레지스트리에 저장된 api 모듈 불러오기

    def set_event_loop(self):
        # 비동기 방식으로 동작되는 이벤트를 동기화(순서대로 동작) 시킬 때
        self.login_event_loop = None
        # self.tr_event_loop = QEventLoop()
        # self.calculator_event_loop = QEventLoop()
        # self.order_loop = None
        # self.condition_event_loop = None

    def set_signal_slots(self):
        self.OnEventConnect.connect(
            self._connect_slot) # 키움 서버 접속 관련 이벤트가 발생할 경우 _connect_slot 함수 호출
        # self.OnReceiveTrData.connect(
        #     self._tr_data_slot) # 조회요청 응답을 받거나 조회데이터를 수신했을때 호출
        # self.OnReceiveRealData.connect(
        #     self._receive_real_data)  # 실시간 데이터 수신할때마다 호출 (내가 만든 것)
        self.OnReceiveRealData.connect(
            self._receive_real_data2)  # 실시간 데이터 수신할때마다 호출 (손가락 하나 까딱)
        # self.OnReceiveChejanData.connect(
        #     self._receive_chejan_data) # 체결
        # self.OnReceiveChejanData.connect(
        #     self._receive_chejan_data2) # 체결 (손가락 하나 까딱)
        # self.OnReceiveMsg.connect(self._msg_slot) # 서버에서 메시지 받기

        # self.OnReceiveConditionVer.connect(
        #     self._receive_condition_var)  # 조건검색식 수신 관련 이벤트가 발생할 경우
        # self.OnReceiveTrCondition.connect(
        #     self._receive_tr_condition) # (조건검색식 초기) 조회 시 반환되는 값이 있을 경우
        # self.OnReceiveRealCondition.connect(
        #     self._receive_real_condition)  # (조건검색식 실시간) 조회 반환되는 값이 있을 경우

    #조건검색식 이벤트 모음
    def condition_event_slot(self):
        self.OnReceiveConditionVer.connect(self.condition_slot)
        self.OnReceiveTrCondition.connect(self.condition_tr_slot)
        # self.OnReceiveRealCondition.connect(self.condition_real_slot)





    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    ###############################################################
    # 슬롯 정의                                                   #
    ###############################################################
    # 키움 서버 접속 관련 이벤트
    def _connect_slot(self, err_code):

        print(errors(err_code)[1])
        # server = Kiwoom.getServerGubun()
        # if len(server) == 0 or server != "1":
        #     print("실서버입니다")
        # else:
        #     print("모의투자 서버입니다.")

        # if err_code == 0:
        #     print("connected")
        #
        #     # self.server = self.getLoginInfo("GetServerGubun", True)
        #     #
        #     # if len(self.server) == 0 or self.server != "1":
        #     #     self.msg += "실서버 연결 성공" + "\r\n\r\n"
        #     #
        #     # else:
        #     #     self.msg += "모의투자서버 연결 성공" + "\r\n\r\n"
        # else:
        #     print("disconnected")
        self.login_event_loop.exit()

    # 실시간 slot
    def _receive_real_data2(self, sCode, sRealType, sRealData):
        print("sRealType : %s" % sRealType)
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분'] # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            print("fid : %s" % fid)
            print("value : %s" % value)

            if value == '0':
                print("장 시작 전")

            elif value == '3':
                print("장 시작")

            elif value == "2":
                print("장 종료, 동시호가로 넘어감")

            elif value == "4":
                print("3시30분 장 종료")

                # for code in self.portfolio_stock_dict.keys():
                #     self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code) # 연결 끊기
                #
                # QTest.qWait(5000)
                #
                # self.file_delete()
                # self.calculator_fnc()
                #
                # sys.exit()

        # elif sRealType == "주식체결":
        #     a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간']) # 출력 HHMMSS
        #     b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
        #     b = abs(int(b))
        #
        #     c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비']) # 출력 : +(-)2520
        #     c = abs(int(c))
        #
        #     d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율']) # 출력 : +(-)12.98
        #     d = float(d)
        #
        #     e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가']) # 출력 : +(-)2520
        #     e = abs(int(e))
        #
        #     f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가']) # 출력 : +(-)2515
        #     f = abs(int(f))
        #
        #     g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량']) # 출력 : +240124 매수일때, -2034 매도일 때, (체결 거래량)
        #     g = abs(int(g))
        #
        #     h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량']) # 출력 : 240124 (당일 거래된 총 체결 거래량)
        #     h = abs(int(h))
        #
        #     i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가']) # 출력 : +(-)2530
        #     i = abs(int(i))
        #
        #     j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가']) # 출력 : +(-)2530
        #     j = abs(int(j))
        #
        #     k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가']) # 출력 : +(-)2530
        #     k = abs(int(k))
        #
        #     if sCode not in self.portfolio_stock_dict:
        #         self.portfolio_stock_dict.update({sCode:{}})
        #
        #     self.portfolio_stock_dict[sCode].update({"체결시간": a})
        #     self.portfolio_stock_dict[sCode].update({"현재가": b})
        #     self.portfolio_stock_dict[sCode].update({"전일대비": c})
        #     self.portfolio_stock_dict[sCode].update({"등락율": d})
        #     self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
        #     self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
        #     self.portfolio_stock_dict[sCode].update({"거래량": g})
        #     self.portfolio_stock_dict[sCode].update({"누적거래량": h})
        #     self.portfolio_stock_dict[sCode].update({"고가": i})
        #     self.portfolio_stock_dict[sCode].update({"시가": j})
        #     self.portfolio_stock_dict[sCode].update({"저가": k})
        #
        #     if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
        #         asd = self.account_stock_dict[sCode]
        #         meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
        #
        #         if asd['매매가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
        #             order_success = self.dynamicCall(
        #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #                 ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
        #             )
        #
        #             if order_success == 0:
        #                 print("매도주문 전달 성공")
        #                 del self.account_stock_dict[sCode]
        #             else:
        #                 print("매도주문 전달 실패")
        #
        #     elif sCode in self.jango_dict.keys():
        #         jd = self.jango_dict[sCode]
        #         meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100
        #
        #         if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
        #             order_success = self.dynamicCall(
        #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #                 ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
        #             )
        #
        #             if order_success == 0:
        #                 print("매도주문 전달 성공")
        #             else:
        #                 print("매도주문 전달 실패")
        #
        #     elif d > 2.0 and sCode not in self.jango_dict:
        #         print("매수조건 통과 %s " % sCode)
        #
        #         result = (self.use_money * 0.1) / e
        #         quantity = int(result)
        #
        #         order_success = self.dynamicCall(
        #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #             ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ""]
        #         )
        #
        #         if order_success == 0:
        #             print("매수주문 전달 성공")
        #         else:
        #             print("매수주문 전달 실패")
        #
        #     not_meme_list = list(self.not_account_stock_dict)
        #     for order_num in not_meme_list:
        #         code = self.not_account_stock_dict[order_num]["종목코드"]
        #         meme_price = self.not_account_stock_dict[order_num]['주문가격']
        #         not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
        #         order_gubun = self.not_account_stock_dict[order_num]['주문구분']
        #
        #         if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
        #             order_success = self.dynamicCall(
        #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #                 ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num]
        #             )
        #
        #             if order_success == 0:
        #                 print("매수취소 전달 성공")
        #             else:
        #                 print("매수취소 전달 실패")
        #
        #         elif not_quantity == 0:
        #             del self.not_account_stock_dict[order_num]


    # 조회요청 응답을 받거나 조회데이터를 수신했을때
    def _tr_data_slot(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):

        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        # rqname은 요청한 이름 그대로 return 된다.
        if rqname == "opt10004_req": # opt10004 : 주식호가요청 (multi)
            self._opt10004(rqname, trcode)
        elif rqname == "opt10007_req": # opt10007 : 시세표성정보요청 (single인데)
            self._opt10007(rqname, trcode)
        elif rqname == "opt10016_req": # OPT10016 : 신고저가요청 (multi)
            self._opt10016(rqname, trcode)
        elif rqname == "opt10080_req": # opt10080 : 주식분봉차트조회요청 (single, multi)
            self._opt10080(rqname, trcode)
        elif rqname == "opt10081_req": # opt10081 : 주식일봉차트조회요청
            self._opt10081(rqname, trcode)
        elif rqname == "opt10082_req": # opt10082 : 주식주봉차트조회요청
            self._opt10082(rqname, trcode)
        elif rqname == "예수금상세현황요청": # opw00001 : 예수금상세현황요청 (single, multi)
            deposit = self._comm_get_data(trcode, "", rqname, 0, "d+2추정예수금")
            self.deposit = int(deposit)
            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4
            output_deposit = self._comm_get_data(trcode, "", rqname, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)
            print("예수금 : %s" % self.output_deposit)
            self._stop_screen_cancel(self.screen_my_info)
            self.tr_event_loop.exit()

        elif rqname == "계좌평가잔고내역요청": # opw00018 : 계좌평가잔고내역요청
            # single data(계좌평가결과)
            total_purchase_price = self._comm_get_data(trcode, "", rqname, 0, "총매입금액")
            self.total_purchase_price = int(total_purchase_price)
            # total_eval_price = self._comm_get_data(trcode, "", rqname, 0, "총평가금액")
            total_eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, 0, "총평가손익금액")
            self.total_eval_profit_loss_price = int(total_eval_profit_loss_price)
            total_earning_rate = self._comm_get_data(trcode, "", rqname, 0, "총수익률(%)")
            self.total_earning_rate = float(total_earning_rate)
            # estimated_deposit = self._comm_get_data(trcode, "", rqname, 0, "추정예탁자산")

            print("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (total_purchase_price, total_eval_profit_loss_price, total_earning_rate))

            # total_earning_rate = self.change_format(total_earning_rate)
            #
            # if self.get_server_gubun():
            #     total_earning_rate = float(total_earning_rate) / 100
            #     total_earning_rate = str(total_earning_rate)
            #
            # self.opw00018_output['single'].append(self.change_format(total_purchase_price))
            # self.opw00018_output['single'].append(self.change_format(total_eval_price))
            # self.opw00018_output['single'].append(self.change_format(total_eval_profit_loss_price))
            # self.opw00018_output['single'].append(total_earning_rate)
            # self.opw00018_output['single'].append(self.change_format(estimated_deposit))

            # keyList = ["총매입금액", "총평가금액", "총평가손익금액", "총수익률(%)", "추정예탁자산"]
            #
            # for key in keyList:
            #     value = self._comm_get_data(trcode, "", rqname, 0, key)
            #
            #     if key.startswith("총수익률"):
            #         value = self.changeFormat(value, 1)
            #     else:
            #         value = self.changeFormat(value)
            #
            #     self.opw00018_output['single'].append(value)

            # multi data(계좌평가잔고개별합산)
            cnt = self._get_repeat_cnt(trcode, rqname)
            for i in range(cnt):
                itemcode = self._comm_get_data(trcode, "", rqname, i, "종목번호")
                itemcode = itemcode.strip()[1:]
                # itemcode = itemcode.strip('A')
                name = self._comm_get_data(trcode, "", rqname, i, "종목명")
                quantity = self._comm_get_data(trcode, "", rqname, i, "보유수량")
                purchase_price = self._comm_get_data(trcode, "", rqname, i, "매입가") #종목별로 매입한 평균가
                current_price = self._comm_get_data(trcode, "", rqname, i, "현재가")
                eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, i, "평가손익")
                earning_rate = self._comm_get_data(trcode, "", rqname, i, "수익률(%)")
                total_chegual_price = self._comm_get_data(trcode, "", rqname, i, "매입금액") #종목별 매입한 총 매수금액
                possible_quantity = self._comm_get_data(trcode, "", rqname, i, "매매가능수량") #종목별로 현재 매도할 수 있는 수량

                print("종목번호 : %s - 종목명 : %s - 보유수량 : %s - 매입가 : %s - 수익률 : %s - 현재가 : %s" % (itemcode, name, quantity, purchase_price, earning_rate, current_price))

                if itemcode in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict[itemcode] = {}

                quantity = self.change_format(quantity)
                purchase_price = self.change_format(purchase_price)
                current_price = self.change_format(current_price)
                # eval_profit_loss_price = self.change_format(eval_profit_loss_price)
                earning_rate = self.change_format2(earning_rate)
                total_chegual_price = self.change_format(total_chegual_price)
                possible_quantity = self.change_format(possible_quantity)

                self.account_stock_dict[itemcode].update({"종목명": name})
                self.account_stock_dict[itemcode].update({"보유수량": quantity})
                self.account_stock_dict[itemcode].update({"매입가": purchase_price})
                self.account_stock_dict[itemcode].update({"수익률(%)": earning_rate})
                self.account_stock_dict[itemcode].update({"현재가": current_price})
                self.account_stock_dict[itemcode].update({"매입금액": total_chegual_price})
                self.account_stock_dict[itemcode].update({"매매가능수량": possible_quantity})


            #
            #     self.opw00018_output['multi'].append([itemcode, name, quantity, purchase_price, current_price,
            #                                           eval_profit_loss_price, earning_rate])

            if next == "2":
                # detail_account_mystock에 있는 self.detail_account_mystock_event_loop = QEventLoop를 전역변수로 옮기고 detail_account_mystock에서는 이벤트 루프만 실행하게 해준다.
                self.detail_account_mystock(sPrevNext="2")
            else:
                self._stop_screen_cancel(self.screen_my_info)
                self.tr_event_loop.exit()

        elif rqname == "실시간미체결요청":  #  : 실시간미체결요청
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

            for i in range(rows):
                # code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                #
                # code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                # order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                # order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태") # 접수,확인,체결
                # order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                # order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                # order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분") # -매도, +매수, -매도정정, +매수정정
                # not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                # ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                print("미체결 종목 : %s " % self.not_account_stock_dict[order_no])

            self.tr_event_loop.exit()

        elif rqname == "주식일봉차트조회": # opt10081 : 주식일봉차트조회
            # self._opt10081(rqname, trcode)
            code = self._comm_get_data(trcode, "", rqname, 0, "종목코드")
            code = code.strip()
            # data = self.get_comm_data_ex(trcode, rqname)

            cnt = self._get_repeat_cnt(trcode, rqname)
            print("남은 일자 수 : %s" % cnt)
            for i in range(cnt):
                data = []
                close = self._comm_get_data(trcode, "", rqname, i, "현재가")
                volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
                tr_volume = self._comm_get_data(trcode, "", rqname, i, "거래대금")
                date = self._comm_get_data(trcode, "", rqname, i, "일자")
                open = self._comm_get_data(trcode, "", rqname, i, "시가")
                high = self._comm_get_data(trcode, "", rqname, i, "고가")
                low = self._comm_get_data(trcode, "", rqname, i, "저가")

                data.append("")
                data.append(close.strip())
                data.append(volume.strip())
                data.append(tr_volume.strip())
                data.append(date.strip())
                data.append(open.strip())
                data.append(high.strip())
                data.append(low.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            if next == "2":
                self.day_kiwoom_db(code=code, sPrevNext=next)
            else:
                print("총 일수 %s" % len(self.calcul_data))
                pass_success = False

                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    # 120 이평선의 최근 가격을 구함
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘의 주가가 120 이평선에 걸쳐있는지 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    # 과거 일봉 데이터를 조회하면서 120 이평선보다 주가가 계속 밑에 존재하는지 확인
                    prev_price = None
                    if bottom_stock_price == True:
                        moving_average_price=0
                        price_top_moving = False
                        idx = 1

                        while True:
                            if len(self.calcul_data[idx:]) < 120: #120치가 있는지 확인
                                print("120일 치가 없음")
                                break

                            total_price=0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                print("20일 동안 주가가 120 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20: #120 이평선 위에 있는 구간 존재
                                print("120일치 이평선 위에 있는 구간 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
                                print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인")
                                pass_success = True

                if pass_success == True:
                    print("조건부 통과됨")
                    code_nm = self.kiwoom.get_master_code_name(code)
                    f = open("files/condition_stock.txt", "a", encoding="utf8") #a는 기존 파일에 이어 쓰기, w는 이전 데이터를 모두 지우고 새로 쓰기
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()
                elif pass_success == False:
                    print("조건부 통과 못 함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()


        # try:
        #     self.tr_event_loop.exit()
        # except AttributeError:
        #     pass

    def _opt10004(self, rqname, trcode):  # opt10004 : 주식호가요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        print(data_cnt)

        for i in range(data_cnt):
            bal_sell = self._comm_get_data(trcode, "", rqname, i, "총매도잔량")
            bal_buy = self._comm_get_data(trcode, "", rqname, i, "총매수잔량")

        print("총매도잔량: ", bal_sell, bal_buy)

    def _opt10007(self, rqname, trcode):  # opt10007 : 시세표성정보요청 (multi)
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        print(data_cnt)

        for i in range(data_cnt):
            bal_sell = self._comm_get_data(trcode, "", rqname, i, "총매도잔량")
            bal_buy = self._comm_get_data(trcode, "", rqname, i, "총매수잔량")

        print("총매도잔량: ", bal_sell, bal_buy)

    def _opt10016(self, rqname, trcode):  # OPT10016 : 신고저가요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        print(data_cnt)

        for i in range(data_cnt):
            bal_sell = self._comm_get_data(trcode, "", rqname, i, "총매도잔량")
            bal_buy = self._comm_get_data(trcode, "", rqname, i, "총매수잔량")

        # print("총매도잔량: ", bal_sell, bal_buy)

    def _opt10080(self, rqname, trcode):  # opt10080 : 주식분봉차트조회요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            tradetime = self._comm_get_data(trcode, "", rqname, i, "체결시간")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            if tradetime[0:8] == '20200429':
                self.ohlcv['tradetime'].append(tradetime)
                self.ohlcv['open'].append(int(open))
                self.ohlcv['high'].append(int(high))
                self.ohlcv['low'].append(int(low))
                self.ohlcv['close'].append(int(close))
                self.ohlcv['volume'].append(int(volume))

    def _opt10081(self, rqname, trcode):  # opt10081 : 주식일봉차트조회요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

        self._stop_screen_cancel(self.screen_my_info)
        self.tr_event_loop.exit()

    def _opt10082(self, rqname, trcode):  # opt10082 : 주식주봉차트조회요청
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

        self._stop_screen_cancel(self.screen_my_info)
        self.tr_event_loop.exit()

    # 주문이 들어가면 결과 데이터를 반환하는 함수
    def _receive_chejan_data2(self, sGubun, nItemCnt, sFidList):
        if int(sGubun) == 0: #주문체결
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호']) # 출력 : defaluse : "000000"
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호']) # 출럭: 0115061 마지막 주문번호

            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태']) # 출력: 접수, 확인, 체결
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량']) # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격']) # 출력: 21000
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량']) # 출력: 15, default: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분']) # 출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간']) # 출력: '151028'

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']) # 출력: 2110 default : ''
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']) # 출력: 5 default : ''
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가']) # 출력: -6000
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가']) # 출력: -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가']) # 출력: -6000
            first_buy_price = abs(int(first_buy_price))

            ######## 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number: {}})

            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})

        elif int(sGubun) == 1: #잔고
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가']) # 계좌에 있는 종목의 총매입가
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]

    def _msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))
        # tr코드라고 출력된 메시지는 정해진 문자는 아니다. 요청된 데이터에 대한 처리 형태를 보여줄 뿐이다.

    ###############################################################
    # 메서드 정의: 로그인 관련 메서드                               #
    ###############################################################
    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def get_connect_state(self):
        """
        현재 접속상태를 반환합니다.
        반환되는 접속상태는 아래와 같습니다.
        0: 미연결, 1: 연결
        :return: int
        """
        state = self.dynamicCall("GetConnectState()")
        return state

    def get_login_info(self, tag, isConnectState=False):
        """
        사용자의 tag에 해당하는 정보를 반환한다.
        tag에 올 수 있는 값은 아래와 같다.
        ACCOUNT_CNT: 전체 계좌의 개수를 반환한다.
        ACCNO: 전체 계좌 목록을 반환한다. 계좌별 구분은 ;(세미콜론) 이다.
        USER_ID: 사용자 ID를 반환한다.
        USER_NAME: 사용자명을 반환한다.
        GetServerGubun: 접속서버 구분을 반환합니다.("1": 모의투자, 그외(빈 문자열포함): 실서버)
        :param tag: string
        :param isConnectState: bool - 접속상태을 확인할 필요가 없는 경우 True로 설정.
        :return: string
        """

        if not isConnectState:
            if not self.get_connect_state():
                raise KiwoomConnectError()

        if not isinstance(tag, str):
            raise ParameterTypeError()

        if tag not in ['ACCOUNT_CNT', 'ACCNO', 'USER_ID', 'USER_NAME', 'GetServerGubun']:
            raise ParameterValueError()

        if tag == "GetServerGubun":
            info = self.get_server_gubun()
        else:
            cmd = 'GetLoginInfo("%s")' % tag
            info = self.dynamicCall(cmd)

        return info

    def get_server_gubun(self):
        """
        서버구분 정보를 반환한다.
        리턴값이 "1"이면 모의투자 서버이고, 그 외에는 실서버(빈 문자열포함).
        :return: string
        """
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    ###############################################################
    # 메서드 정의: opw00001 : 예수금상세현황요청                    #
    ###############################################################
    def detail_account_info(self, sPrevNext="0"):
        self.set_input_value("계좌번호", self.account_num)
        self.set_input_value("비밀번호", "6285")
        self.set_input_value("비밀번호입력매체구분", "00")
        self.set_input_value("조회구분", "1")
        self.comm_rq_data("예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

        self.tr_event_loop.exec_()
    ###############################################################
    # 메서드 정의: opw00018 : 계좌평가잔고내역요청                  #
    ###############################################################
    def detail_account_mystock(self, sPrevNext="0"):
        self.set_input_value("계좌번호", self.account_num)
        self.set_input_value("비밀번호", "6285")
        self.set_input_value("비밀번호입력매체구분", "00")
        self.set_input_value("조회구분", "1")
        self.comm_rq_data("계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.tr_event_loop.exec_()

    ###############################################################
    # 메서드 정의: opt10075 : 실시간미체결요청                      #
    ###############################################################
    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 종목 요청")
        self.set_input_value("계좌번호", self.account_num)
        self.set_input_value("체결구분", "1")
        self.set_input_value("매매구분", "0")
        self.comm_rq_data("실시간미체결요청", "opt00075", sPrevNext, self.screen_my_info)

        self.tr_event_loop.exec_()

    ###############################################################
    # 메서드 정의: 종목 가져오고 선정함수 호출                      #
    ###############################################################
    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10") #코스닥

        print("코스닥 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) #스크린 연결 끊기

            print("%s / %s KOSDAQ Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)

    ###############################################################
    # 메서드 정의: 저장된 파일에서 코드 읽기                        #
    ###############################################################
    def read_code(self):
        if os.path.exists("files/condition_stock.txt"):

            f = open("files/condition.txt", "r", encoding="uft8")

            lines = f.readlines() #파일에 있는 내용들을 읽는다.
            for line in lines: #줄바꿈 내용 읽기
                if line != "":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = int(ls[2].split("\n")[0])
                    stock_price = abs(stock_price)

                    self.portfolio_stock_dict.update({stock_code: {"종목명": stock_name, "현재가": stock_price}})
            f.close()

    ###############################################################
    # 메서드 정의: 보유한 종목, 미체결 종목, 분석된 종목 합치기      #
    ###############################################################
    def merge_dict(self):
        self.all_stock_dict.update({"계좌평가잔고내역": self.account_stock_dict})
        self.all_stock_dict.update({'미체결종목': self.not_account_stock_dict})
        self.all_stock_dict.update({'포트폴리오종목': self.portfolio_stock_dict})

    ###############################################################
    # 메서드 정의: 스크린번호 세팅                                 #
    ###############################################################
    def screen_number_setting(self):
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

       # 스크린 번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

        print(self.portfolio_stock_dict)

    ###############################################################
    # 메서드 정의: 종목 선정                                       #
    ###############################################################
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.
        # 다음 줄의 코드가 실행되지 않게 막으면서 증권 서버에 요청 중인 이벤트 처리는 유지한다.
        #우리가 원하는 것은 일봉데이터를 요청하는 상황 등에서 다른 코드들은 실행되지 않게 이벤트 루프를 줘야 한다는 것이다.
        #따라서 이벤트 루프가 계속 실행된 상태로 다른 코드들의 실행을 막으면서 시간 간격도 줘야 한다.
        #만약 sleep(초)이나 timer(초) 함수를 사용해서 타이머를 설정하면 이벤트 루프의 동작까지 타이머의 영향을 받게 된다. 그러면 키움에 요청 중이던 프로세스 자체가 중지된다.
        #결국에는 연속조회 도중에 이벤트가 끊겨서 에러가 발생한다.
        #하지만 QTest.qWait는 이전에 키움 서버에 요청한 이벤트와 이벤트 루프의 동작은 계속 작동시키면서 타이머를 준다.
        #그러므로 이벤트 루프가 중단되는 에러를 피하면서 SetInputValue를 재작성하여 안전하게 요청한다.

        self.set_input_value("종목코드", code)
        self.set_input_value("수정주가구분", "1")

        if date != None:
            self.set_input_value("기준일자", date)

        self.comm_rq_data("주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        self.calculator_event_loop.exec_()

    ######################## 실시간 데이터 처리 관련 ########################
    def setRealReg(self, screenNo, codelist, fidlist, optType):
        """
        실시간 데이터 요청 메서드
        종목코드와 fid 리스트를 이용해서 실시간 데이터를 요청하는 메서드입니다.
        한번에 등록 가능한 종목과 fid 갯수는 100종목, 100개의 fid 입니다.
        실시간등록타입을 0으로 설정하면, 등록한 종목들은 실시간 해지되고 등록한 종목만 실시간 시세가 등록
        실시간등록타입을 1로 설정하면, 먼저 등록한 종목들과 함께 실시간 시세가 등록된다.
        실시간 데이터는 실시간 타입 단위로 receiveRealData() 이벤트로 전달되기 때문에,
        이 메서드에서 지정하지 않은 fid 일지라도, 실시간 타입에 포함되어 있다면, 데이터 수신이 가능하다.
        :param screenNo: string
        :param codes: string - 종목코드 리스트(종목코드;종목코드;...)
        :param fids: string - fid 리스트(fid;fid;...)
        :param realRegType: string - 실시간등록타입(0: 첫 등록, 1: 추가 등록)
        """

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                         screenNo, codelist, fidlist, optType)

        # receiveConditionVer() 이벤트 메서드에서 루프 종료
        self.condition_event_loop = QEventLoop()
        self.condition_event_loop.exec_()

    # 실시간 데이터 처리시 이벤트 호출 함수
    def _receive_real_data(self, code, realType, realData):

        # self.real_data = {'close': [], 'power': [], 'sign': [], 'r128': [], 'r138': []}
        try:
            # print("realType: ", realType)

            if realType == '주식체결':
                close = self.dynamicCall("GetCommRealData(QString, int)", code, 10) #현재가
                power = self.dynamicCall("GetCommRealData(QString, int)", code, 228) #체결강도
                sign = self.dynamicCall("GetCommRealData(QString, int)", code, 15) #체결량, 거래량

                # print("코드: ", Kiwoom)
                # print("sign: " , sign)
                # print("int sign: ", int(sign))

                if int(sign) > 10000:
                    print("매수해라 코드, 체결량: ", code, sign)




                # self.real_data['close'].append(int(close))
                # self.real_data['power'].append(int(power))
                # self.real_data['sign'].append(int(sign))
                # self.real_data['r128'].append(int(r128))
                # self.real_data['r138'].append(int(r138))
                #
                # print(self.real_data)

            elif realType == '주식호가잔량':
                r121 = self.dynamicCall("GetCommRealData(QString, int)", code, 121)  # 매도호가총잔량
                r125 = self.dynamicCall("GetCommRealData(QString, int)", code, 125)  # 매수호가총잔량

                print("Kiwoom: ", code)
                name = self.kiwoom.get_master_code_name(code)
                print("name: ", name)

                if r121 < r125:
                    print('팔아 ', code, name)

        except Exception as e:
            print(e)

        self.condition_event_loop.exit()
        # finally:
        #     self.condition_event_loop.exit()


    ######################## 조검검색 관련 ########################
    # 어떤 조건식이 있는지 확인
    def condition_slot(self, lRet, sMsg):
        self.logging.logger.debug("호출 성공 여부 %s, 호출결과 메시지 %s" % (lRet, sMsg))

        # lRet 정상적으로 요청됐으면 1을 반환, 그 외는 모두 실패
        condition_name_list = self.dynamicCall("GetConditionNameList()")
        self.logging.logger.debug("HTS의 조건검색식 이름 가져오기 %s" % condition_name_list)

        condition_name_list = condition_name_list.split(";")[:-1]

        for unit_condition in condition_name_list:
            index = unit_condition.split("^")[0]
            index = int(index)
            condition_name = unit_condition.split("^")[1]

            self.logging.logger.debug("조건식 분리 번호: %s, 이름: %s" % (index, condition_name))

            ok  = self.dynamicCall("SendCondition(QString, QString, int, int)", "0156", condition_name, index, 1) #조회요청 + 실시간 조회, 0이면 조회요청, 1이면 실시간요청
            self.logging.logger.debug("조회 성공여부 %s " % ok)



    # 조건식 로딩 하기
    def condition_signal(self):
        self.dynamicCall("GetConditionLoad()")

    # 나의 조건식에 해당하는 종목코드 받기
    def condition_tr_slot(self, sScrNo, strCodeList, strConditionName, index, nNext):
        self.logging.logger.debug("화면번호: %s, 종목코드 리스트: %s, 조건식 이름: %s, 조건식 인덱스: %s, 연속조회: %s" % (sScrNo, strCodeList, strConditionName, index, nNext))

        code_list = strCodeList.split(";")[:-1]
        self.logging.logger.debug("코드 종목 \n %s" % code_list)

    # 조건식 실시간으로 받기
    def condition_real_slot(self, strCode, strType, strConditionName, strConditionIndex):
        self.logging.logger.debug("종목코드: %s, 이벤트종류: %s, 조건식이름: %s, 조건명인덱스: %s" % (strCode, strType, strConditionName, strConditionIndex))

        if strType == "I":
            self.logging.logger.debug("종목코드: %s, 종목편입: %s" % (strCode, strType))

        elif strType == "D":
            self.logging.logger.debug("종목코드: %s, 종목이탈: %s" % (strCode, strType))





    # 키움 서버에 사용자 조건식 목록을 요청
    def get_condition_load(self):
        isLoad = self.dynamicCall("GetConditionLoad()") # 목록을 다 수신하면 OnReceiveConditionVer() 이벤트를 호출한다.

        if not isLoad:
            raise KiwoomProcessingError("getConditionLoad(): 조건식 요청 실패")

        # receiveConditionVar() 이벤트 메서드에서 루프 종료
        self.condition_event_loop = QEventLoop()
        self.condition_event_loop.exec_()

    def _receive_condition_var(self, bRet, sMsg):  # 사용자 조건검색식 수신 함수
        # print("receive_condition_var bRet: " + str(bRet))  # debug 레벨 로그를 남김
        # print("receive_condition_var sMsg: " + str(sMsg))  # debug 레벨 로그를 남김

        # try:
        # if bRet == '1':
        conditionNameList = self.dynamicCall('GetConditionNameList()')  # 수신된 사용자 조건검색식 리스트를 받아옴 (ex. 인덱스^조건명;)
        # conditionNameListArray = conditionNameList.rstrip(';').split(';')  # 조건검색식 리스트에 마지막 ";" 기호를 삭제하고 ";" 기호 기준 분리

        pairs = [idx_name.split('^') for idx_name in [cond for cond in conditionNameList.split(';')]]

        # print("pairs: ", pairs)

        if len(pairs) > 0:
            for i in range(0, len(pairs)):
                if pairs[i][0] == '007':
                    nIndex = pairs[i][0]
                    strConditionName = pairs[i][1]

        # 조건검색 종목조회TR송신한다.
        # strScrNo : 화면번호
        # strConditionName : 조건식 이름
        # nIndex : 조건명 인덱스
        # nSearch : 조회구분(0:조건검색, 1:실시간 조건검색)
        # 1:실시간조회의 화면 개수의 최대는 10개
        isRequest = self.dynamicCall("SendCondition(QString,QString, int, int)", "0156", strConditionName,
                                      nIndex, 1)  # 선택한 조건검색을 화면번호 0156 실시간 조건검색 타입으로 호출


        # print("isRequest: ", isRequest)
        # finally:
        #     self.condition_event_loop.exit()

    def _receive_tr_condition(self, screen_no, codelist, condition_name, index, next):
        """
        (1회성, 실시간) 종목 조건검색 요청시 발생되는 이벤트
        검색 버튼 눌렀을 때 이벤트
        :param screenNo: string
        :param codes: string - 종목코드 목록(각 종목은 세미콜론으로 구분됨)
        :param conditionName: string - 조건식 이름
        :param conditionIndex: int - 조건식 인덱스
        :param inquiry: int - 조회구분(0: 남은데이터 없음, 2: 남은데이터 있음)
        """

        # print("SendCondition 메소드 이용할 때 호출됨")
        # try:

        self.setRealReg("012345", codelist.rstrip(';'), "10;", "0")


        # codes = [idx_name for idx_name in [cond for cond in codelist.rstrip(';').split(';')]]
        #
        # self.setRealReg("012345", codes, "10;", "0")

        # for i, Kiwoom in enumerate(codes):
            # self.codelistArray['Kiwoom'].append(Kiwoom)


        # finally:
        #     self.condition_event_loop.exit()



    # 조건검색 실시간 조회시 반환되는 값을 받는 함수
    # strCode : 종목코드
    # strType : 이벤트 종류, "I":종목편입, "D", 종목이탈
    # strConditionName : 조건식 이름
    # strConditionIndex : 조건명 인덱스
    def _receive_real_condition(self, strCode, strType, strConditionName,
                               strConditionIndex):
        # logger.info("receive_real_condition strCode: " + str(strCode) + ", strType: " + str(
        #     strType) + ", strConditionName: " + str(strConditionName) + ", strConditionIndex: " + str(
        #     strConditionIndex))  # info 레벨 로그를 남김
        # try:
        print("strCode: ", strCode)
        print("strType: ", strType)
        print("strConditionName: ", strConditionName)
        print("strConditionIndex: ", strConditionIndex)

        logDateTime = datetime.today().strftime("%Y-%m-%d %H:%M:%S")  # 화면에 노출할 날짜를 만듬 (YYYY-mm-dd HH:MM:SS 형태)
        strCodeName = self.dynamicCall("GetMasterCodeName(QString)", [strCode]).strip()  # 종목 코드로 종목 이름을 가져옴

        if str(strType) == "I":  # 편입 종목이라면
            # opt10004 TR 요청, 주식호가요청
            self.set_input_value("종목코드", strCode)
            self.comm_rq_data("opt10004_req", "opt10004", 0, "0101")
            print(str(logDateTime) + " 편입 신호 : " + str(strCode) + ", " + str(strCodeName))
            # self.pteLog.appendPlainText(
            #     str(logDateTime) + " 편입 신호 : " + str(strCode) + ", " + str(strCodeName))  # 트레이딩 화면 내역에 로그를 남김
        elif str(strType) == "D":  # 이탈 종목이라면
            print(str(logDateTime) + " 이탈 신호 : " + str(strCode) + ", " + str(strCodeName))
            # self.pteLog.appendPlainText(
            #     str(logDateTime) + " 이탈 신호 : " + str(strCode) + ", " + str(strCodeName))  # 트레이딩 화면 내역에 로그를 남김
        # finally:
        #     self.condition_event_loop.exit()

    ######################## 주문체결 관련 ########################
    def _receive_chejan_data(self, gubun, itemCnt, fidList):
        """
        주문 접수/확인 수신시 이벤트
        주문요청후 주문접수, 체결통보, 잔고통보를 수신할 때 마다 호출됩니다.
        :param gubun: string - 체결구분('0': 주문접수/주문체결, '1': 잔고통보, '3': 특이신호)
        :param itemCnt: int - fid의 갯수
        :param fidList: string - fidList 구분은 ;(세미콜론) 이다.
        """

        fids = fidList.split(';')
        print("[receiveChejanData]")
        print("gubun: ", gubun, "itemCnt: ", itemCnt, "fidList: ", fidList)
        print("========================================")
        print("[ 구분: ", self.getChejanData(913) if '913' in fids else '잔고통보', "]")
        # for fid in fids:
        #     print(FidList.CHEJAN[int(fid)] if int(fid) in FidList.CHEJAN else fid, ": ", self.getChejanData(int(fid)))
        print("========================================")


    ###############################################################
    # 메서드 정의: 주문과 잔고처리 관련 메서드                              #
    # 1초에 5회까지 주문 허용                                          #
    ###############################################################
    def sendOrder(self, requestName, screenNo, accountNo, orderType, code, qty, price, hogaType, originOrderNo):

        """
        주식 주문 메서드
        sendOrder() 메소드 실행시,
        OnReceiveMsg, OnReceiveTrData, OnReceiveChejanData 이벤트가 발생한다.
        이 중, 주문에 대한 결과 데이터를 얻기 위해서는 OnReceiveChejanData 이벤트를 통해서 처리한다.
        OnReceiveTrData 이벤트를 통해서는 주문번호를 얻을 수 있는데, 주문후 이 이벤트에서 주문번호가 ''공백으로 전달되면,
        주문접수 실패를 의미한다.
        :param requestName: string - 주문 요청명(사용자 정의)
        :param screenNo: string - 화면번호(4자리)
        :param accountNo: string - 계좌번호(10자리)
        :param orderType: int - 주문유형(1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정)
        :param code: string - 종목코드
        :param qty: int - 주문수량
        :param price: int - 주문단가
        :param hogaType: string - 거래구분(00: 지정가, 03: 시장가, 05: 조건부지정가, 06: 최유리지정가, 그외에는 api 문서참조) 시장가로 주문을 넣으면 price는 빈 값(" ")이어야 한다.
        :param originOrderNo: string - 원주문번호(신규주문에는 공백, 정정및 취소주문시 원주문번호르 입력합니다.)
        """
        # 1초에 5회만 주문이 가능하다.

        if not self.getConnectState():
            raise KiwoomConnectError()

        if not (isinstance(requestName, str)
                and isinstance(screenNo, str)
                and isinstance(accountNo, str)
                and isinstance(orderType, int)
                and isinstance(code, str)
                and isinstance(qty, int)
                and isinstance(price, int)
                and isinstance(hogaType, str)
                and isinstance(originOrderNo, str)):

            raise ParameterTypeError()

        returnCode = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                      [requestName, screenNo, accountNo, orderType, code, qty, price, hogaType, originOrderNo])

        # if returnCode != ReturnCode.OP_ERR_NONE:
        #     raise KiwoomProcessingError("sendOrder(): " + ReturnCode.CAUSE[returnCode])

        # receiveTrData() 에서 루프종료
        self.orderLoop = QEventLoop()
        self.orderLoop.exec_()

    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")

    def changeFormat(self, data, percent=0):
        if percent == 0:
            d = int(data)
            formatData = '{:-,d}'.format(d)

        elif percent == 1:
            f = int(data) / 100
            formatData = '{:-,.2f}'.format(f)

        elif percent == 2:
            f = float(data)
            formatData = '{:-,.2f}'.format(f)

        return formatData

    @staticmethod
    def change_format(data):
        strip_data = data.lstrip('-0')
        if strip_data == '':
            strip_data = '0'

        try:
            format_data = format(int(strip_data), ',d')
        except:
            format_data = format(float(strip_data))
        if data.startswith('-'):
            format_data = '-' + format_data

        return format_data


    @staticmethod
    def change_format2(data):
        strip_data = data.lstrip('-0')

        if strip_data == '':
            strip_data = '0'

        if strip_data.startswith('.'):
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data

        return strip_data

    def reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        kiwoom = Kiwoom()

        # Kiwoom.codelistArray = {'Kiwoom': []}

        # Kiwoom.get_condition_load()

        # print("main 0번째: ", Kiwoom.codelistArray['Kiwoom'][0])

        # opt10004 TR 요청, 주식호가요청
        # Kiwoom.set_input_value("종목코드", "001200")
        # Kiwoom.comm_rq_data("opt10004_req", "opt10004", 0, "0101")


        # Kiwoom.setRealReg("012345", Kiwoom.codelistArray['Kiwoom'], "10;", "0")
        # Kiwoom.setRealReg("012345", '081150', "10;", "0")


        # Kiwoom.set_input_value("종목코드", "000400")
        # Kiwoom.comm_rq_data("opt10003_req", "opt10003", 0, "0101") # opt10003 : 체결정보요청


        kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        # opt10081 TR 요청
        kiwoom.set_input_value("종목코드", "078130")
        kiwoom.set_input_value("기준일자", "20200801")
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10082_req", "opt10082", 0, kiwoom.screen_my_info)
        kiwoom.tr_event_loop.exec_()

        # while Kiwoom.remained_data == True:
        #     time.sleep(TR_REQ_TIME_INTERVAL)
        #     KiwoomFunc.set_input_value("종목코드", "078130")
        #     KiwoomFunc.set_input_value("기준일자", "20200608")
        #     KiwoomFunc.set_input_value("수정주가구분", "1")
        #     KiwoomFunc.comm_rq_data("opt10081_req", "opt10081", 2, Kiwoom.screen_my_info)
        #     Kiwoom.tr_event_loop.exec_()

        df = pd.DataFrame(kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],index=kiwoom.ohlcv['date'])

        print(df)

        # df_sorted = df.sort_index()

        # ma5 = df_sorted['close'].rolling(window=5).mean()
        # ma10 = df_sorted['close'].rolling(window=10).mean()
        # ma20 = df_sorted['close'].rolling(window=20).mean()
        # ma60 = df_sorted['close'].rolling(window=60).mean()
        # ma120 = df_sorted['close'].rolling(window=120).mean()

        # df_sorted.insert(len(df_sorted.columns), "MA5", ma5)
        # df_sorted.insert(len(df_sorted.columns), "MA10", ma10)
        # df_sorted.insert(len(df_sorted.columns), "MA20", ma20)
        # df_sorted.insert(len(df_sorted.columns), "MA60", ma60)
        # df_sorted.insert(len(df_sorted.columns), "MA120", ma120)

        # con = sqlite3.connect("d:/finance_data/sqlite/stock_jarvis.db")
        # df_sorted.to_sql('039490', con, if_exists='replace')

    except Exception as e:
        print(e)

    sys.exit(app.exec_())  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기, 마지막에 있어야 한다!



