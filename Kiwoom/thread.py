from PyQt5.QtCore import QThread
import time
from PyQt5.QtTest import QTest
from Kiwoom.quant.MinuteCandleAlgorithm import MinuteCandleAlgorithm


class SellThread(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            for code in df_copy:
                QTest.qWait(500)
                try:
                    global dayObjectCreate
                    if "당일상한가" in df_copy: # 계좌에 있는 종목은 계좌평가잔고내역 호출할 때 가져온다
                        dayObjectCreate = False
                    else:
                        dayObjectCreate = True
                    mAlgo = MinuteCandleAlgorithm(code, dayObjectCreate)

                    if len(mAlgo.mIndicator.minute_df['체결가']) >= 20:
                        if mAlgo.mIndicator.t_now.strftime('%Y-%m-%d %H:%M:%S') < mAlgo.mIndicator.t_9_22.strftime(
                                '%Y-%m-%d %H:%M:%S'):  # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
                            QTest.qWait(6000)
                        else:
                            QTest.qWait(3000)
                        self.signal.portfolio_stock_dict[code].update({"ub": round(mAlgo.mIndicator.minute_df['ub'].iloc[-1])})
                        self.signal.portfolio_stock_dict[code].update({"D1Close": round(mAlgo.mIndicator.minute_df['체결가'].iloc[-2])}) # D-1값
                        self.signal.portfolio_stock_dict[code].update({"bandwidth": round(mAlgo.mIndicator.minute_df['bandwidth'].iloc[-1])})
                        self.signal.portfolio_stock_dict[code].update({"MA20": round(mAlgo.mIndicator.minute_df['min10'].iloc[-1])})
                        if dayObjectCreate:
                            self.signal.portfolio_stock_dict[code].update(
                                {"당일상한가": mAlgo.dayAlgo.dIndicator.day_candle['Close'].iloc[-2] * 1.298})
                except:
                    print("{} sell 코드 오류 발생".format(code))
            time.sleep(90)


class BuyThread(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        # i = 0
        # max = len(self.signal.condition_stock)
        # if max > 0:
        #     while i == 0:
        for code in self.signal.condition_stock.keys():
            if code not in self.signal.portfolio_stock_dict:
                QTest.qWait(500)
                try:
                    if self.signal.api.server_gubun == "1": # 모의서버
                        # is_receive_real = 0이면 자꾸 들어오니까 강제로 1로 바꿈 (나중에 테이블 수정하기!!!) 2021-02-18
                        if code == '066430' or code == '570045' or code == '036630' or code == '093230':
                            continue
                        else:
                            code_name = self.signal.api.get_master_code_name(code)
                            MinuteCandleAlgorithm(code, code_name)
                    else:
                        code_name = self.signal.api.get_master_code_name(code)
                        MinuteCandleAlgorithm(code, code_name)
                except:
                    print("{} buy 코드 오류 발생".format(code))

                # i += 1
                # if i == max:
                #     i = 0
        print("끝났다")


class RealTimeScreenNumbering(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            self.signal.real_time_recommand_fuc() # real_time_recommand_dict에 넣음
            QTest.qWait(1000)  # 1초
            self.signal.screen_number_real_time_setting()
            # QTest.qWait(8000)  # 8초
            # df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            # for code in df_copy:
            #     self.signal.checking_minute_candle_func(code)
            time.sleep(70)
