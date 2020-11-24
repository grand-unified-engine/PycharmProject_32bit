import os
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QEventLoop
from Kiwoom.KiwoomAPI import Api, RealType
from Kiwoom.EventLoop import EventLoop
from Kiwoom.config.log_class import Logging
# from Kiwoom.config.MariaDB import MarketDB
from Kiwoom.quant.Analyzer_daily import Analyzer as Analyzer_daily
from Kiwoom.quant.Analyzer_minute import Analyzer as Analyzer_minute
import pandas as pd
import operator


class Signal:
    def __init__(self):

        self.api = Api()
        self.real_type = RealType()
        self.logging = Logging()

        # self.init_dict = {"매수매도": "매수", "순매수리스트": [], "매도우선호가리스트": [], "매도호가직전대비1": [], "전환점여부": False, "체결량리스트": [], "세력체결조절여부": False,
        #                   "이평선허락": False, "신호": False}

        self.init_dict = {"매수매도": "매수", "이평선허락": False, "신호": False}

        self.portfolio_stock_dict = {}

        # self.mk = MarketDB()
        self.analyzer_daily = Analyzer_daily()
        self.analyzer_minute = Analyzer_minute()

        # self.read_code()

        self.event_loop = EventLoop(self.api, self.real_type, self.logging, self.portfolio_stock_dict,
                                    self.analyzer_daily, self.analyzer_minute)

        ####### 요청 스크린 번호
        self.screen_real_stock = "5000"  # 종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000"  # 종목별 할당할 주문용스크린 번호

        self.temp_screen_real_stock = "7000"  # 종목별 할당할 스크린 번호
        self.temp_screen_meme_stock = "8000"  # 종목별 할당할 주문용스크린 번호
        ########################################

        self.another_job_stop = False

    def login_commConnect(self):
        self.api.comm_connect()  # 로그인 요청 시그널
        # self.api.server_gubun = self.api.get_login_info("GetServerGubun") -> 로그인이 안된 상태에서 이거 호출하면 오류 발생함. get_account_info에서 호출
        self.event_loop.login_event_loop.exec_()  # 이벤트루프 실행

    ###############################################################
    # 계좌번호 가져오기                                            #
    ###############################################################
    def get_account_info(self):
        self.event_loop.account_num = self.api.get_login_info("ACCNO").strip(';')
        # self.logging.logger.debug("계좌번호 : %s" % self.event_loop.account_num)
        print("계좌번호 : %s" % self.event_loop.account_num)

        self.api.server_gubun = self.api.get_login_info("GetServerGubun")

    ###############################################################
    # 메서드 정의: opw00001 : 예수금상세현황요청                    #
    ###############################################################
    def detail_account_info(self, sPrevNext="0"):
        self.api.set_input_value("계좌번호", self.event_loop.account_num)
        self.api.set_input_value("비밀번호", "6285")
        self.api.set_input_value("비밀번호입력매체구분", "00")
        self.api.set_input_value("조회구분", "1")

        self.api.comm_rq_data("예수금상세현황요청", "opw00001", sPrevNext, self.event_loop.screen_my_info)
        self.event_loop.detail_account_info_event_loop.exec_()

    ###############################################################
    # 메서드 정의: opw00018 : 계좌평가잔고내역요청                  #
    ###############################################################
    def detail_account_mystock(self, sPrevNext="0"):
        self.api.set_input_value("계좌번호", self.event_loop.account_num)
        self.api.set_input_value("비밀번호", "6285")
        self.api.set_input_value("비밀번호입력매체구분", "00")
        self.api.set_input_value("조회구분", "1")

        self.api.comm_rq_data("계좌평가잔고내역요청", "opw00018", sPrevNext, self.event_loop.screen_my_info)
        self.event_loop.detail_account_info_event_loop.exec_()

    ###############################################################
    # 메서드 정의: opt10075 : 실시간미체결요청                      #
    ###############################################################
    def not_concluded_account(self, sPrevNext="0"):
        self.api.set_input_value("계좌번호", self.event_loop.account_num)
        self.api.set_input_value("체결구분", "1")
        self.api.set_input_value("매매구분", "0")

        self.api.comm_rq_data("실시간미체결요청", "opt10075", sPrevNext, self.event_loop.screen_my_info)

        self.event_loop.detail_account_info_event_loop.exec_()

    ###############################################################
    # 메서드 정의: 실시간 시세를 등록하는 함수                      #
    ###############################################################
    def call_set_real_reg(self, screenNo, codelist, fidlist, optType):
        self.api.set_real_reg(screenNo, codelist, fidlist, optType)

    ###############################################################
    # 메서드 정의: 사용자 조건검색 목록을 서버에 요청                     #
    ###############################################################
    def get_condition_load(self):
        self.api.get_condition_load()

    ###############################################################
    # 포트폴리오 테이블 읽기                                         #
    ###############################################################
    def read_code(self):

        df = self.mk.get_portfolio()

        for row in df.itertuples():
            stock_code = row[1]
            self.portfolio_stock_dict.update({stock_code: self.init_dict})
            # algorithm_num = row[2]
            # self.self.portfolio_stock_dict.update({stock_code: {"알고리즘번호": algorithm_num}})

        print("read_code : {}".format(self.portfolio_stock_dict))

    ###############################################################
    # 포트폴리오 파일 읽기                                         #
    ###############################################################
    def screen_number_setting(self):

        screen_overwrite = []

        # 포트폴리오 테이블에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():

            if code not in screen_overwrite:
                screen_overwrite.append(code)

            # read_code에서 넣으므로 여기 매수매도 키 안 넣어도 됨
            self.minute_candle_req(code=code)  # 시스템 시작할 때 분봉 데이터를 가져온다.

            # with self.mk.conn.cursor() as curs:
            #     sql = "UPDATE portfolio_stock SET is_receive_real = True WHERE code = '{}'" \
            #         .format(code)
            #     curs.execute(sql)
            #     self.mk.conn.commit()

        # print("self.self.portfolio_stock_dict 스크린 넘버 세팅: {}".format(self.self.portfolio_stock_dict))

        # 계좌평가잔고내역에 있는 종목들
        for code in self.event_loop.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

            self.portfolio_stock_dict.update({code: self.init_dict})
            self.portfolio_stock_dict[code].update({"매수매도": "매도"})

            self.minute_candle_req(code=code)  # 시스템 시작할 때 분봉 데이터를 가져온다.

        # print("self.account_stock_dict 스크린 넘버 세팅 : {}".format(self.event_loop.account_stock_dict))

        # 미체결에 있는 종목들
        for order_number in self.event_loop.not_account_stock_dict.keys():
            code = self.event_loop.not_account_stock_dict[order_number]['종목코드']
            order_gubun = self.event_loop.not_account_stock_dict[order_number]['주문구분']
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            if code not in screen_overwrite:
                screen_overwrite.append(code)

            self.portfolio_stock_dict.update({code: self.init_dict})
            self.portfolio_stock_dict[code].update({"매수매도": order_gubun})

        # print("self.not_account_stock_dict 스크린 넘버 세팅 : {}".format(self.event_loop.not_account_stock_dict))

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            # self.event_loop.real_data_dict.update({code: {}})  # 실시간 분봉 만들기 위한 dict 2020-10-26

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            # if code in self.portfolio_stock_dict.keys():
            self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
            self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            # elif code not in self.portfolio_stock_dict.keys():
            #     self.portfolio_stock_dict.update(
            #         {code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

        QTest.qWait(500)  # 분봉호출보다 real_data reg가 먼저 작업되어서 추가
        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # fids = self.real_type.REALTYPE['주식체결']['체결시간']
            a = self.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            b = self.real_type.REALTYPE['주식체결']['체결시간']
            fids = str(a) + ';' + str(b)
            # fids = b
            self.call_set_real_reg(screen_num, code, fids, "1")

    def screen_number_real_time_setting(self):

        screen_overwrite = []

        for code in self.portfolio_stock_dict.keys():
            # print("screen_number_real_time_setting 코드: {}, dict: {}".format(code, self.portfolio_stock_dict[code]))
            if "스크린번호" not in self.portfolio_stock_dict[code]:
                screen_overwrite.append(code)
                self.minute_candle_req(code=code)

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.temp_screen_real_stock)
            meme_screen = int(self.temp_screen_meme_stock)

            temp_screen += 1
            self.temp_screen_real_stock = str(temp_screen)

            meme_screen += 1
            self.temp_screen_meme_stock = str(meme_screen)

            self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
            self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            # print("screen_number_real_time_setting 코드: {}, dict: {}".format(code, self.portfolio_stock_dict[code]))
            #
            # if code not in self.event_loop.condition_stock:
            # with self.mk.conn.cursor() as curs:
            #     sql = "UPDATE portfolio_stock SET is_receive_real = True WHERE code = '{}'" \
            #         .format(code)
            #     curs.execute(sql)
            #     self.mk.conn.commit()

            # self.event_loop.real_data_dict.update({code: {}})  # 실시간 분봉 만들기 위한 dict 2020-10-26

            cnt += 1

        QTest.qWait(500)  # 분봉호출보다 real_data reg가 먼저 작업되어서 추가
        for code in screen_overwrite:
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # fids = self.real_type.REALTYPE['주식체결']['체결시간']
            a = self.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            b = self.real_type.REALTYPE['주식체결']['체결시간']
            fids = str(a) + ';' + str(b)
            # fids = b
            self.call_set_real_reg(screen_num, code, fids, "1")

    '''
    포트폴리오 테이블에 새로 들어온 종목
    '''

    def real_time_new_portfolio_fuc(self):
        db = MarketDB()
        df = db.get_portfolio()
        del db

        if df is not None:
            for row in df.itertuples():
                stock_code = row[1]
                print("새로 들어왔따: {}".format(stock_code))
                if self.api.server_gubun == "1":
                    if stock_code == '096350' or stock_code == '96040':  # 096350(대창솔루션) 모의투자 매매 불가능
                        continue

                self.portfolio_stock_dict.update({stock_code: self.init_dict})

    '''
    조검검색에 새로 들어온 종목
    '''

    def real_time_condition_stock_fuc(self):
        copy_condition_stock = self.event_loop.condition_stock.copy()
        for code in copy_condition_stock:
            # print("code : {}".format(code))
            for key, value in copy_condition_stock[code].items():
                if value is True:
                    del copy_condition_stock[code]

        self.logging.logger.debug("copy_condition_stock : {}".format(copy_condition_stock))

        i = 0
        for code in copy_condition_stock:
            # if not copy_condition_stock[code]['portfolio_stock_dict추가여부']:
            # print("조건검색 새로 들어왔따: {}".format(code))
            if self.api.server_gubun == "1":
                if code == '096350' or code == '96040':  # 096350(대창솔루션) 모의투자 매매 불가능
                    continue

            self.event_loop.condition_stock[code].update({"portfolio_stock_dict추가여부": True})
            self.portfolio_stock_dict.update({code: self.init_dict})

            if i >= 10:
                break

            i += 1

    '''
    * 거래량 급증 종목 기준
    * 2020-10-14 개발 시작
    2020-10-18 
    스켈핑으로 개발
    2020-10-20 
    신고가 호출하는 걸로 변경
    ------------------------------------   
    
    '''

    def gathering_money_fuc(self):
        # global count, sched
        self.new_high_req()

        top_data = []
        if self.event_loop.gathering_money_stock is not None:

            for row in self.event_loop.gathering_money_stock:

                if self.api.server_gubun == "1":
                    if row[0] == '096350' or row[0] == '96040':  # 096350(대창솔루션) 모의투자 매매 불가능
                        continue

                df = self.mk.get_daily_price(row[0])

                market = self.api.get_login_info(tag="GetMasterStockInfo", code=row[0]).split(";")[0].split("|")[1]

                if market == '거래소' or market == '코스닥':
                    # print("종목명 : {}, 종목코드 : {}, 시장구분 : {}".format(row[1], row[0], market))
                    if self.analyzer_daily.get_side_by_side_rise(df) or self.analyzer_daily.get_disparity(df):
                        top_data.append(row[0])

            # print("top_data : {}".format(top_data))

        for code in self.portfolio_stock_dict.keys():
            for i in top_data:  # screen_number_setting에 갔다 온 코드는 screen_number_setting에서 부여한 스크린 번호 사용
                if i == code:
                    top_data.remove(i)

        max_invest_num = 10
        remain = max_invest_num - len(self.portfolio_stock_dict)
        top_data = top_data[0:remain]

        self.event_loop.vol_uprise_stock_dict.clear()

        for code in top_data:
            self.event_loop.vol_uprise_stock_dict.update({code: {}})
        #
        # 스크린번호 할당
        cnt = 0
        for code in self.event_loop.vol_uprise_stock_dict.keys():

            temp_screen = int(self.temp_screen_real_stock)
            meme_screen = int(self.temp_screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.temp_screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.temp_screen_meme_stock = str(meme_screen)

            self.event_loop.vol_uprise_stock_dict.update(
                {code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)}})
            self.portfolio_stock_dict.update(
                {code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock),
                        "매수매도": "매수"}})
            cnt += 1

        print("self.vol_uprise_stock_dict : {}".format(self.event_loop.vol_uprise_stock_dict))

        for code in self.event_loop.vol_uprise_stock_dict.keys():
            screen_num = self.event_loop.vol_uprise_stock_dict[code]['스크린번호']
            fids = self.real_type.REALTYPE['주식체결']['체결시간']
            # a = signal.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            # b = signal.real_type.REALTYPE['주식체결']['체결시간']
            # fids = str(a) + ';' + str(b)
            # fids = b
            # self.signal.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")
            self.call_set_real_reg(screen_num, code, fids, "1")

    # 신고저가요청
    def new_high_req(self):

        self.api.set_input_value("시장구분", '000')
        self.api.set_input_value("신고저구분", '1')
        self.api.set_input_value("고저종구분", "2")
        self.api.set_input_value("거래량구분",
                                 "00020")  # 00000:전체조회, 00010:만주이상, 00050:5만주이상, 00100:10만주이상, 00150:15만주이상, 00200:20만주이상, 00300:30만주이상, 00500:50만주이상, 01000:백만주이상
        self.api.set_input_value("상하한포함", "0")  # 0:미포함, 1:포함
        self.api.set_input_value("기간", "20")  # 5:5일, 10:10일, 20:20일, 60:60일, 250:250일, 250일까지 입력가능

        self.api.comm_rq_data("신고저가요청", "opt10016", 0, self.event_loop.screen_calculation_stock)

        self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

    def gathering_money_fuc_bak(self, is_after="2"):
        # global count, sched

        '''
        거래량 급증 이용
        '''
        # if is_after == '1':
        #     self.volume_uprise_req("2", "500") # 전일 가져오기. 거래량 급증 tr 요청 -> 거래량 급증 테이블 insert
        # else:
        #     self.volume_uprise_req("1", "500", "1")  # 1분 전 가져오기. 거래량 급증 tr 요청 -> 거래량 급증 테이블 insert

        #
        # QTest.qWait(1000)

        # print(self.event_loop.volume_uprise)
        calcu_data = []
        top_data = []
        if self.event_loop.gathering_money_stock is not None:

            # calcu_data = [x for x in self.event_loop.gathering_money_stock if (0 < float(x[5]) <= 8)]
            # calcu_data = calcu_data[:5]
            # print("5개 골라낸거 : {}".format(calcu_data))

            for row in calcu_data:
                # if len(top_data) == 2:
                #     break
                if self.api.server_gubun == "1":
                    if row[0] == '096350' or row[0] == '96040':  # 096350(대창솔루션) 모의투자 매매 불가능
                        continue

                # if self.get_ma20v_low(row[0]):
                #     top_data.append(row[0])
                # print(float(row[5]))

                # if float(row[5]) > 0 and float(row[5]) <= 8:
                # QTest.qWait(3600)
                # self.minute_candle_req(row[0], buy_sell_gubn='1') # 1은 매수 확인

            # QTest.qWait(1000)
            for code in self.event_loop.convergence_dict.keys():
                if self.event_loop.convergence_dict[code] == True:
                    top_data.append(code)

            print("top_data : {}".format(top_data))

        for code in self.portfolio_stock_dict.keys():
            for i in top_data:  # screen_number_setting에 갔다 온 코드는 screen_number_setting에서 부여한 스크린 번호 사용
                if i == code:
                    top_data.remove(i)

        self.event_loop.vol_uprise_stock_dict.clear()

        for code in top_data:
            self.event_loop.vol_uprise_stock_dict.update({code: {}})
        #
        # 스크린번호 할당
        cnt = 0
        for code in self.event_loop.vol_uprise_stock_dict.keys():

            temp_screen = int(self.temp_screen_real_stock)
            meme_screen = int(self.temp_screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.temp_screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.temp_screen_meme_stock = str(meme_screen)

            # 포트폴리오에 없을 때만 스크린번호 생성
            # if code in self.portfolio_stock_dict.keys():
            #     # 실시간 수신쪽 이용을 위해
            #     self.portfolio_stock_dict[code].update({"스크린번호": str(self.temp_screen_real_stock)})
            #     self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.temp_screen_meme_stock)})
            #
            #     self.vol_uprise_stock_dict[code].update({"스크린번호": str(self.temp_screen_real_stock)})
            #     self.vol_uprise_stock_dict[code].update({"주문용스크린번호": str(self.temp_screen_meme_stock)})

            # top_data.remove(i) 위에서 처리함
            # if code not in self.portfolio_stock_dict.keys():
            self.event_loop.vol_uprise_stock_dict.update(
                {code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)}})
            self.portfolio_stock_dict.update(
                {code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)}})
            cnt += 1

        print("self.vol_uprise_stock_dict : {}".format(self.event_loop.vol_uprise_stock_dict))

        for code in self.event_loop.vol_uprise_stock_dict.keys():
            screen_num = self.event_loop.vol_uprise_stock_dict[code]['스크린번호']
            fids = self.real_type.REALTYPE['주식체결']['체결시간']
            # a = signal.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            # b = signal.real_type.REALTYPE['주식체결']['체결시간']
            # fids = str(a) + ';' + str(b)
            # fids = b
            self.call_set_real_reg(screen_num, code, fids, "1")

    def sche_minute_candle(self):
        try:

            for code in self.portfolio_stock_dict.keys():
                if "스크린번호" in self.portfolio_stock_dict[code]:
                    result = None
                    self.minute_candle_req(code)
                    if self.portfolio_stock_dict[code]["매수매도"] == "매수":
                        result = self.analyzer_minute.get_buy_timing(self.event_loop.minute_candle[code])
                    else:
                        result = self.analyzer_minute.get_sell_timing(self.event_loop.minute_candle[code],
                                                                      stock_code=code)
                    self.portfolio_stock_dict[code].update({"이평선허락": result})
                    self.logging.logger.debug("코드: {}, 이평선허락: {} ".format(code, result))
                    # print("result : {}".format(self.portfolio_stock_dict[code]["이평선허락"]))
            # self.another_job_stop = False

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("sche_minute_candle() -> exception! {} ".format(str(ex)))
            return None

    # 거래량급증요청
    def volume_uprise_req(self, time_gubun, vol_gubun, time="1"):
        # QTest.qWait(300)
        if len(self.portfolio_stock_dict) <= 10:
            self.api.set_input_value("시장구분", "000")
            self.api.set_input_value("정렬구분", "1")  # 1:급증량, 2:급증률
            self.api.set_input_value("시간구분", time_gubun)  # 1:분, 2:전일
            self.api.set_input_value("거래량구분",
                                     vol_gubun)  # 5:5천주이상, 10:만주이상, 50:5만주이상, 100:10만주이상, 200:20만주이상, 300:30만주이상, 500:50만주이상, 1000:백만주이상
            self.api.set_input_value("시간", time)  # 2분전, 시간구분이 2:전일일 경우 비활성화. 2:전일일 때 입력해도 오류 안 남.

            self.api.comm_rq_data("거래량급증요청", "opt10023", "0", self.event_loop.screen_signal_event)

            # 여기 있으면 아예 slot으로 안 넘어감
            # self.api.set_real_remove("2222", "ALL")  # opt10023 : 거래량급증요청 호출해서 등록된 거 삭제

            self.event_loop.for_signal_event_loop = QEventLoop()
            self.event_loop.for_signal_event_loop.exec_()

    # 주봉 데이터
    def week_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600)
        self.event_loop.test_code = code

        self.api.set_input_value("종목코드", code)
        self.api.set_input_value("기준일자", "20201106")
        # self.api.set_input_value("끝일자", "20201013")
        self.api.set_input_value("수정주가구분", "1")

        self.api.comm_rq_data("주식주봉차트조회", "opt10082", sPrevNext, self.event_loop.screen_calculation_stock)

        self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

    # 일봉 데이터
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(300)

        # self.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.api.set_input_value("종목코드", code)
        self.api.set_input_value("수정주가구분", "1")

        if date is not None:
            self.api.set_input_value("기준일자", date)

        self.api.comm_rq_data("주식일봉차트조회", "opt10081", sPrevNext, self.event_loop.screen_calculation_stock)

        # self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

    # 분봉 데이터
    def minute_candle_req(self, code=None):
        QTest.qWait(500)

        # print("minute_candle_req code : {}".format(code))
        self.event_loop.test_code = code

        try:
            self.api.set_input_value("종목코드", code)
            self.api.set_input_value("틱범위", '1')
            self.api.set_input_value("수정주가구분", "1")

            self.api.comm_rq_data("주식분봉차트조회", "opt10080", 0, self.event_loop.screen_calculation_stock)

            self.event_loop.calculator_event_loop = QEventLoop()
            self.event_loop.calculator_event_loop.exec_()

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("minute_candle_req() -> exception! {} ".format(str(ex)))
            self.event_loop.calculator_event_loop.exit()
            return None

    # 주식기본정보요청
    def corp_info_req(self, code=None):
        QTest.qWait(3600)

        # print("corp_info_req code : {}".format(code))

        self.api.set_input_value("종목코드", code)

        self.api.comm_rq_data("주식기본정보요청", "opt10001", 0, self.event_loop.screen_calculation_stock)

        self.event_loop.for_signal_event_loop = QEventLoop()
        self.event_loop.for_signal_event_loop.exec_()

    # opt10027 : 전일대비등락률상위요청
    def everyday_anaytic_stock(self, code=None, sPrevNext="0"):
        # QTest.qWait(3600)

        # self.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        print("everyday_anaytic_stock code : {}".format(code))
        self.event_loop.test_code = code

        self.api.set_input_value("시장구분", 000)  # 000:전체, 001:코스피, 101:코스닥
        self.api.set_input_value("정렬구분", '1')

        self.api.comm_rq_data("전일대비등락률상위요청", "opt10027", sPrevNext, self.event_loop.screen_calculation_stock)

        self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

    # OPT10020 : 호가잔량상위요청
    def hoga_balance_top_req(self):

        self.api.set_input_value("시장구분", "101")  # 001:코스피, 101:코스닥
        self.api.set_input_value("정렬구분", "1")  # 1:순매수잔량순, 2:순매도잔량순, 3:매수비율순, 4:매도비율순
        self.api.set_input_value("거래량구분",
                                 "00100")  # 0000:장시작전(0주이상), 0010:만주이상, 0050:5만주이상, 00100:10만주이상

        self.api.comm_rq_data("호가잔량상위요청", "opt10020", 0, self.event_loop.screen_calculation_stock)

        self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

    ###############################################################
    # 종목 분석                                                    #
    ###############################################################

    def calculator_fuc(self):
        ###############################################################
        '''
        알고리즘 테스트
        :return:
        '''
        # code_list = self.api.get_code_list_by_market("0")
        # code_list.extend(self.api.get_code_list_by_market("10"))
        # # code_list.extend(self.api.get_code_list_by_market("8"))
        #
        # # code_list = self.api.get_code_list_by_market("10")
        # # print("code_list : {}".format(self.analyzer.mk.codes))
        #
        # # self.logging.logger.debug('코스닥 갯수 : {}'.format(len(code_list)))
        # # code_list = ['041190']  #
        # #
        # top_data = []
        # for idx, code in enumerate(code_list):
        #     # self.minute_candle_req(code=code)
        #
        #     df = self.mk.get_daily_price(code, end_date="2020-10-19")
        #
        #     # if self.analyzer_daily.get_side_by_side_rise(df):
        #     if self.analyzer_daily.get_disparity(df):
        #         top_data.append(code)
        #
        #
        # print("top_data : {}".format(top_data))
        ###############################################################

        ###############################################################
        '''
        tr 테스트
        :return:
        '''
        # code_list = self.api.get_code_list_by_market("0")
        # code_list.extend(self.api.get_code_list_by_market("10"))
        # code_list.extend(self.api.get_code_list_by_market("8"))

        # code_list = self.api.get_code_list_by_market("10")
        # # print("code_list : {}".format(self.analyzer.mk.codes))
        #
        # # self.logging.logger.debug('코스닥 갯수 : {}'.format(len(code_list)))
        # # code_list = ['011150']  #
        # # #
        # # top_data = []
        # for idx, code in enumerate(code_list):
        #     # self.minute_candle_req(code=code)
        #     self.hoga_balance_top_req()

        ###############################################################

        ###############################################################
        '''
        주봉 테이블에 저장
        :return: 
        '''
        # sql = "SELECT a.code, a.company FROM company_info a where code > '045300'"
        # sql = "SELECT a.code, a.company FROM company_info a LEFT OUTER JOIN (select distinct code from week_price WHERE DATE = '2020-10-19') b on a.code = b.code WHERE b.code IS NULL"
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.mk.conn)
        for idx in range(len(df)):
            self.week_kiwoom_db(code=df['code'].values[idx])
        ###############################################################

    def make_minute_candle_func(self, code):

        if code in self.event_loop.minute_candle_dict:  # 분봉을 먼저 읽어라
            if code in self.event_loop.real_data_dict:  # 실시간 주식체결 데이터
                copy_real_data_dict = self.event_loop.real_data_dict[code].copy()  # 반복문 오류를 피하기 위해. 내용은 같지만 독립적인 딕셔너리
                # {'114622': {'close': [2430], 'volume': [10]}, '114616': {'close': [2425], 'volume': [200]}}
                # self.event_loop.real_data_dict[code] 기존거를 삭제 할 수 없을까?

                ##################################### 새로운 분 리스트 만들기 #####################################
                # max_hm = max(self.event_loop.minute_candle_dict[code].items(), key=operator.itemgetter(0))[0] #분봉의 최대분 값을 가져와서
                # '2020-10-30 11:46:00'
                # 초까지 있어야 하므로 기존 max_hm 로직 폐기
                max_hm = self.portfolio_stock_dict[code]['최종작업시간']  # 초기 분봉 호출, make_minute_candle_func작업 마지막에
                add_real_data_dict = {key: value for key, value in copy_real_data_dict.items() if key > max_hm}
                # {'114622': {'close': [2430], 'volume': [10]}, '114616': {'close': [2425], 'volume': [200]}}
                if copy_real_data_dict:
                    self.portfolio_stock_dict[code].update({'최종작업시간': max(copy_real_data_dict.keys())})  # 실시간 꺼로 업데이트

                key_list = list(add_real_data_dict.keys())
                # ['121522', '121520', '121523']
                s_add_real_data_dict = sorted(add_real_data_dict.items())
                # [('121520', {'close': [2440], 'volume': [10]}),
                #  ('121522', {'close': [2435, 2430, 2425], 'volume': [4802, 3207, 991]}),
                #  ('121523', {'close': [2440], 'volume': [14]})]
                for index, value in enumerate(key_list):
                    key_list[index] = self.event_loop.today + " " + value[:2] + ":" + value[2:4] + ":00"

                group_by_date_list = list(set(key_list))  # 분 단위로 키 합침
                # ['2020-10-30 12:15:00']
                ##############################################################################################################################

                for date in group_by_date_list:  # 추가해야 할 분 키값
                    if date not in self.event_loop.minute_candle_dict[code]:
                        self.event_loop.minute_candle_dict[code].update({date: {}})  # 분봉 dict 없는 것 분키 초기화
                    # low = 0
                    # high = 0
                    for key, value in enumerate(s_add_real_data_dict):  # 실시간 주식체결 데이터
                        if date == self.event_loop.today + " " + value[0][:2] + ":" + value[0][2:4] + ":00":
                            if "volume" not in self.event_loop.minute_candle_dict[code][date]:
                                self.event_loop.minute_candle_dict[code][date].update({"volume": 0})

                            volume = self.event_loop.minute_candle_dict[code][date]["volume"] + sum(value[1]["volume"])
                            self.event_loop.minute_candle_dict[code][date].update({"volume": volume})

                            # 분별로 open이 없을 때만 넣는다. 처음
                            if "open" not in self.event_loop.minute_candle_dict[code][date]:
                                self.event_loop.minute_candle_dict[code][date].update({"open": value[1]["close"][-1]})

                            if "low" not in self.event_loop.minute_candle_dict[code][date]:
                                self.event_loop.minute_candle_dict[code][date].update({"low": value[1]["close"][-1]})
                            else:
                                if self.event_loop.minute_candle_dict[code][date]['low'] > value[1]["close"][-1]:
                                    self.event_loop.minute_candle_dict[code][date].update(
                                        {"low": value[1]["close"][-1]})

                            if "high" not in self.event_loop.minute_candle_dict[code][date]:
                                self.event_loop.minute_candle_dict[code][date].update({"high": value[1]["close"][-1]})
                            else:
                                if self.event_loop.minute_candle_dict[code][date]['high'] < value[1]["close"][-1]:
                                    self.event_loop.minute_candle_dict[code][date].update(
                                        {"high": value[1]["close"][-1]})

                            self.event_loop.minute_candle_dict[code][date].update({"close": value[1]["close"][-1]})

                df = pd.DataFrame(self.event_loop.minute_candle_dict[code])
                df = df.T

                self.logging.logger.debug("code : {}, df : {}".format(code, df))

                if self.portfolio_stock_dict[code]["매수매도"] == "매수":
                    result = self.analyzer_minute.get_buy_timing(df)
                else:
                    result = self.analyzer_minute.get_sell_timing(df)
                self.logging.logger.debug("code : {}, result : {}".format(code, result))
                self.portfolio_stock_dict[code].update({"이평선허락": result})

    def checking_minute_candle_func(self, code):
        df = pd.DataFrame(self.event_loop.minute_candle_dict[code])
        df = df.T

        self.logging.logger.debug("code : {}, df : {}".format(code, df))

        if self.portfolio_stock_dict[code]["매수매도"] == "매수":
            result = self.analyzer_minute.get_buy_timing(df)
        else:
            result = self.analyzer_minute.get_sell_timing(df)
        self.logging.logger.debug("code : {}, result : {}".format(code, result))
        self.portfolio_stock_dict[code].update({"이평선허락": result})