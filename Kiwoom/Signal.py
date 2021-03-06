from PyQt5.QtTest import QTest
from PyQt5.QtCore import QEventLoop
from Kiwoom.KiwoomAPI import Api, RealType
from Kiwoom.EventLoop import EventLoop
from Kiwoom.config.log_class import Logging
from Kiwoom.config.MariaDB import MarketDB
# from Kiwoom.quant.Analyzer_daily import Analyzer as Analyzer_daily
# from Kiwoom.quant.Analyzer_minute import Analyzer as Analyzer_minute
from Kiwoom.quant.StockInfo import get_current_price
import pandas as pd
import time
# import operator


class Signal:
    def __init__(self):

        self.api = Api()
        self.real_type = RealType()
        self.logging = Logging()

        # self.init_dict = {"매수매도": "매수", "순매수리스트": [], "매도우선호가리스트": [], "매도호가직전대비1": [], "전환점여부": False, "체결init_dict량리스트": [], "세력체결조절여부": False,
        #                   "이평선허락": False, "신호": False}

        # self.init_dict = {"매수매도": "매수", "이평선허락": False, "신호": False}

        # 변동성 돌파 전략 20.12.02
        # self.init_dict = {"매수매도": "매수", "매수 목표가 중간 값": 0, "매수 목표가": 0, "ma5": 0, "ma10": 0, "신호": False}

        ######## 시스템 내 전체 포트폴리오
        self.portfolio_stock_dict = {}
        ########################

        ######## 실시간 추천 dict
        self.real_time_recommand_dict = {}
        ########################

        # self.mk = MarketDB()
        # self.analyzer_daily = Analyzer_daily()
        # self.analyzer_minute = Analyzer_minute()

        # self.read_code()

        self.event_loop = EventLoop(self.api, self.real_type, self.logging, self.portfolio_stock_dict)

        self.condition_stock = self.event_loop.condition_stock

        ####### 요청 스크린 번호
        self.screen_start_stop_real = "1000"  # 장 시작/종료 실시간 스크린 번호
        self.screen_real_stock = "5000"  # 지정한 종목의 실시간 정보 요청시 사용
        self.screen_meme_stock = "6000"  # 주문을 요청할 때 사용

        self.temp_screen_real_stock = "7000"  # 지정한 종목의 실시간 정보 요청시 사용
        self.temp_screen_meme_stock = "8000"  # 주문을 요청할 때 사용

        self.tr_test_screen_no = "9000"
        ########################################

        self.another_job_stop = False # ???
        self.real_stock_cnt = 0 # ???

    ###############################################################
    # 로그인                                                       #
    ###############################################################
    def login_commConnect(self):
        self.api.comm_connect()  # 로그인 요청 시그널
        # self.api.server_gubun = self.api.get_login_info("GetServerGubun") -> 로그인이 안된 상태에서 이거 호출하면 오류 발생함. get_account_info에서 호출
        self.event_loop.login_event_loop.exec_()  # 이벤트루프 실행

    ###############################################################
    # 계좌번호 가져오기                                            #
    ###############################################################
    def get_account_info(self):
        self.event_loop.account_num = self.api.get_login_info("ACCNO").strip(';') # 첫번째 계좌 [0] 붙이면 문자열 첫번째만 인식하게 됨.
        # self.logging.logger.debug("계좌번호 : %s" % self.event_loop.account_num)
        # print("계좌번호 : %s" % self.event_loop.account_num)

        self.api.server_gubun = self.api.get_login_info("GetServerGubun")

    ###############################################################
    # 메서드 정의: opw00001 : 예수금상세현황요청                    #
    ###############################################################
    def detail_account_info(self, sPrevNext="0"):
        self.api.set_input_value("계좌번호", self.event_loop.account_num)
        self.api.set_input_value("비밀번호", "8374")
        self.api.set_input_value("비밀번호입력매체구분", "00")
        self.api.set_input_value("조회구분", "1")

        self.api.comm_rq_data("예수금상세현황요청", "opw00001", sPrevNext, self.event_loop.screen_my_info)
        self.event_loop.detail_account_info_event_loop.exec_()

    ###############################################################
    # 메서드 정의: opw00018 : 계좌평가잔고내역요청                  #
    ###############################################################
    def detail_account_mystock(self, sPrevNext="0"):
        self.api.set_input_value("계좌번호", self.event_loop.account_num)
        self.api.set_input_value("비밀번호", "8374")
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
        ret = self.api.set_real_reg(screenNo, codelist, fidlist, optType)
        return ret

    ###############################################################
    # 메서드 정의: 사용자 조건검색 목록을 서버에 요청                     #
    ###############################################################
    def get_condition_load(self):
        self.api.get_condition_load()

    ###############################################################
    # 포트폴리오 파일 읽기                                         #
    ###############################################################
    def screen_number_setting(self):

        screen_overwrite = []

        # 계좌평가잔고내역에 있는 종목들
        for code in self.event_loop.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        # 미체결에 있는 종목들
        for order_number in self.event_loop.not_account_stock_dict.keys():
            code = self.event_loop.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 담겨있는 종목들
        # for code in self.portfolio_stock_dict.keys():
        #
        #     if code not in screen_overwrite:
        #         screen_overwrite.append(code)
        # 조선비즈에서 가져오도록 하면 처음에 self.portfolio_stock_dict 데이터 없으므로 막음

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0: # 하나의 스크린번호에 50개씩 담는다!!
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            self.portfolio_stock_dict.update(
                {code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

        # print("screen_number_setting : {}".format(self.portfolio_stock_dict))

        #실시간 수신 관련 함수
        # self.call_set_real_reg(self.screen_start_stop_real, ' ', self.real_type.REALTYPE['장시작시간']['장운영구분'], "0")

        for code in self.portfolio_stock_dict.keys():
            # QTest.qWait(300) #여기에 이거 있어도 끝나기 전 다음 실행되는거 같은데??
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # fids = self.real_type.REALTYPE['주식체결']['체결시간']
            # a = self.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            b = self.real_type.REALTYPE['주식체결']['현재가']
            # fids = str(a) + ';' + str(b)
            fids = b
            self.call_set_real_reg(screen_num, code, fids, "1")



    def screen_number_real_time_setting2(self):

        screen_overwrite = []

        # 실시간 추천 종목
        for code, value in self.real_time_recommand_dict.items():
            if value["numbering"] is False:
                if code not in screen_overwrite:
                    if code not in self.portfolio_stock_dict.keys():
                        self.portfolio_stock_dict.update({code: {"매수매도": "매수"}})
                        screen_overwrite.append(code)
                        self.logging.logger.debug("스크린 넘버 세팅 새로 들어온 종목: {}, portfolio_stock_dict: {}".format(code,
                                                                                                       self.portfolio_stock_dict[
                                                                                                           code]))

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.temp_screen_real_stock)
            meme_screen = int(self.temp_screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.temp_screen_real_stock = str(temp_screen)
            if (cnt % 50) == 0:
                meme_screen += 1
                self.temp_screen_meme_stock = str(meme_screen)

            self.portfolio_stock_dict[code].update({"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)})
            # self.portfolio_stock_dict.update({code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)}})
            cnt += 1

        # print("screen_number_real_time_setting screen_overwrite dict: {}".format(screen_overwrite))
        screen_num = ''
        code_list = ''
        fids = ''
        for code in screen_overwrite:
            # QTest.qWait(5000)
            self.real_time_recommand_dict[code].update({"numbering": True})
            print("code: {}, real_time_recommand_dict : {}".format(code, self.real_time_recommand_dict[code]))
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # fids = self.real_type.REALTYPE['주식체결']['체결시간']
            # a = self.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            b = self.real_type.REALTYPE['주식체결']['현재가']
            # fids = str(a) + ';' + str(b)
            fids = b
            code_list = code_list + ';' + code

        if code_list != '':
            QTest.qWait(1000)
            ret = self.call_set_real_reg(screen_num, code_list[1:], fids, "1")
            self.logging.logger.debug("실시간 등록 코드: {}, 실시간 등록 리턴값: {}".format(code_list, ret))



    def screen_number_real_time_setting(self):

        screen_overwrite = []

        # 실시간 추천 종목
        for code, value in self.real_time_recommand_dict.items():
            if value["numbering"] is False:
                if code not in screen_overwrite:
                    if code not in self.portfolio_stock_dict.keys():
                        self.portfolio_stock_dict.update({code: {"매수매도": "매수"}})
                        screen_overwrite.append(code)
                        self.logging.logger.debug("스크린 넘버 세팅 새로 들어온 종목: {}, portfolio_stock_dict: {}".format(code,
                                                                                                       self.portfolio_stock_dict[
                                                                                                           code]))

        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.temp_screen_real_stock)
            meme_screen = int(self.temp_screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.temp_screen_real_stock = str(temp_screen)
            if (cnt % 50) == 0:
                meme_screen += 1
                self.temp_screen_meme_stock = str(meme_screen)

            self.portfolio_stock_dict[code].update({"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)})
            # self.portfolio_stock_dict.update({code: {"스크린번호": str(self.temp_screen_real_stock), "주문용스크린번호": str(self.temp_screen_meme_stock)}})
            cnt += 1

        # print("screen_number_real_time_setting screen_overwrite dict: {}".format(screen_overwrite))
        # db = MarketDB()
        screen_num = ''
        code_list = ''
        fids = ''
        for code in screen_overwrite:
            # QTest.qWait(5000)
            self.real_time_recommand_dict[code].update({"numbering": True})
            print("code: {}, real_time_recommand_dict : {}".format(code, self.real_time_recommand_dict[code]))
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            # fids = self.real_type.REALTYPE['주식체결']['체결시간']
            # a = self.real_type.REALTYPE['주식호가잔량']['매도호가총잔량']
            b = self.real_type.REALTYPE['주식체결']['현재가']
            # fids = str(a) + ';' + str(b)
            fids = b
            code_list = code_list + ';' + code
            # self.logging.logger.debug("실시간 가자~ 스크린번호: {}, fids: {}, 코드: {}".format(screen_num, fids, code))
            # with db.conn.cursor() as curs:
            #     sql = "UPDATE portfolio_stock SET is_receive_real = '1' WHERE code = '{}' and create_date = '{}' " \
            #         .format(code, self.event_loop.today)
            #     curs.execute(sql)
            #     db.conn.commit()

        if code_list != '':
            QTest.qWait(3000)
            ret = self.call_set_real_reg(screen_num, code_list[1:], fids, "1")
            self.logging.logger.debug("실시간 등록 코드: {}, 실시간 등록 리턴값: {}".format(code_list, ret))

        # del db

    '''
    포트폴리오 테이블에 새로 들어온 종목
    '''
    def real_time_recommand_fuc(self):
        db = MarketDB()
        df = db.get_portfolio()

        if df is not None:
            for row in df.itertuples():
                stock_code = row[1]
                if stock_code not in self.portfolio_stock_dict.keys(): #이미 시스템에서 해당 종목코드가 돌고 있으면 제외
                    if self.api.server_gubun == "1":
                        # is_receive_real = 0이면 자꾸 들어오니까 강제로 1로 바꿈 (나중에 테이블 수정하기!!!) 2021-02-18
                        if stock_code == '066430' or stock_code == '570045' or stock_code == '036630' or stock_code == '093230':  # 066430(와이오엠), 570045(TRUE 레버리지 천연가스 선물ETN) 모의투자 매매 불가능
                            with db.conn.cursor() as curs:
                                sql = "UPDATE portfolio_stock SET is_receive_real = '1' WHERE code = '{}' and create_date = '{}' " \
                                    .format(stock_code, self.event_loop.today)
                                curs.execute(sql)
                                db.conn.commit()
                            continue
                        else: # 매매 불가능 코드 외 추가
                            self.real_time_recommand_dict.update(
                                {stock_code: {"ub": row[2], "time": time.strftime('%H%M%S'), "numbering": False}})
                            self.logging.logger.debug("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(stock_code,
                                                                                                           self.real_time_recommand_dict[
                                                                                                               stock_code]))
                    else: # 실서버일 때
                        self.real_time_recommand_dict.update({stock_code: {"ub": row[2], "time": time.strftime('%H%M%S'), "numbering": False}})
                        self.logging.logger.debug("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(stock_code, self.real_time_recommand_dict[stock_code]))
        del db


    # 신고저가요청
    def new_high_req(self):

        self.api.set_input_value("시장구분", '000')
        self.api.set_input_value("신고저구분", '1')
        self.api.set_input_value("고저종구분", "2")
        self.api.set_input_value("거래량구분",
                                 "00020")  # 00000:전체조회, 00010:만주이상, 00050:5만주이상, 00100:10만주이상, 00150:15만주이상, 00200:20만주이상, 00300:30만주이상, 00500:50만주이상, 01000:백만주이상
        self.api.set_input_value("상하한포함", "0")  # 0:미포함, 1:포함
        self.api.set_input_value("기간", "20")  # 5:5일, 10:10일, 20:20일, 60:60일, 250:250일, 250일까지 입력가능

        self.api.comm_rq_data("신고저가요청", "opt10016", 0, "1111")

        self.event_loop.calculator_event_loop = QEventLoop()
        self.event_loop.calculator_event_loop.exec_()

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

    # 일봉 데이터 요청
    def day_candle_req(self, code=None, date=None, sPrevNext="0"):
        # QTest.qWait(3600)
        # self.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.api.set_input_value("종목코드", code)
        self.api.set_input_value("수정주가구분", "1")

        if date is not None:
            self.api.set_input_value("기준일자", date)

        self.api.comm_rq_data("주식일봉차트조회", "opt10081", sPrevNext, self.event_loop.screen_analyze_stock)

        self.event_loop.analyze_event_loop.exec_()

    # 분봉 데이터
    def minute_candle_req(self, code=None):
        # QTest.qWait(3600)

        # print("minute_candle_req code : {}".format(code))
        self.event_loop.test_code = code

        try:
            self.api.set_input_value("종목코드", code)
            self.api.set_input_value("틱범위", '1')
            self.api.set_input_value("수정주가구분", "1")

            self.api.comm_rq_data("주식분봉차트조회", "opt10080", 0, self.tr_test_screen_no)

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


    def get_target_price(self, code):
        """매수 목표가를 반환한다."""
        try:
            str_today = self.event_loop.today
            ohlc = get_current_price(code)
            if str_today == ohlc.index.strftime('%Y-%m-%d')[-1]:
                lastdata = ohlc.iloc[-2]
                lastday = ohlc.index.strftime('%Y-%m-%d')[-2]
            else:
                lastdata = ohlc.iloc[-1]
                lastday = ohlc.index.strftime('%Y-%m-%d')[-1]
            lastday_high = lastdata[1]
            lastday_low = lastdata[2]
            sub_price = (lastday_high - lastday_low) * 0.5
            ma5 = ohlc.rolling(window=5).mean()
            ma10 = ohlc.rolling(window=10).mean()

            self.portfolio_stock_dict[code].update({"매수 목표가 중간 값": sub_price})
            self.portfolio_stock_dict[code].update({"ma5": ma5['Close'].loc[lastday]})
            self.portfolio_stock_dict[code].update({"ma10": ma10['Close'].loc[lastday]})
        except Exception as ex:
            print("`get_target_price() -> exception! " + str(ex) + "`")
