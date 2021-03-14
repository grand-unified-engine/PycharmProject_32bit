import os
from PyQt5.QtCore import QEventLoop
from PyQt5.QtTest import QTest
import pandas as pd
import datetime
from Kiwoom.KiwoomAPI import ErrorCode
# from slacker import Slacker
# from Kiwoom.config.MariaDB import MarketDB
import sys


# import numpy as np

class EventLoop:
    def __init__(self, api, real_type, logging, portfolio_stock_dict):

        self.api = api
        self.real_type = real_type
        self.logging = logging

        self.portfolio_stock_dict = portfolio_stock_dict

        self.today = datetime.datetime.today().strftime('%Y-%m-%d')

        # token = 'xoxb-1383363554548-1362462106343-PcF4KAsYG6QVSIRkAuKXyhSa'
        # self.slack = Slacker(token)

        # self.mk = MarketDB()

        ########## event loop를 실행하기 위한 변수 모음
        self.login_event_loop = QEventLoop()  # 로그인을 요청하고 안전하게 완료될 때까지 기다리게 만들기 위한 이벤트 루프 변수
        self.detail_account_info_event_loop = QEventLoop()  # 예수금 요청 이벤트 루프. sPrevNext가 2로 호출될 수 있으므로 시그널 메소드에서 인스턴스하면 안 되고 전역에서 인스턴스해야 한다.
        self.analyze_event_loop = QEventLoop()  # 분석용 signal.calculator_fuc에서 사용
        self.for_signal_event_loop = None  # 시그널에서 호출해서 반복없이 event slot에서 받을 때 시그널 함수에서 QEventLoop() 시작을 할 때 여기서 None

        self.calculator_event_loop = QEventLoop()  # tr 테스트용
        #############################################

        ########
        self.jango_dict = {}  # 실시간 잔고에 반영된 종목
        ########################

        ########## 계좌 관련된 변수
        self.account_num = None  # 계좌번호 담아줄 변수
        self.deposit = 0  # 예수금
        self.use_money = 0  # 실제 투자에 사용할 금액
        self.use_money_percent = 1  # 0.5 #예수금에서 실제 사용할 비율
        self.output_deposit = 0  # 출력가능 금액
        self.total_profit_loss_money = 0  # 총평가손익금액
        self.total_profit_loss_rate = 0.0  # 총수익률(%)
        self.account_stock_dict = {}  # 계좌평가잔고내역에서 조회된 것. 시그널을 보냈을 때 넣어줌.
        self.not_account_stock_dict = {}  # 미체결종목
        #######################################################

        ########## 요청 스크린 번호
        self.screen_my_info = "2000"  # 계좌 관련 스크린 번호 -- 이건 eventloop에서 사용하므로 여기 있어야 함.
        self.screen_analyze_stock = "4000"  # 분석용 스크린 번호 . 여기 있어야 함. signal.analyze_fuc에서 사용
        self.screen_signal_event = "3000"  # ???
        #######################################################

        ########## 종목 분석 용
        self.analyze_data = []  # 종목 분석 데이터

        self.day_candle = None  # 일봉 차트 담기
        self.real_data_dict = {}  # 분봉 차트를 만들기 위한 딕셔너리
        self.minute_candle_dict = {}  # 종목별 분봉담기 2020-10-25
        self.condition_stock = {}  # 조검검색 1차 필터링 종목 2021-03-04
        #######################################################

        ########## 변동성 돌파 전략 20.12.02
        self.bought_list = []
        self.target_buy_cnt = 5
        self.buy_percent = 0.19
        # self.t_now = datetime.datetime.now()
        # self.t_9 = self.t_now.replace(hour=9, minute=0, second=0, microsecond=0)
        # self.t_start = self.t_now.replace(hour=9, minute=5, second=0, microsecond=0)
        # self.t_sell = self.t_now.replace(hour=15, minute=15, second=0, microsecond=0)
        # self.t_exit = self.t_now.replace(hour=15, minute=20, second=0, microsecond=0)
        #######################################################

        self.test_code = None  # 시그널 재호출용
        self.req_cnt = 0  # 당일전일 체결내역 카운트용
        self.today_open = 0  # 테스트용. 실제로 매입가 가져올 수 있으므로 필요없게 되면 삭제할 것.

        # self.convergence_dict = {} #수렴 여부 딕셔너리. 거래량 급증 실시간에서 사용

        self.event_slots()  # 슬롯을 받을 이벤트 등록
        self.real_event_slots()  # 슬롯을 받을 이벤트 등록(실시간)

        self.condition_event_slot() # 슬롯을 받을 이벤트 등록(조건검색)

    def event_slots(self):
        self.api.ocx.OnEventConnect.connect(self._event_connect_slot)  # 키움 서버 접속 관련 이벤트가 발생할 경우 _connect_slot 함수 호출
        self.api.ocx.OnReceiveTrData.connect(self._tr_data_slot)  # 조회요청 응답을 받거나 조회데이터를 수신했을때 호출
        self.api.ocx.OnReceiveMsg.connect(self._msg_slot)

    def real_event_slots(self):
        self.api.ocx.OnReceiveRealData.connect(self._receive_real_data_slot)  # 실시간 이벤트 연결
        self.api.ocx.OnReceiveChejanData.connect(self._chejan_slot)  # 주문이 들어간 후 결과 데이터를 반환받는다.

    # 조건검색식 이벤트 모음
    def condition_event_slot(self):
        self.api.ocx.OnReceiveConditionVer.connect(self._condition_ver_slot)
        self.api.ocx.OnReceiveTrCondition.connect(self._condition_tr_slot)
        # self.api.ocx.OnReceiveRealCondition.connect(self._condition_real_slot)

    # 로그인 slot
    def _event_connect_slot(self, err_code):
        self.logging.logger.debug('{}'.format(ErrorCode.errors(err_code)[1]))
        # self.logging.logger.debug(f'{errors(err_code)[1]}')
        # 로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_loop.exit()

    # 어떤 조건식이 있는지 확인
    def _condition_ver_slot(self, lRet, sMsg):
        # self.logging.logger.debug("호출 성공 여부 %s, 호출결과 메시지 %s" % (lRet, sMsg))
        condition_name_list = self.api.get_condition_name_list()
        # self.logging.logger.debug("HTS의 조건검색식 이름 가져오기 %s" % condition_name_list)

        condition_name_list = condition_name_list.split(";")[:-1]

        condition_name_list = [x for x in condition_name_list if x.split("^")[1] == "자비스전달종목"]

        self.api.send_condition("0156", condition_name_list[0].split("^")[1], condition_name_list[0].split("^")[0],
                                0)  # 조회요청 + 실시간 조회

        # for unit_condition in condition_name_list:
        #     index = unit_condition.split("^")[0]
        #     index = int(index)
        #     condition_name = unit_condition.split("^")[1]
        #
        #     self.logging.logger.debug("조건식 분리 번호: %s, 이름: %s" % (index, condition_name))
        #
        #     ok = self.api.send_condition("0156", condition_name, index, 0) #조회요청 + 실시간 조회
        #     self.logging.logger.debug("조회 성공여부 %s " % ok)

    # 나의 조건식에 해당하는 종목코드 받기
    def _condition_tr_slot(self, sScrNo, strCodeList, strConditionName, index, nNext):
        # self.logging.logger.debug("화면번호: %s, 종목코드 리스트: %s, 조건식 이름: %s, 조건식 인덱스: %s, 연속조회: %s" % (sScrNo, strCodeList, strConditionName, index, nNext))

        code_list = strCodeList.split(";")[:-1]
        print("코드 종목 : {}".format(code_list))
        print("코드 개수 : {}".format(len(code_list)))

        # for code in code_list:
        #     if code not in self.portfolio_stock_dict:
        #         self.condition_stock.update({code: {}})
        # print("포트폴리오 필터링 후 코드 개수 : {}".format(len(self.condition_stock)))

        self.condition_stock.update({'189980': {}})

        self.api.set_real_remove("0156", "ALL") # 조건 검색한 종목들 실시간 스크린번호 삭제

    # 조건식 실시간으로 받기
    def _condition_real_slot(self, strCode, strType, strConditionName, strConditionIndex):
        # self.logging.logger.debug("종목코드: %s, 이벤트종류: %s, 조건식이름: %s, 조건명인덱스: %s" % (strCode, strType, strConditionName, strConditionIndex))

        if strType == "I":
            if strCode not in self.condition_stock:
                self.condition_stock.update({strCode: {}})
                self.condition_stock[strCode].update({"portfolio_stock_dict추가여부": False})
                self.logging.logger.debug("종목코드: %s, 종목편입: %s" % (strCode, strType))

        # elif strType == "D":
        #     self.logging.logger.debug("종목코드: %s, 종목이탈: %s" % (strCode, strType))

    '''
    조회요청 응답을 받거나 조회데이터를 수신했을때
    slot 안에서 tr 다시 요청하면 처리 되지 않는다!!!
    '''

    # 조회요청 응답을 받거나 조회데이터를 수신했을때
    # sTrCode : TR이름 ex)opt10075
    def _tr_data_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext, unused1, unused2, unused3, unused4):
        # from Kiwoom.Signal import Signal
        # print("OnReceiveTrData 이벤트 루프 큐 실행: ", screen_no, sRQName, sTrCode, record_name, sPrevNext)

        # if sRQName == "신규매수" or sRQName == "신규매도" or sRQName == "매수취소":
        #     try:
        #         self.api.orderLoop.exit()
        #     except AttributeError:
        #         pass
        # 주문번호와 주문루프
        # self.orderNo = self.api.get_comm_data(sTrCode, "", sRQName, 0, "주문번호")
        #
        # try:
        #     self.api.orderLoop.exit()
        # except AttributeError:
        #     pass
        # print("sRQName : {}".format(sRQName))
        if sRQName == "예수금상세현황요청":  # opw00001 : 예수금상세현황요청 (single, multi)
            deposit = self.api.get_comm_data(sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            # print("예수금 : {}".format(self.deposit))
            # print("실제 사용할 비율 : {}".format(self.use_money_percent))
            use_money = float(self.deposit) * self.use_money_percent  # 예수금 * 실제 사용할 비율
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4  # 5종목 이상 매수할 수 있게 5로 나눠준다. 이 뜻이 아닌데?

            # print("실제 사용할 금액 : {}".format(self.use_money))

            output_deposit = self.api.get_comm_data(sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            # self.logging.logger.debug("출금가능금액 : %s" % self.output_deposit)

            self.api.disconnect_real_data(self.screen_my_info)  # 예수금 스크린 번호 연결 끊기

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":  # opw00018 : 계좌평가잔고내역요청

            total_buy_money = self.api.get_comm_data(sTrCode, sRQName, 0, "총매입금액").lstrip("0")
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.api.get_comm_data(sTrCode, sRQName, 0, "총평가손익금액").lstrip("0")
            if total_profit_loss_money[0] == "-":
                total_profit_loss_money = "-" + total_profit_loss_money[1:].lstrip("0")
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.api.get_comm_data(sTrCode, sRQName, 0, "총수익률(%)").lstrip("0")
            if total_profit_loss_rate[0] == "-":
                total_profit_loss_rate = "-" + total_profit_loss_rate[1:].lstrip("0")
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            self.logging.logger.debug(
                "계좌평가잔고내역요청 싱글데이터 : 총매입금액 {}, 총평가손익금액 {}, 총수익률(%) {}".format(total_buy_money, total_profit_loss_money,
                                                                             total_profit_loss_rate))

            rows = self.api.get_repeat_cnt(sTrCode, sRQName)  # 시그널 보냈을 때 반환된 데이터 갯수
            for i in range(rows):
                code = self.api.get_comm_data(sTrCode, sRQName, i,
                                              "종목번호")  # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]
                code_nm = self.api.get_comm_data(sTrCode, sRQName, i, "종목명").rstrip()  # 출럭 : 한국기업평가
                stock_quantity = self.api.get_comm_data(sTrCode, sRQName, i, "보유수량").lstrip(
                    "0")  # 보유수량 : 000000000000010
                buy_price = self.api.get_comm_data(sTrCode, sRQName, i, "매입가").lstrip("0")  # 매입가 : 000000000054100
                learn_rate = self.api.get_comm_data(sTrCode, sRQName, i, "수익률(%)").lstrip("0")  # 수익률 : -000000001.94
                if learn_rate[0] == "-":
                    learn_rate = "-" + learn_rate[1:].lstrip("0")
                current_price = self.api.get_comm_data(sTrCode, sRQName, i, "현재가").lstrip("0")  # 현재가 : 000000003450
                total_chegual_price = self.api.get_comm_data(sTrCode, sRQName, i, "매입금액").lstrip("0")
                possible_quantity = self.api.get_comm_data(sTrCode, sRQName, i, "매매가능수량").lstrip("0")
                d1_close = self.api.get_comm_data(sTrCode, sRQName, i, "전일종가").lstrip("0")

                self.logging.logger.debug("종목코드: {} - 종목명: {} - 보유수량: {} - 매입가: {} - 수익률: {} - 현재가: {}".format(
                    code, code_nm, stock_quantity, buy_price, learn_rate, current_price))

                if code in self.account_stock_dict:  # dictionary 에 해당 종목이 있나 확인
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())
                d1_close = int(d1_close.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량': possible_quantity})
                self.account_stock_dict[code].update({'당일상한가': d1_close * 1.298})

            # self.logging.logger.debug("sPreNext : %s" % next)
            print("계좌에 가지고 있는 종목은 %s " % rows)

            if sPrevNext == "2":
                # Signal.detail_account_mystock(sPrevNext=sPrevNext)
                self.api.set_input_value("계좌번호", self.account_num)
                self.api.set_input_value("비밀번호", "8374")
                self.api.set_input_value("비밀번호입력매체구분", "00")
                self.api.set_input_value("조회구분", "1")

                self.api.comm_rq_data("계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
                self.detail_account_info_event_loop.exec_()
            else:
                self.detail_account_info_event_loop.exit()


        elif sRQName == "주식일봉차트조회":  # opt10081 : 주식일봉차트조회
            # ex_data = self.api.get_comm_data_ex(sTrCode, "주식일봉차트조회")
            # print("ex_data : {}".format(ex_data))
            # colName = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가',
            #            '저가', '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']
            # df = pd.DataFrame(ex_data, columns=colName)
            # df.index = pd.to_datetime(df['일자'])
            # df = df[['현재가', '거래량', '시가', '고가', '저가', '거래대금']]
            # df[['현재가', '거래량', '시가', '고가', '저가', '거래대금']] = df[
            #     ['현재가', '거래량', '시가', '고가', '저가', '거래대금']].astype(int)
            # # df는 현재에서 과거로, final_df는 과거에서 현재로 - 이평선 컬럼 만들기 위해
            # final_df = df.sort_index()
            # print("final_df : {}".format(final_df))
            # ma3 = final_df['close'].rolling(window=3).mean()
            # ma5 = final_df['close'].rolling(window=5).mean()
            # ma10 = final_df['close'].rolling(window=10).mean()
            # ma20 = final_df['close'].rolling(window=20).mean()
            # ma60 = final_df['close'].rolling(window=60).mean()
            # ma120 = final_df['close'].rolling(window=120).mean()
            # if sCode not in self.portfolio_stock_dict:
            #     self.portfolio_stock_dict.update({sCode: {}})
            # self.day_candle = final_df
            code = self.api.get_comm_data(sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            cnt = self.api.get_repeat_cnt(sTrCode, sRQName)

            for i in range(cnt):
                data = []
                current_price = self.api.get_comm_data(sTrCode, sRQName, i, "현재가")
                value = self.api.get_comm_data(sTrCode, sRQName, i, "거래량")
                trading_value = self.api.get_comm_data(sTrCode, sRQName, i, "거래대금")
                date = self.api.get_comm_data(sTrCode, sRQName, i, "일자")
                start_price = self.api.get_comm_data(sTrCode, sRQName, i, "시가")
                high_price = self.api.get_comm_data(sTrCode, sRQName, i, "고가")
                low_price = self.api.get_comm_data(sTrCode, sRQName, i, "저가")

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.analyze_data.append(data.copy())

            if sPrevNext == "2":
                Signal.day_candle_req(code=code, sPrevNext=sPrevNext)
            else:
                pass_success = False

                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.analyze_data == None or len(self.analyze_data) < 120:
                    pass_success = False
                else:
                    # 120일 이평선의 최근 가격 구함
                    total_price = 0
                    for value in self.analyze_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.analyze_data[0][7]) <= moving_average_price and moving_average_price <= int(
                            self.analyze_data[0][6]):
                        print("오늘의 주가가 120 이평선에 걸쳐있는지 확인")
                        bottom_stock_price = True
                        check_price = int(self.analyze_data[0][6])

                    # 과거 일봉 데이터를 조회하면서 120일 이동평균선보다 주가가 계속 밑에 존재하는지 확인
                    prev_price = None
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0  # 120일 이평선의 가격
                        price_top_moving = False  # 아래 조건문이 모두 통과하면 True
                        idx = 1

                        while True:
                            if len(self.analyze_data[idx:]) < 120:  # 120일 치가 있는지 계속 확인
                                print("120일 치가 없음")
                                break

                            total_price = 0
                            for value in self.analyze_data[idx:120 + idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.analyze_data[idx][6]) and idx <= 20:
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못 함")
                                price_top_moving = False
                                break

                            elif int(self.analyze_data[idx][
                                         7]) > moving_average_price_prev and idx > 20:  # 120일 이평선 위에 있는 구간 존재
                                print("120일치 이평선 위에 있는 구간 확인됨")
                                price_top_moving = True
                                prev_price = int(self.analyze_data[idx][7])
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

                    code_nm = self.api.get_master_code_name(code)

                    f = open("files/condition_stock.txt", "a",
                             encoding="utf8")  # a는 기존 파일에 이어서 쓰는 옵션, w는 이전 데이터를 모두 지우고 새로 쓰는 옵션
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.analyze_data[0][1])))  # \t는 TAB, \n은 엔터
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못 함")

                self.analyze_data.clear()
                self.analyze_event_loop.exit()


        elif sRQName == "주식기본정보요청":  # opt10003 : 체결정보요청 (single, multi)

            code = self.api.get_comm_data(sTrCode, sRQName, 0, "종목코드")
            code = code.strip()

            open = self.api.get_comm_data(sTrCode, sRQName, 0, "시가")
            # self.today_open = int(open)

            par_value = self.api.get_comm_data(sTrCode, sRQName, 0, "액면가")
            par_value = int(par_value)

            tr_total_cnt = self.api.get_comm_data(sTrCode, sRQName, 0, "상장주식")
            tr_total_cnt = int(tr_total_cnt)

            real_tr_stock_cnt = self.api.get_comm_data(sTrCode, sRQName, 0,
                                                       "유통주식")  # 리턴값이 string이므로 1000을 곱하면 1000번 출력된다.
            real_tr_stock_cnt = real_tr_stock_cnt.strip()
            # real_tr_stock_cnt.zfill(20)

            # print("상장주식 : {}".format(tr_total_cnt))

            # 우선주는 유통주식수가 없다. ETF도 없다. 그래서 상장수로 업데이트
            # 유통주식수가 없는건 None이 아니라 빈칸 20자리가 들어가 있다;;;;
            if real_tr_stock_cnt != '':
                ''' 회사정보 테이블에 유통주식 수 업데이트'''
                with self.mk.conn.cursor() as curs:
                    sql = "UPDATE company_info set real_tr_stock_cnt = {} where code = '{}' " \
                        .format(int(real_tr_stock_cnt) * 1000, code)
                    print(sql)
                    curs.execute(sql)
                    self.mk.conn.commit()
            else:
                with self.mk.conn.cursor() as curs:
                    sql = "UPDATE company_info set real_tr_stock_cnt = {} where code = '{}' " \
                        .format(tr_total_cnt * 1000, code)
                    print(sql)
                    curs.execute(sql)
                    self.mk.conn.commit()

            print("code 111: {}".format(code))
            # if real_tr_stock_cnt == None: # 유통주식수 값이 없는게 있다니;;;
            #     real_tr_stock_cnt = 0
            # else:
            #     real_tr_stock_cnt = int(real_tr_stock_cnt) * 1000
            # # real_tr_stock_cnt = int(real_tr_stock_cnt.lstrip("0"))
            # print("real_tr_stock_cnt 222: {}".format(real_tr_stock_cnt))
            # print(len(real_tr_stock_cnt))

            # if real_tr_stock_cnt.strip(' ') == '':
            #     print("true")
            # else:
            #     print("false")

            # if real_tr_stock_cnt[-1] != ' ':  # 유통주식수 값이 없는게 있다니;;;
            #     ''' 회사정보 테이블에 유통주식 수 업데이트'''
            #     with self.mk.conn.cursor() as curs:
            #         sql = "UPDATE company_info set real_tr_stock_cnt = {} where code = '{}' "\
            #             .format(int(real_tr_stock_cnt) * 1000, code)
            #         print(sql)
            #         curs.execute(sql)
            #         self.mk.conn.commit()

            # print("open : {}".format(self.today_open))
            # high_price = self.api.get_comm_data(sTrCode, sRQName, 0, "상한가")
            # low_price = self.api.get_comm_data(sTrCode, sRQName, 0, "하한가")
            # buyable_stock_cnt = self.api.get_comm_data(sTrCode, sRQName, 0, "유통주식")
            # buyable_stock_cnt = int(buyable_stock_cnt) * 1000
            # buyable_stock_rate = self.api.get_comm_data(sTrCode, sRQName, 0, "유통비율")
            # print("상한가 : {}, 하한가 : {}, 유통주식 : {}, 유통비율 : {}".format(high_price, low_price, buyable_stock_cnt, buyable_stock_rate))
            '''            
            전일 종가보다 30% 오르면 상한가
            '''
            self.for_signal_event_loop.exit()

        elif sRQName == "실시간미체결요청":  # sTrCode : opt10075
            rows = self.api.get_repeat_cnt(sTrCode, sRQName)

            for i in range(rows):

                code = self.api.get_comm_data(sTrCode, sRQName, i, "종목코드")
                code_nm = self.api.get_comm_data(sTrCode, sRQName, i, "종목명")
                order_no = self.api.get_comm_data(sTrCode, sRQName, i, "주문번호")
                order_status = self.api.get_comm_data(sTrCode, sRQName, i, "주문상태")  # 접수,확인,체결
                order_quantity = self.api.get_comm_data(sTrCode, sRQName, i, "주문수량")
                order_price = self.api.get_comm_data(sTrCode, sRQName, i, "주문가격")
                order_gubun = self.api.get_comm_data(sTrCode, sRQName, i, "주문구분")  # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.api.get_comm_data(sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.api.get_comm_data(sTrCode, sRQName, i, "체결량")

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

                self.logging.logger.debug("미체결 종목 : %s " % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()


        elif sRQName == "주식주봉차트조회":  # opt10082 : 주식주봉차트조회요청

            ex_data = self.api.get_comm_data_ex(sTrCode, "주식주봉차트조회")

            # print("ex_data : {}".format(len(ex_data)))

            print("self.test_code : {}".format(self.test_code))
            i = ex_data[0]  # 이번주꺼
            with self.mk.conn.cursor() as curs:
                sql = "REPLACE INTO week_price VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                    self.test_code, i[3], i[4], i[5], i[6], i[0], i[1], i[2])
                curs.execute(sql)
                self.mk.conn.commit()
            #
            # for i in ex_data:
            #     with self.mk.conn.cursor() as curs:
            #         sql = "REPLACE INTO week_price VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.test_code, i[3], i[4], i[5], i[6], i[0], i[1], i[2])
            #         curs.execute(sql)
            #         self.mk.conn.commit()

            # colName = ['close', 'volumn', 'date', 'open', 'high', 'low',
            #            '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']
            #
            # df = pd.DataFrame(ex_data, columns=colName)
            #
            # df.index = pd.to_datetime(df.date)
            #
            # df = df[['close', 'volumn', 'open', 'high', 'low']]
            #
            # df[['close', 'volumn', 'open', 'high', 'low']] = df[
            #     ['close', 'volumn', 'open', 'high', 'low']].astype(int)
            #
            # # df는 현재에서 과거로, final_df는 과거에서 현재로 - 이평선 컬럼 만들기 위해
            # final_df = df.sort_index()
            #
            # final_df['MA5'] = final_df['close'].rolling(window=5).mean()
            # final_df['MA10'] = final_df['close'].rolling(window=10).mean()
            # final_df['MA20'] = final_df['close'].rolling(window=20).mean()
            # final_df['MA60'] = final_df['close'].rolling(window=60).mean()
            #
            # final_df = final_df[final_df.index.strftime('%Y-%m-%d %H:%M') == datetime.today().strftime('%Y-%m-%d %H:%M')]
            self.calculator_event_loop.exit()


        elif sRQName == "주식분봉차트조회":  # opt10080 : 주식분봉차트조회요청 (single, multi)

            print("주식분봉차트조회 slot, test_code : {}".format(self.test_code))
            # print("self.test_code : {}".format(self.test_code))

            ex_data = self.api.get_comm_data_ex(sTrCode, sRQName)
            # print("ex_data : {}".format(ex_data))

            self._opt10080_test(ex_data)

            self.calculator_event_loop.exit()

        elif sRQName == "호가잔량상위요청":  # OPT10020 : 호가잔량상위요청

            # 여기 있으면 실시간 안 넘어감 OK
            self.api.disconnect_real_data(self.screen_calculation_stock)

            ex_data = self.api.get_comm_data_ex(sTrCode, sRQName)

            print("ex_data : {}".format(ex_data))

            # self.gathering_money_stock = ex_data

            # print("self.volume_uprise : {}".format(self.volume_uprise))

            # colName = ['종목코드', '종목명', '현재가', '등락기호', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']
            #
            # df = pd.DataFrame(ex_data, columns=colName)
            #
            # df.index = df['종목코드'] <-- 이거 해결방법 찾아야 함
            #
            # df = df[['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']]
            #
            # df[['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']] = df[
            #     ['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']].astype(int)
            #
            # df = df.drop(df[df['등락률'] < 0].index)  # 096350(대창솔루션) 모의투자 매매 불가능
            #
            # print("df : {}".format(df))

            # with self.mk.conn.cursor() as curs:
            #     sql = "DELETE FROM vol_uprise_stock" # 다 지워버려. 다시 등록한 종목 실시간 등록하므로
            #     curs.execute(sql)
            #     self.mk.conn.commit()

            # for data in top_data:
            #
            #     seq = self.mk.get_buy_stock_info_max_seq(data, datetime.today().strftime('%Y-%m-%d'))
            #
            #     df = self.mk.get_buy_stock_info(data, datetime.today().strftime('%Y-%m-%d'), seq, '매수')
            #
            #     with self.mk.conn.cursor() as curs:
            #         if len(df) == 0: # 매수하지 않은 종목
            #             sql = "REPLACE INTO vol_uprise_stock VALUES ('{}')".format(data)
            #             curs.execute(sql)
            #             self.mk.conn.commit()

            self.for_signal_event_loop.exit()

        elif sRQName == "거래량급증요청":  # OPT10023 : 거래량급증요청

            # 여기 있으면 실시간 안 넘어감 OK
            # self.api.set_real_remove("2222", "ALL")  # opt10023 : 거래량급증요청 호출해서 등록된 거 삭제
            self.api.disconnect_real_data(self.screen_calculation_stock)

            ex_data = self.api.get_comm_data_ex(sTrCode, "거래량급증요청")

            # print("ex_data : {}".format(ex_data))

            self.gathering_money_stock = ex_data

            # print("self.volume_uprise : {}".format(self.volume_uprise))

            # colName = ['종목코드', '종목명', '현재가', '등락기호', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']
            #
            # df = pd.DataFrame(ex_data, columns=colName)
            #
            # df.index = df['종목코드'] <-- 이거 해결방법 찾아야 함
            #
            # df = df[['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']]
            #
            # df[['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']] = df[
            #     ['현재가', '전일대비', '등락률', '전일', '당일', '급증량', '급증률']].astype(int)
            #
            # df = df.drop(df[df['등락률'] < 0].index)  # 096350(대창솔루션) 모의투자 매매 불가능
            #
            # print("df : {}".format(df))

            # with self.mk.conn.cursor() as curs:
            #     sql = "DELETE FROM vol_uprise_stock" # 다 지워버려. 다시 등록한 종목 실시간 등록하므로
            #     curs.execute(sql)
            #     self.mk.conn.commit()

            # for data in top_data:
            #
            #     seq = self.mk.get_buy_stock_info_max_seq(data, datetime.today().strftime('%Y-%m-%d'))
            #
            #     df = self.mk.get_buy_stock_info(data, datetime.today().strftime('%Y-%m-%d'), seq, '매수')
            #
            #     with self.mk.conn.cursor() as curs:
            #         if len(df) == 0: # 매수하지 않은 종목
            #             sql = "REPLACE INTO vol_uprise_stock VALUES ('{}')".format(data)
            #             curs.execute(sql)
            #             self.mk.conn.commit()

            self.for_signal_event_loop.exit()



        elif sRQName == "전일대비등락률상위요청":  # opt10027 : 전일대비등락률상위요청

            ex_data = self.api.get_comm_data_ex(sTrCode, "전일대비등락률상위요청")

            # print("ex_data : {}".format(ex_data))

            colName = ['종목분류', '종목코드', '종목명', '현재가', '전일대비기호', '전일대비',
                       '등락률', '매도잔량', '매수잔량', '현재거래량', '체결강도', '횟수']

            df = pd.DataFrame(ex_data, columns=colName)
            # print("df : {}".format(df))

            code_list = list(df['종목코드'])

            print("code_list : {}".format(code_list))

            #
            # df.index = pd.to_datetime(df.date)
            #
            # df = df[['close', 'volumn', 'open', 'high', 'low']]
            #
            # df[['close', 'volumn', 'open', 'high', 'low']] = df[
            #     ['close', 'volumn', 'open', 'high', 'low']].astype(int)
            #
            # # df는 현재에서 과거로, final_df는 과거에서 현재로 - 이평선 컬럼 만들기 위해
            # final_df = df.sort_index()
            #
            # final_df['MA5'] = final_df['close'].rolling(window=5).mean()
            # final_df['MA10'] = final_df['close'].rolling(window=10).mean()
            # final_df['MA20'] = final_df['close'].rolling(window=20).mean()
            # final_df['MA60'] = final_df['close'].rolling(window=60).mean()
            #
            # final_df = final_df[final_df.index.strftime('%Y-%m-%d %H:%M') == datetime.today().strftime('%Y-%m-%d %H:%M')]
            #
            # # 10% 못 먹었을 때만 적용
            # self.right_now_sell = False
            #
            # ''' 기울기 로직 추가할 것'''
            # # if final_df['MA5'].iloc[-1] > final_df['MA10'].iloc[-1] > final_df['MA20'].iloc[-1]:
            # #     self.right_now_sell = False
            # # else:
            # #     if final_df['MA20'].iloc[-1] > final_df['MA60'].iloc[-1]:
            # #         self.right_now_sell = False
            # #     else:
            # #         self.right_now_sell = True
            #
            # print("right_now_sell : {}".format(self.right_now_sell))

        elif sRQName == "당일전일체결요청":

            cnt = self.api.get_repeat_cnt(sTrCode, sRQName)

            for i in range(cnt):
                data = []
                a = self.api.get_comm_data(sTrCode, sRQName, i, "시간")
                b = self.api.get_comm_data(sTrCode, sRQName, i, "현재가")
                c = self.api.get_comm_data(sTrCode, sRQName, i, "전일대비")
                d = self.api.get_comm_data(sTrCode, sRQName, i, "대비율")
                e = self.api.get_comm_data(sTrCode, sRQName, i, "우선매도호가단위")
                f = self.api.get_comm_data(sTrCode, sRQName, i, "우선매수호가단위")
                g = self.api.get_comm_data(sTrCode, sRQName, i, "체결거래량")
                h = self.api.get_comm_data(sTrCode, sRQName, i, "sign")
                i = self.api.get_comm_data(sTrCode, sRQName, i, "누적거래량")
                # j = self.api.get_comm_data(sTrCode, sRQName, i, "누적거래대금")
                # k = self.api.get_comm_data(sTrCode, sRQName, i, "체결강도")

                data.append(a.strip())
                data.append(b.strip())
                data.append(c.strip())
                data.append(d.strip())
                data.append(e.strip())
                data.append(f.strip())
                data.append(g.strip())
                data.append(h.strip())
                data.append(i.strip())
                # data.append(j.strip())
                # data.append(k.strip())

                self.calcul_data.append(data.copy())

            if sPrevNext == "2":
                # self.screen_calculation_stock += 1
                self.sign_volume_req(code=self.test_code, sPrevNext=sPrevNext)
            else:
                print("calcul_data %s" % self.calcul_data)

                for idx, sign_list in enumerate(self.calcul_data):
                    # if int(sign_list[7]) < -500:
                    print("시간 : {}, 현재가 : {}, 전일대비 : {}, 대비율 : {}, 우선매도호가단위: {}, 우선매수호가단위: {}, 체결거래량 : {}" \
                          .format(sign_list[1], sign_list[2], sign_list[3], sign_list[4], sign_list[5], sign_list[6],
                                  sign_list[7]))
                # print(sign_list)
                #         # print("시간 : {}, 현재가 : {}, 거래량 : {}, 체결강도 : {}".format(sign_list[1], sign_list[2], sign_list[3], sign_list[4]))
                #         # if int(sign_list[2]) >= self.today_open * 1.095:
                #         #     print("시간 : {}, 현재가 : {}".format(sign_list[1], sign_list[2]))

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

        elif sRQName == "신고저가요청":  # OPT10016 : 신고저가요청

            # 여기 있으면 실시간 안 넘어감 OK
            # self.api.set_real_remove("2222", "ALL")  # opt10023 : 거래량급증요청 호출해서 등록된 거 삭제
            # self.api.disconnect_real_data(self.screen_calculation_stock)

            ex_data = self.api.get_comm_data_ex(sTrCode, "신고저가요청")

            # colName = ['종목코드', '종목명', '현재가', '전일대비기호', '전일대비', '등락률', '거래량', '전일거래량대비율', '매도호가', '매수호가', '고가', '저가']
            #
            # df = pd.DataFrame(ex_data, columns=colName)
            #
            print("ex_data : {}".format(ex_data))

            # self.gathering_money_stock = ex_data

            self.calculator_event_loop.exit()

    # 당일전일 체결내역
    def sign_volume_req(self, code=None, sPrevNext="0"):  #
        QTest.qWait(300)

        # print("self.req_cnt %s" % self.req_cnt)

        self.req_cnt += 1

        # print("sign_volume_req code : {}".format(code))
        self.test_code = code

        if self.req_cnt > 20:
            print("calcul_data %s" % self.calcul_data)

            # rev_calcul_data = reversed(self.calcul_data)

            # for idx, sign_list in enumerate(reversed(self.calcul_data)): # for문에 rev_calcul_data 쓰면 안된다!!!!!!
            #     # if int(sign_list[7]) < -500:
            #     print("시간 : {}, 현재가 : {}, 전일대비 : {}, 대비율 : {}, 우선매도호가단위: {}, 우선매수호가단위: {}, 체결거래량 : {}" \
            #           .format(sign_list[0], sign_list[1], sign_list[2], sign_list[3], sign_list[4], sign_list[5],
            #                   sign_list[6]))

            # 분봉
            # minute_candle_dict = {}
            # temp_list = []
            # for sign_list in reversed(self.calcul_data):
            #     # print("sign_list %s" % sign_list[0][:-2])
            #     temp_list.append(sign_list[0][:-2])
            #
            # # print("temp_list : {}".format(temp_list))
            #
            # # date_list = list(set(temp_list)) # 오류
            #
            # for minute in list(set(temp_list)):
            #     minute_candle_dict.update({minute: {}})
            #
            # for minute in list(set(temp_list)):
            #     volume = 0
            #     close = 0
            #     cnt_by_minute = 0
            #     real_cnt = 0
            #     for sign_list in reversed(self.calcul_data):
            #         if minute == sign_list[0][:-2]:
            #             cnt_by_minute += 1
            #
            #     for sign_list in reversed(self.calcul_data):
            #
            #         if minute == sign_list[0][:-2]:
            #             volume = volume + abs(int(sign_list[6]))
            #             real_cnt += 1
            #             if real_cnt == cnt_by_minute:
            #                 close = abs(int(sign_list[1]))
            #
            #     # groupby 사용
            #     # # “Year” 열로 데이터를 묶고자 한다.
            #     # alco_noidx = alco.reset_index()
            #     # sum_alco = alco_noidx.groupby("Year").sum()
            #     # sum_alco.tail()
            #
            #         # if int(sign_list[7]) < -500:
            #         # print("시간 : {}, 현재가 : {}, 전일대비 : {}, 대비율 : {}, 우선매도호가단위: {}, 우선매수호가단위: {}, 체결거래량 : {}" \
            #         #       .format(sign_list[0], sign_list[1], sign_list[2], sign_list[3], sign_list[4], sign_list[5],
            #         #               sign_list[6]))
            #
            #     minute_candle_dict[minute].update({"volume": volume})
            #     minute_candle_dict[minute].update({"close": close})

            # print("minute_candle_dict : {}".format(minute_candle_dict))
            # print("minute_candle_dict length: {}".format(len(minute_candle_dict)))

            #
            #
            # df = pd.DataFrame(minute_candle_dict)
            # df = df.T
            #
            # df['ma3'] = df['close'].rolling(window=3).mean()
            # df['ma3_dpc'] = (df['ma3'] / df['ma3'].shift(1) - 1) * 100
            # df['ma5'] = df['close'].rolling(window=5).mean()
            # df['ma5_dpc'] = (df['ma5'] / df['ma5'].shift(1) - 1) * 100
            # df['ma10'] = df['close'].rolling(window=10).mean()
            # df['ma20'] = df['close'].rolling(window=20).mean()
            # df['ma20_dpc'] = (df['ma20'] / df['ma20'].shift(1) - 1) * 100
            # df['ma3v'] = df['volume'].rolling(window=3).mean()
            # df['ma3v_dpc'] = (df['ma3v'] / df['ma3v'].shift(1) - 1) * 100
            #
            # print("df : {}".format(df))
            #
            # df_sec = pd.DataFrame(second_candle_dict)
            # df_sec = df_sec.T
            #
            # df_sec['ma20'] = df_sec['close'].rolling(window=20).mean()
            # df_sec['ma20_dpc'] = (df_sec['ma20'] / df_sec['ma20'].shift(1) - 1) * 100
            # df_sec['ma3v'] = df_sec['volume'].rolling(window=3).mean()
            # df_sec['ma3v_dpc'] = (df_sec['ma3v'] / df_sec['ma3v'].shift(1) - 1) * 100
            #
            # # if 8% 먹으면 매도:
            # # elif 8% 이하:
            #
            # print("ma3_dpc : {}".format(df['ma3_dpc'][-1]))
            #
            # if df['ma20_dpc'][-2] > 0: # 20일선 상승하다가
            #     if df['open'][-4] > df['close'][-4] and df['open'][-3] > df['close'][-3] and df['open'][-2] > df['close'][-2]: #3분 연속 음봉봉
            #         if df['ma3v_dpc'][-2] > 0: #거래량까지 실리면
            #             if df['ma20'][-2] > df['close'][-2]:
            #                 self.slack.chat.post_message("hellojarvis", "매도 타이밍인지 확인")
            #     # i = 0
            #     # if df2['ma20_dpc'][-1] < 0: # 20일 변곡점
            #     #     if i == 0:
            #     #         print("매도 확인")
            #     #     i += 1
            #     # if df2['ma20_dpc'][-1] > 0:  # 20일 변곡점
            #     #     if i == 0:
            #     #         print("상승 확인")
            #     #     i += 1
            #     # if df2['volume'][-2] > df2['volume'][-1] * 10:
            #     #     print("세력이 팔 때가 왔다")
            #
            #     # if (df2['ma3v_dpc'][-4] > 300 or df2['ma3v_dpc'][-3] > 300):
            #     #     print("1 : {}".format(df2['ma3v_dpc'][-4]))
            #     #     print("2 : {}".format(df2['ma3v_dpc'][-3]))
            #     print("3 : {}".format(df.index[-1]))
            #     print("세력이 팔 때가 왔다. 분봉 차트 확인")
            #     for row in df_sec.itertuples():
            #         if df.index[-1] == row[0][:-2]:
            #             print("날짜 : {}, 종가: {}, 거래량: {}, ma20: {}, ma20_dpc {}, ma3v 3: {}, ma3v_dpc {}, ".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

            # print("df2_sec : {}".format(df2_sec))

            self.calculator_event_loop.exit()
        else:

            self.api.set_input_value("종목코드", code)
            self.api.set_input_value("당일전일", '1')  # 당일 : 1, 전일 : 2
            self.api.set_input_value("틱분", '0')  # 틱 : 0 , 분 : 1
            self.api.set_input_value("시간", '1508')

            self.api.comm_rq_data("당일전일체결요청", "opt10084", sPrevNext, self.screen_calculation_stock)

            # self.calculator_event_loop = QEventLoop()
            self.calculator_event_loop.exec_()

    '''
    실시간 slot
    '''

    def _receive_real_data_slot(self, sCode, sRealType, sRealData):
        # from Kiwoom.Signal import Signal
        if sRealType == "장시작시간":
            fid = self.real_type.REALTYPE[sRealType][
                '장운영구분']  # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감(시간외종료), a:시간외종가매매 시작, b:시간외종가매매 종료)
            value = self.api.get_comm_real_data(sCode, fid)

            if value == '0':
                # 8시 40분부터 1분마다 신호 보내줌
                self.logging.logger.debug("장 시작 전")

            elif value == '3':
                self.logging.logger.debug("장 시작")
                # self.slack.chat.post_message("hellojarvis", self.today + "장 시작했습니다.")

            elif value == "2":
                # 3시 20분부터 1분마다 신호 보내줌
                self.logging.logger.debug("장 종료, 동시호가로 넘어감")

            elif value == "4":
                self.logging.logger.debug("3시30분 장 종료")
                # self.slack.chat.post_message("hellojarvis", self.today + "장 종료됐습니다.")

                for code in self.portfolio_stock_dict.keys():
                    self.api.set_real_remove(self.portfolio_stock_dict[code]['스크린번호'], code)

                sys.exit()
        elif sRealType == "주식호가잔량":  # 초단위
            hoga_time = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['호가시간'])  # 출력 HHMMSS

            a = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매도호가총잔량'])
            a = int(a)

            b = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매수호가총잔량'])
            b = int(b)

            c = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['순매수잔량'])
            c = int(c)

            d = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매도호가1'])
            d = int(d)

            # e = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매도호가수량1'])
            # e = int(e)

            f = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매도호가직전대비1'])
            f = int(f)

            g = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매수호가1'])
            g = int(g)

            h = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매수호가수량1'])
            h = int(h)

            i = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['매수호가직전대비1'])
            i = int(i)

            # if sCode in self.portfolio_stock_dict:
            #     if self.portfolio_stock_dict[sCode]["매수매도"] == "매도":
            #         # c_list = self.portfolio_stock_dict[sCode]["순매수리스트"]
            #         d_list = self.portfolio_stock_dict[sCode]["매도우선호가리스트"]
            #
            #         if len(d_list) == 2:
            #             if 1000 < d <= 4000: # 매도호가1
            #                 if d <= d_list[-1] - 50: # 매도호가가 확 내려갔을 때
            #                     if c > 0: # 순매수가 +이면
            #                         self.logging.logger.debug("매도 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                         self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #             elif 4000 < d <= 10000:
            #                 if d <= d_list[-1] - 150: # 매도호가가 확 내려갔을 때
            #                     if c > 0: # 순매수가 +이면
            #                         self.logging.logger.debug(
            #                             "매도 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                         self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #             elif 10000 < d <= 50000:
            #                 if d <= d_list[-1] -300: # 매도호가가 확 내려갔을 때
            #                     if c > 0: # 순매수가 +이면
            #                         self.logging.logger.debug(
            #                             "매도 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                         self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #             d_list.pop(0)
            #         d_list.append(d)

            # if len(c_list) == 10:
            #     if len([z for z in c_list if z > 0]) == 0: # 연속 10개 총매수가 더 많다가 (계속 상승하다가)
            #         if c > 0: # 총매수수량이 많아지면 추세전환으로 봄
            #             self.logging.logger.debug("종목코드 : {}, 총매수량 증가 시간 : {}".format(sCode, hoga_time))
            #             self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #     # if c < 0:
            #     #     if c_list[-1] - 100000 > c: # 예) 전꺼 -3,879, 지금 들어온 c : -117,305
            #     #         self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #     c_list.pop(0)
            # c_list.append(c)

            # if self.portfolio_stock_dict[sCode]["매수매도"] == "매수":
            #     # c_list = self.portfolio_stock_dict[sCode]["순매수리스트"]
            #     d_list = self.portfolio_stock_dict[sCode]["매도우선호가리스트"]
            #     f_list = self.portfolio_stock_dict[sCode]["매도호가직전대비1"]
            #
            #     if len(d_list) == 2:
            #         if 1000 < d <= 4000: # 매도호가1
            #             if d >= d_list[-1] + 20: # 매도호가가 20원 오를 때
            #                 if c < 0: # 순매수가 -이면
            #                     if f < 0: # 매도호가직전대비1이 -이면
            #                         self.logging.logger.debug(
            #                             "매수 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                         self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #         elif 4000 < d <= 10000:
            #             if d >= d_list[-1] + 100: # 매도호가가 100원 오를 때
            #                 if c > 0: # 순매수가 +이면
            #                     self.logging.logger.debug(
            #                         "매수 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                     self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #         elif 10000 < d <= 50000:
            #             if d >= d_list[-1] + 200: # 매도호가가 200원 오를 때
            #                 if c > 0: # 순매수가 +이면
            #                     self.logging.logger.debug(
            #                         "매수 종목코드 : {}, 매도호가 : {}, 시간 : {}".format(sCode, d, hoga_time))
            #                     self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #         d_list.pop(0)
            #         f_list.pop(0)
            #     d_list.append(d)
            #     f_list.append(f)

            # if len(c_list) == 10:
            #     if len([z for z in c_list if z < 0]) == 0: # 연속 10개 총매수가 더 많다가 (계속 하락하다가)
            #         if c < 0: # 총매도량이 많아지면 추세전환으로 봄
            #             self.logging.logger.debug("매수 종목코드 : {}, 총매도량 증가 시간 1 : {}".format(sCode, hoga_time))
            #             self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #
            #     if c < 0:
            #         if c_list[-1] - 100000 > c: # 예) 전꺼 -3,879, 지금 들어온 c : -117,305
            #             self.logging.logger.debug("매수 종목코드 : {}, 총매도량 증가 시간 2: {}".format(sCode, hoga_time))
            #             self.portfolio_stock_dict[sCode].update({"전환점여부": True})
            #     c_list.pop(0)
            # c_list.append(c)





        elif sRealType == "주식체결":  # 틱단위
            # self.api.set_real_remove("0168", "ALL") # opt10023 : 거래량급증요청 호출해서 등록된 거 삭제
            # self.api.set_real_remove(self.screen_calculation_stock, sCode)  # 주식분봉차트조회 opt10080 호출해서 등록된 거 삭제

            a = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['체결시간'])  # 출력 HHMMSS

            b = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['현재가'])  # 출력 : +(-)2520
            b = abs(int(b))

            c = self.api.get_comm_real_data(sCode,
                                            self.real_type.REALTYPE[sRealType]['전일대비'])  # 출력 : +(-)2520 전일 대비 현재 가격의 차액
            c = int(c)

            d = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['등락율'])  # 출력 : +(-)12.98 전날 종가 대비
            d = float(d)

            e = self.api.get_comm_real_data(sCode,
                                            self.real_type.REALTYPE[sRealType]['(최우선)매도호가'])  # 출력 : +(-)2520 매도 1호가
            e = abs(int(e))

            f = self.api.get_comm_real_data(sCode,
                                            self.real_type.REALTYPE[sRealType]['(최우선)매수호가'])  # 출력 : +(-)2520 매수 1호가
            f = abs(int(f))

            g = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType][
                '거래량'])  # 출력 : +240124  매수일때, -2034 매도일 때, 체결거래량
            g = int(g)

            h = self.api.get_comm_real_data(sCode,
                                            self.real_type.REALTYPE[sRealType]['누적거래량'])  # 출력 : 240124 당일 거래된 총 거래량
            h = abs(int(h))

            i = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['고가'])  # 출력 : +(-)2520
            i = abs(int(i))

            # 당일 시가
            j = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['시가'])  # 출력 : +(-)2520
            j = abs(int(j))

            k = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['저가'])  # 출력 : +(-)2520
            k = abs(int(k))

            # l = self.api.get_comm_real_data(sCode, self.real_type.REALTYPE[sRealType]['전일거래량대비(비율)'])  # 출력 : +(-)2520
            # l = float(l)

            print("코드 : {}, 현재가 : {}, 체결시간 : {}".format(sCode, b, a))
            # if sCode not in self.portfolio_stock_dict:
            #     print("포트폴리오 없는 코드 : {}".format(sCode))

            # if sCode in self.portfolio_stock_dict:
            #     print("오류 나기 전 코드 : {}".format(self.portfolio_stock_dict[sCode]["스크린번호"]))

            # 포트폴리오 없는 코드 생김;;;;; 막음
            # hts에서 작업하려면 주문용 스크린번호 키 생성해줘야 함;;;;; 10-19 발견!!!
            # if sCode not in self.portfolio_stock_dict:
            #     self.portfolio_stock_dict.update({sCode: {}})
            #     print("포트폴리오 없는 코드 : {}".format(sCode))

            # self.portfolio_stock_dict[sCode].update({"체결시간": a})
            # self.portfolio_stock_dict[sCode].update({"현재가": b})
            # self.portfolio_stock_dict[sCode].update({"전일대비": c})
            # self.portfolio_stock_dict[sCode].update({"등락율": d})
            # self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            # self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            # self.portfolio_stock_dict[sCode].update({"거래량": g})
            # self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            # self.portfolio_stock_dict[sCode].update({"고가": i})
            # self.portfolio_stock_dict[sCode].update({"시가": j})
            # self.portfolio_stock_dict[sCode].update({"저가": k})

            # print("self.portfolio_stock_dict 111 : {}".format(self.portfolio_stock_dict))
            # 알고리즘 4 적용 할 것
            # if a <= '090031': # 장 시작하자마자
            #     if d >= 1.14: # 등락률 1.14 이상 체결될 때
            #         self.portfolio_stock_dict[sCode].update({"장시작갭상승": True})
            #
            # if '장시작갭상승' in self.portfolio_stock_dict[sCode].keys():
            #     if self.portfolio_stock_dict[sCode]["장시작갭상승"] == True:
            #         if d < -2.3: # 등락율이 시가보다 확 내려가면 제거
            #             self.api.set_real_remove(self.portfolio_stock_dict[sCode]['스크린번호'], sCode)
            #             del self.portfolio_stock_dict[sCode]

            # print("self.portfolio_stock_dict - real slot : {}".format(self.portfolio_stock_dict))
            # self.logging.logger.debug("종목코드 : {}, 체결시간 : {}".format(sCode, a))

            '''
            장중일 때 테스트 구간 start
            '''
            # 분봉 만들기 위한 dict 2020-10-26
            # if sCode in self.real_data_dict:
            #     if a not in self.real_data_dict[sCode]:
            #         self.real_data_dict[sCode].update({a: {}})
            #
            #     if "close" not in self.real_data_dict[sCode][a]:
            #         self.real_data_dict[sCode][a].update({"close": []})
            #     self.real_data_dict[sCode][a]["close"].append(b)
            #     if "volume" not in self.real_data_dict[sCode][a]:
            #         self.real_data_dict[sCode][a].update({"volume": []})
            #     self.real_data_dict[sCode][a]["volume"].append(abs(g))

            # print("self.real_data_dict - real slot : {}".format(self.real_data_dict[sCode]))
            # print("실시간 종목 갯수: {}".format(len(self.real_data_dict)))

            # now_date = self.today + " " + a[:2] + ":" + a[2:4] + ":00"
            # self.logging.logger.debug("체결시간 레이아웃변경 : {}".format(now_date))

            # if now_date not in self.minute_candle_dict[sCode]:
            #     self.minute_candle_dict[sCode].update({now_date: {}})  # 분봉 dict 없는 것 분키 초기화
            #
            # if "volume" not in self.minute_candle_dict[sCode][now_date]:
            #     self.minute_candle_dict[sCode][now_date].update({"volume": 0})
            #
            # volume = self.minute_candle_dict[sCode][now_date]["volume"] + abs(g)
            # self.minute_candle_dict[sCode][now_date].update({"volume": volume})
            #
            # if "open" not in self.minute_candle_dict[sCode][now_date]:
            #     self.minute_candle_dict[sCode][now_date].update({"open": b})
            #
            # low = 0
            # if "low" not in self.minute_candle_dict[sCode][now_date]:
            #     self.minute_candle_dict[sCode][now_date].update({"low": b})
            #     low = b
            # else:
            #     if low >= b:
            #         self.minute_candle_dict[sCode][now_date].update(
            #             {"low": b})
            #
            # high = 0
            # if "high" not in self.minute_candle_dict[sCode][now_date]:
            #     self.minute_candle_dict[sCode][now_date].update({"high": b})
            # else:
            #     if high <= b:
            #         self.minute_candle_dict[sCode][now_date].update(
            #             {"high": b})
            #
            # self.minute_candle_dict[sCode][now_date].update({"close": b})

            # if self.portfolio_stock_dict[sCode]["매수매도"] == "매수":
            #     if self.portfolio_stock_dict[sCode]["이평선허락"]:
            #         if b < i * 0.91:
            #             self.portfolio_stock_dict[sCode].update({"신호": False})
            #         else:
            #             self.portfolio_stock_dict[sCode].update({"신호": True})
            #     else:
            #         self.portfolio_stock_dict[sCode].update({"신호": False})
            # else:
            #     if self.portfolio_stock_dict[sCode]["이평선허락"]:
            #         self.portfolio_stock_dict[sCode].update({"신호": True})
            #     else:
            #         self.portfolio_stock_dict[sCode].update({"신호": False})

            # if self.portfolio_stock_dict[sCode]["매수매도"] == "매도":
            #     self.portfolio_stock_dict[sCode].update({"신호": False})
            #     g_list = self.portfolio_stock_dict[sCode]["체결량리스트"]
            #     if len(g_list) == 10:
            #         if len([z for z in g_list if z > 0]) == 0: # 연속 10개 -
            #             self.logging.logger.debug("매도 종목코드 : {}, 연속 10개 체결량이 -일 때 : {}".format(sCode, a))
            #             self.portfolio_stock_dict[sCode].update({"세력체결조절여부": True})
            #         elif len([z for z in g_list if z < 0]) == 0: # 연속 10개 +
            #             self.logging.logger.debug("매도 종목코드 : {}, 매도조건 이탈 : {}".format(sCode, a))
            #             self.portfolio_stock_dict[sCode].update({"세력체결조절여부": False})
            #         g_list.pop(0)
            #     g_list.append(g)
            #
            #     if self.portfolio_stock_dict[sCode]["전환점여부"]:
            #         if self.portfolio_stock_dict[sCode]["세력체결조절여부"]:
            #             # if self.portfolio_stock_dict[sCode]["이평선허락"]:
            #             self.portfolio_stock_dict[sCode].update({"신호": True})
            #             # else:
            #         else:
            #             self.portfolio_stock_dict[sCode].update({"신호": False})
            #
            #
            # if self.portfolio_stock_dict[sCode]["매수매도"] == "매수":
            #     self.portfolio_stock_dict[sCode].update({"신호": False})
            #     g_list = self.portfolio_stock_dict[sCode]["체결량리스트"]
            #     if len(g_list) == 2: #체결량리스트 갯수 조절용
            #         if g_list[-1] == abs(self.portfolio_stock_dict[sCode]["매도호가직전대비1"][-1]):
            #             self.logging.logger.debug("매수 종목코드 : {}, 이전체결량 : {}, 현재매도호가직전대비1 : {}".format(sCode, g_list[-1], abs(self.portfolio_stock_dict[sCode]["매도호가직전대비1"][-1])))
            #             self.portfolio_stock_dict[sCode].update({"세력체결조절여부": True})
            #         # elif len([z for z in g_list if z > 0]) == 0: # 연속 10개 -
            #         #     self.logging.logger.debug("매수 종목코드 : {}, 매수조건 이탈 : {}".format(sCode, a))
            #         #     self.portfolio_stock_dict[sCode].update({"세력체결조절여부": False}) #
            #         g_list.pop(0)
            #     g_list.append(g)
            #
            #     if self.portfolio_stock_dict[sCode]["전환점여부"]:
            #         if self.portfolio_stock_dict[sCode]["세력체결조절여부"]:
            #             if self.portfolio_stock_dict[sCode]["이평선허락"]:
            #                 self.portfolio_stock_dict[sCode].update({"신호": True})
            #             else:
            #                 self.portfolio_stock_dict[sCode].update({"신호": False})
            '''
            장중일 때 테스트 구간 end
            '''

            # 변동성 돌파 전략 20.12.02
            # if self.portfolio_stock_dict[sCode]["매수매도"] == "매수":
            #     sub_price = self.portfolio_stock_dict[sCode]["매수 목표가 중간 값"]
            #     self.portfolio_stock_dict[sCode].update({"매수 목표가": j + sub_price})
            #     target_price = self.portfolio_stock_dict[sCode]["매수 목표가"]
            #     ma5_price = self.portfolio_stock_dict[sCode]["ma5"]
            #     ma10_price = self.portfolio_stock_dict[sCode]["ma10"]
            #     if d < 20: #전날 종가 대비 등락률이 20%미만일 때 - 상한가 종목도 매수처리하다 오류나서 추가(매수할 때 (최우선)매도호가가 0이 되서 오류남) 20.12.03
            #         if b > target_price and b > ma5_price and b > ma10_price:
            #             self.portfolio_stock_dict[sCode].update({"신호": True})

            # print("self.portfolio_stock_dict : {}".format(self.portfolio_stock_dict))

            # 계좌평가잔고내역 종목 매도하기 - 로그인 전 매수한 건
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                asd = self.account_stock_dict[sCode]

                meme_rate = (b - asd['매입가']) / asd['매입가'] * 100

                # self.logging.logger.debug("수익률 : {}, 주문용스크린번호: {}, 계좌번호: {}".format(meme_rate, self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num))
                # print("계좌평가잔고내역 종목코드 : {}, 매매가능수량: {}, 수익률: {}, 시간: {}".format(sCode, asd['매매가능수량'], meme_rate, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                if sCode in self.portfolio_stock_dict.keys():
                    if "당일상한가" in self.portfolio_stock_dict[sCode]:
                        if b > self.portfolio_stock_dict[sCode]['당일상한가']:
                            order_success = self.api.send_order("신규매도", self.portfolio_stock_dict[sCode][
                                "주문용스크린번호"],
                                                                self.account_num, 2, sCode, asd['매매가능수량'],
                                                                0,
                                                                self.real_type.SENDTYPE['거래구분']['시장가'], "")

                            if order_success == 0:
                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(계좌에 있던 거)")
                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                                del self.account_stock_dict[sCode]

                            else:
                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패(계좌에 있던 거)")
                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")

                    if "ub" in self.portfolio_stock_dict[sCode] and "D1Close" in self.portfolio_stock_dict[sCode] \
                            and "bandwidth" in self.portfolio_stock_dict[sCode] and "MA20" in self.portfolio_stock_dict[sCode]:
                        # print("들어가기 전 계좌평가잔고내역 종목코드 : {}, 매매가능수량: {}, 수익률: {}, 시간: {}, 현재가: {}".format(sCode, asd['매매가능수량'],
                        #                                                                         meme_rate,
                        #                                                                         datetime.datetime.now().strftime(
                        #                                                                             '%Y-%m-%d %H:%M:%S'),
                        #                                                                         b))
                        if asd['매매가능수량'] > 0:
                            if meme_rate > 1:
                                # print("들어간 후 계좌평가잔고내역 종목코드 : {}, 매매가능수량: {}, 수익률: {}, 시간: {}, 현재가: {}".format(sCode, asd['매매가능수량'],
                                #                                                                meme_rate,
                                #                                                                datetime.datetime.now().strftime(
                                #                                                                    '%Y-%m-%d %H:%M:%S'), b))
                                # print("들어가기 전 MA20: {}, average: {}".format(self.portfolio_stock_dict[sCode]["MA20"],
                                #                                      self.portfolio_stock_dict[sCode]["average"]))
                                if b < self.portfolio_stock_dict[sCode]["ub"] and b < self.portfolio_stock_dict[sCode]["D1Close"]:
                                    # or (self.t_sell.strftime('%Y-%m-%d %H:%M:%S') < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_exit.strftime('%Y-%m-%d %H:%M:%S'))):
                                    if self.portfolio_stock_dict[sCode]["bandwidth"] > 16:
                                        if b <= self.portfolio_stock_dict[sCode]["MA20"]:
                                            order_success = self.api.send_order("신규매도", self.portfolio_stock_dict[sCode][
                                                "주문용스크린번호"],
                                                                                self.account_num, 2, sCode, asd['매매가능수량'],
                                                                                0,
                                                                                self.real_type.SENDTYPE['거래구분']['시장가'], "")

                                            if order_success == 0:
                                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(계좌에 있던 거)")
                                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                                                del self.account_stock_dict[sCode]

                                            else:
                                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패(계좌에 있던 거)")
                                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")

                    if asd['매매가능수량'] > 0 and meme_rate < -5:  # 손절매
                        order_success = self.api.send_order("신규매도",
                                                            self.portfolio_stock_dict[sCode]["주문용스크린번호"],
                                                            self.account_num, 2, sCode, asd['매매가능수량'], 0,
                                                            self.real_type.SENDTYPE['거래구분']['시장가'], "")

                        if order_success == 0:
                            self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(계좌에 있던 거)")
                            # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                            del self.account_stock_dict[sCode]

                        else:
                            self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패(계좌에 있던 거)")
                            # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")


            #  프로그램 run 한 후 주문한 종목 팔기
            elif sCode in self.jango_dict.keys():
                # print("self.jango_dict : {}".format(self.jango_dict))
                jd = self.jango_dict[sCode]
                meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100  # 수익률 (b : 현재가)

                if sCode in self.portfolio_stock_dict.keys():
                    if "당일상한가" in self.portfolio_stock_dict[sCode]:
                        if b > self.portfolio_stock_dict[sCode]['당일상한가']:
                            order_success = self.api.send_order("신규매도", self.portfolio_stock_dict[sCode][
                                "주문용스크린번호"],
                                                                self.account_num, 2, sCode, jd['주문가능수량'], 0,
                                                                self.real_type.SENDTYPE['거래구분']['시장가'], "")

                            if order_success == 0:
                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(프로그램 오픈 후)")
                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                            else:
                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패")
                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")

                    if "ub" in self.portfolio_stock_dict[sCode] and "D1Close" in self.portfolio_stock_dict[sCode] \
                            and "bandwidth" in self.portfolio_stock_dict[sCode] and "MA20" in self.portfolio_stock_dict[sCode]:

                        if jd['주문가능수량'] > 0:
                            # or (self.t_sell.strftime('%Y-%m-%d %H:%M:%S') < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_exit.strftime('%Y-%m-%d %H:%M:%S'))):
                            if meme_rate > 1:
                                if b < self.portfolio_stock_dict[sCode]["ub"] and b < self.portfolio_stock_dict[sCode][
                                    "D1Close"]:
                                    # or (self.t_sell.strftime('%Y-%m-%d %H:%M:%S') < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_exit.strftime('%Y-%m-%d %H:%M:%S'))):
                                    if self.portfolio_stock_dict[sCode]["bandwidth"] > 16:
                                        if b <= self.portfolio_stock_dict[sCode]["MA20"]:
                                            order_success = self.api.send_order("신규매도", self.portfolio_stock_dict[sCode][
                                                "주문용스크린번호"],
                                                                                self.account_num, 2, sCode, jd['주문가능수량'], 0,
                                                                                self.real_type.SENDTYPE['거래구분']['시장가'], "")

                                            if order_success == 0:
                                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(프로그램 오픈 후)")
                                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                                            else:
                                                self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패")
                                                # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")

                    if jd['주문가능수량'] > 0 and meme_rate < -5:  # 손절매
                        order_success = self.api.send_order("신규매도",
                                                            self.portfolio_stock_dict[sCode]["주문용스크린번호"],
                                                            self.account_num, 2, sCode, jd['주문가능수량'], 0,
                                                            self.real_type.SENDTYPE['거래구분']['시장가'], "")

                        if order_success == 0:
                            self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 성공(프로그램 오픈 후)")
                            # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 성공")
                        else:
                            self.logging.logger.debug("코드 : " + sCode + " 매도주문 전달 실패")
                            # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매도주문 전달 실패")
            # 여기는 매수
            # elif d > 2.0 and sCode not in self.jango_dict:
            elif sCode not in self.jango_dict:

                # 포트폴리오 로직 수정 후 아래 지워야 함
                # if sCode in self.portfolio_stock_dict.keys():
                #     print("매수종목코드 : {}, 포트폴리오 : {}, 현재가: {}, 시간: {}".format(sCode, self.portfolio_stock_dict[sCode], e,
                #                                       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                # else:
                #     print("매수 포트폴리오 dict이 없다!!!")

                if e > 0:  # (최우선)매도호가가 0이면 안됨(ex. 상한가)
                    if sCode in self.portfolio_stock_dict.keys():  # 포트폴리오에 있을 때
                        # self.logging.logger.debug("종목코드 : {}, 매수신호 : {}".format(sCode, self.portfolio_stock_dict[sCode]["신호"]))
                        # if self.portfolio_stock_dict[sCode]["신호"]:
                        #     print("self.portfolio_stock_dict - 매수일 때 : {}".format(self.portfolio_stock_dict))
                        #     print("self.portfolio_stock_dict  매수일 때 개수 : {}".format(len(self.portfolio_stock_dict)))
                        if "매수매도" in self.portfolio_stock_dict[sCode]:  # 원래 갖고 있던 종목에는 매수매도가 없으므로 나중에 수정 더 좋은걸로
                            if self.portfolio_stock_dict[sCode]["매수매도"] == "매수":
                                self.logging.logger.debug("매수조건 통과 %s " % sCode)
                                self.logging.logger.debug("(최우선)매도호가 %s " % e)

                                # self.use_money 500만원이 됨
                                result = (self.use_money * 0.1) / e
                                quantity = int(result)

                                order_success = self.api.send_order("신규매수",
                                                                    self.portfolio_stock_dict[sCode]["주문용스크린번호"],
                                                                    self.account_num, 1, sCode, quantity, e,
                                                                    self.real_type.SENDTYPE['거래구분']['지정가'], "")
                                # 주문유형(4번째 파라미터) 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                                # 마지막 파라미터 : 신규주문시에는 빈값, 이후에 주문 취소 및 정정주문에서는 주문번호가 필요
                                if order_success == 0:
                                    self.logging.logger.debug("코드 : " + sCode + " 매수주문 전달 성공")
                                    self.portfolio_stock_dict[sCode].update({"매수매도": "매도"})
                                    # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매수주문 전달 성공")
                                else:
                                    self.logging.logger.debug("코드 : " + sCode + " 매수주문 전달 실패")
                                    # self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 매수주문 전달 실패")

            not_meme_list = list(self.not_account_stock_dict)
            for order_num in not_meme_list:
                code = self.not_account_stock_dict[order_num]["종목코드"]
                meme_price = self.not_account_stock_dict[order_num]['주문가격']
                not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
                order_gubun = self.not_account_stock_dict[order_num]['주문구분']

                if order_gubun == "매수" and not_quantity > 0 and e > meme_price:

                    order_success = self.api.send_order("매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"],
                                                        self.account_num, 3, sCode, 0, 0,
                                                        self.real_type.SENDTYPE['거래구분']['지정가'], order_num)
                    # 주문수량(5번째 파라미터) : 0으로 하면 미체결수량 전부를 매수취소한다는 뜻이다.
                    # 주문가격(6번째 파라미터) : 매수취소라 주문가격은 필요없으므로 0
                    if order_success == 0:
                        self.logging.logger.debug("매수취소 전달 성공")
                    else:
                        self.logging.logger.debug("매수취소 전달 실패")

                elif not_quantity == 0:
                    del self.not_account_stock_dict[order_num]

    # 주문후 체결 정보
    def _chejan_slot(self, sGubun, nItemCnt, sFidList):
        # sGubun '0': 주문체결, '1' : 잔고, '4' : 파생잔고
        # 주문체결 : 접수 -> 확인 -> 체결
        # 잔고 : 체결된 주문이 잔고에 영향을 줄 때
        # print("체잔 정보 chejan_slot : {}".format(int(sGubun)))

        if int(sGubun) == 0:  # 주문체결, 접수한 데이터도 들어옴

            account_num = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['계좌번호'])
            sCode = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.api.get_chejan_data(
                self.real_type.REALTYPE['주문체결']['원주문번호'])  # 출력 : defaluse : "000000"
            order_number = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문번호'])  # 출럭: 0115061 마지막 주문번호
            order_status = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문상태'])  # 출력: 접수, 확인, 체결
            order_quan = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문수량'])  # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문가격'])  # 출력: 21000
            order_price = int(order_price)

            not_chegual_quan = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['미체결수량'])  # 출력: 15, default: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문구분'])  # 출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['주문/체결시간'])  # 출력: '151028'
            chegual_price = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['체결가'])  # 출력: 2110  default : ''

            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['체결량'])  # 출력: 5  default : ''

            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['현재가'])  # 출력: -6000
            current_price = abs(int(current_price))

            first_sell_price = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['(최우선)매도호가'])  # 출력: -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.api.get_chejan_data(self.real_type.REALTYPE['주문체결']['(최우선)매수호가'])  # 출력: -6000
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

            self.logging.logger.debug("접수, 확인, 체결 : %s" % (self.not_account_stock_dict[order_number]))

        elif int(sGubun) == 1:  # 잔고

            account_num = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['계좌번호'])
            sCode = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['총매입가'])  # 계좌에 있는 종목의 총매입가
            total_buy_price = int(total_buy_price)

            meme_gubun = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.real_type.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.api.get_chejan_data(self.real_type.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode: {}})

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

            self.logging.logger.debug("잔고반영: %s" % (self.jango_dict[sCode]))
            if stock_quan == 0:
                del self.jango_dict[sCode]
                # print("매도 지우기 전 스크린번호 확인 : {}".format(self.portfolio_stock_dict[sCode])) # 해당 코드 실시간 안 없어짐 2020.10.22
                self.api.set_real_remove(self.portfolio_stock_dict[sCode]['스크린번호'], sCode)
                self.api.set_real_remove(self.portfolio_stock_dict[sCode]['주문용스크린번호'], sCode)
                del self.portfolio_stock_dict[sCode]
                # del self.real_data_dict[sCode] # 분봉을 위한 실시간 데이터 담는 dict
                # if sCode in self.condition_stock:
                #     del self.condition_stock[sCode] # 조건검색 dict 삭제
                # 팔았을 땐 지우자. 10-25 다시 확인할 것
                #
                # seq = self.mk.get_buy_stock_info_max_seq(sCode, self.datetime)
                #
                # with self.mk.conn.cursor() as curs:
                #     sql = "UPDATE buy_stock_info SET state WHERE code = '{}' and buy_date = '{}' and seq = '{}'"\
                #         .format(sCode, self.datetime, seq)
                #     curs.execute(sql)
                #     self.mk.conn.commit()

    # 송수신 메세지 get
    def _msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        self.logging.logger.debug("스크린: %s, 요청이름: %s, tr코드: %s, 시간: %s --- %s" % (
            sScrNo, sRQName, sTrCode, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))

    def _opt10080(self, ex_data):  # 분봉 호출

        ex_data.sort(key=lambda x: x[2])
        # [['+2345', '1305', '20201028101300', '+2345', '+2345', '+2340', '', '', '', '', '', '', ''],
        #  ['+2345', '15415', '20201028101400', '+2350', '+2350', '+2335', '', '', '', '', '', '', '']......

        final_dic = dict()
        for idx, data_list in enumerate(ex_data):

            convert_date = data_list[2][:4] + "-" + data_list[2][4:6] + "-" + data_list[2][6:8] + " " + data_list[2][
                                                                                                        8:10] + ":" + \
                           data_list[2][10:12] + ":" + "00"

            # colName = ['close', 'volume', 'date', 'open', 'high', 'low',
            #            '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']

            if convert_date not in final_dic.keys():
                final_dic.update({convert_date: {}})

            final_dic[convert_date].update({"close": abs(int(data_list[0]))})
            final_dic[convert_date].update({"volume": int(data_list[1])})

            final_dic[convert_date].update({"open": abs(int(data_list[3]))})
            final_dic[convert_date].update({"high": abs(int(data_list[4]))})
            final_dic[convert_date].update({"low": abs(int(data_list[5]))})

        # df = pd.DataFrame(final_dic)
        # df = df.T
        #
        # print("final_dic : {}".format(final_dic))

        self.minute_candle_dict.update({self.test_code: final_dic})
        self.portfolio_stock_dict[self.test_code].update(
            {'최종작업시간': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')[-8:].replace(":", "")})

        # print("self.minute_candle_dict 분봉 : {}".format(self.minute_candle_dict[self.test_code]))

    def _opt10080_test(self, ex_data):  # 분봉 테스트
        colName = ['close', 'volumn', 'date', 'open', 'high', 'low',
                   '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']

        df = pd.DataFrame(ex_data, columns=colName)

        df.index = pd.to_datetime(df.date)

        df = df[['close', 'volumn', 'open', 'high', 'low']]

        df[['close', 'volumn', 'open', 'high', 'low']] = df[
            ['close', 'volumn', 'open', 'high', 'low']].astype(int)

        # df는 현재에서 과거로, final_df는 과거에서 현재로 - 이평선 컬럼 만들기 위해
        final_df = df.sort_index()

        final_df['close'] = final_df['close'].abs()
        final_df['open'] = final_df['open'].abs()
        final_df['high'] = final_df['high'].abs()
        final_df['low'] = final_df['low'].abs()

        book = final_df.copy()
        book['trade'] = ''

        final_df['MA3'] = final_df['close'].rolling(window=3).mean()
        final_df['MA5'] = final_df['close'].rolling(window=5).mean()
        final_df['MA10'] = final_df['close'].rolling(window=10).mean()
        final_df['MA20'] = final_df['close'].rolling(window=20).mean()
        final_df['MA60'] = final_df['close'].rolling(window=60).mean()

        print(final_df)
        # final_df['MA5_dpc'] = final_df['MA5'].pct_change(5)

        final_df['MA240'] = final_df['close'].rolling(window=240).mean()
        final_df['bandwidth5-20'] = ((final_df['MA5'] - final_df['MA20']) / (
                (final_df['MA5'] + final_df['MA20']) / 2)) * 100
        final_df['stddev'] = final_df['close'].rolling(window=20).std()
        final_df['upper'] = final_df['MA20'] + (final_df['stddev'] * 2)
        final_df['lower'] = final_df['MA20'] - (final_df['stddev'] * 2)
        final_df['bandwidth'] = (final_df['upper'] - final_df['lower']) / final_df['MA20'] * 100

        # print(final_df.loc['2021-02-24 15:09:00', 'MA5_dpc'])
        print(final_df.loc['2020-11-18 10:22:00', 'lower'])
        print(final_df.loc['2020-11-18 10:22:00', 'MA20'])
        print(final_df.loc['2020-11-18 11:05:00', 'upper'])

        pre_val = ''
        close_list = []
        max_close = 0
        min_close = 0

        volume_list = []
        max_volume = 0
        min_volume = 0

        for i in final_df.index:

            if pre_val != '':
                '''
                매수
                '''
                if 1 < final_df.loc[pre_val, 'bandwidth'] <= 2.5:  # 밴드폭이 1~2 사이
                    if final_df.loc[pre_val, 'MA5'] < final_df.loc[i, 'MA5']:
                        if final_df.loc[i, 'close'] > final_df.loc[i, 'open']:  # 현재 양봉
                            if final_df.loc[i, 'close'] > final_df.loc[i, 'upper'] > final_df.loc[
                                i, 'open']:  # 볼린저 밴드 상향선 돌파
                                if final_df.loc[i, 'volumn'] > final_df.loc[pre_val, 'volumn'] * 2.9:  # 거래량 급증
                                    book.loc[i, 'trade'] = 'buy'

                # if final_df.loc[pre_val, 'MA5'] > final_df.loc[pre_val, 'MA20']:
                #     if 1 < final_df.loc[pre_val, 'bandwidth'] <= 2:  # 밴드폭이 1~2 사이
                #         if final_df.loc[i, 'close'] > final_df.loc[i, 'open']: # 현재 양봉
                #             # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
                #                 if final_df.loc[i, 'close'] > final_df.loc[i, 'upper'] > final_df.loc[i, 'open']: # 볼린저 밴드 상향선 돌파
                #                     if final_df.loc[i, 'volumn'] > final_df.loc[pre_val, 'volumn'] * 4: # 거래량 급증
                #                         book.loc[i, 'trade'] = 'buy'
                #     elif final_df.loc[pre_val, 'bandwidth'] > 2:
                #         if final_df.loc[pre_val, 'MA10_dpc'] > 0.00075:
                #             if final_df.loc[i, 'close'] > final_df.loc[i, 'open']: # 현재 양봉
                #                 # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
                #                     if (final_df.loc[i, 'close'] > final_df.loc[i, 'upper'] > final_df.loc[i, 'open']) \
                #                             or (final_df.loc[i, 'upper'] > final_df.loc[i, 'close'] > final_df.loc[i, 'MA5']): #
                #                         if final_df.loc[i, 'volumn'] > final_df.loc[pre_val, 'volumn'] * 2: #
                #                             book.loc[i, 'trade'] = 'buy'
                # else:
                #     if final_df.loc[pre_val, 'bandwidth'] > 5:
                #         if final_df.loc[i, 'close'] > final_df.loc[i, 'open']: # 현재 양봉
                #             # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
                #                 if final_df.loc[i, 'close'] > final_df.loc[i, 'MA20'] > final_df.loc[i, 'open']: # 20일선 상향선 돌파
                #                     if final_df.loc[i, 'volumn'] > final_df.loc[pre_val, 'volumn'] * 2: #
                #                         book.loc[i, 'trade'] = 'buy'

                '''
                매도
                '''
                if final_df.loc[pre_val, 'MA5'] < final_df.loc[i, 'MA5']:
                    if max_volume > final_df.loc[i, 'volumn'] * 2:
                        if final_df.loc[i, 'close'] < final_df.loc[i, 'open']:  # 현재 음봉
                            if final_df.loc[i, 'bandwidth'] > 7.8:
                                if final_df.loc[pre_val, 'close'] > final_df.loc[pre_val, 'open']:  # 1분전 양봉
                                    if final_df.loc[pre_val, 'open'] <= final_df.loc[i, 'open'] <= final_df.loc[
                                        pre_val, 'high']:
                                        book.loc[i, 'trade'] = 'sell'
                                else:  # 1분전 음봉
                                    if final_df.loc[pre_val, 'open'] <= final_df.loc[i, 'open'] <= final_df.loc[
                                        pre_val, 'high']:
                                        book.loc[i, 'trade'] = 'sell'

                # if round(final_df.loc[i, 'upper']) == round(final_df.loc[i, 'lower']):
                #     if final_df.loc[i, 'close'] == max_close:
                #         book.loc[i, 'trade'] = 'sell'
                # else:
                #     if final_df.loc[i, 'close'] > min_close * 1.05:
                #         if final_df.loc[pre_val, 'MA20_dpc5'] < 0:
                #             if final_df.loc[pre_val, 'MA3_dpc'] >= 0 and final_df.loc[i, 'MA3_dpc'] < 0: # 3일선이 상향에서 하향으로 변경
                #                 # if final_df.loc[pre_val, 'MA10_dpc'] > 0 and final_df.loc[pre_val, 'MA20_dpc'] > 0:
                #                     if final_df.loc[i, 'close'] < final_df.loc[i, 'open']:  # 현재 음봉
                #                         if final_df.loc[i, 'close'] < final_df.loc[i, 'MA3'] < final_df.loc[i, 'open']:
                #                             book.loc[i, 'trade'] = 'sell'

                if len(close_list) == 5:
                    close_list.pop(0)
                close_list.append(final_df.loc[i, 'close'])
                max_close = max(close_list)
                min_close = min(close_list)

                if len(volume_list) == 5:
                    volume_list.pop(0)
                volume_list.append(final_df.loc[i, 'volumn'])
                max_volume = max(volume_list)
                min_volume = min(volume_list)

            pre_val = i

        book = book[(book['trade'] == 'buy') | (book['trade'] == 'sell')]

        book = book[book.index.strftime('%Y-%m-%d %H:%M') >= '2021-02-25 15:30:00']

        print(book.tail(300))
