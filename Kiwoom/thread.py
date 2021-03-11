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
                    mAlgo = MinuteCandleAlgorithm(code)

                    if len(mAlgo.mIndicator.minute_df['체결가']) >= 20:
                        if mAlgo.mIndicator.t_now.strftime('%Y-%m-%d %H:%M:%S') < mAlgo.mIndicator.t_9_22.strftime(
                                '%Y-%m-%d %H:%M:%S'):  # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
                            QTest.qWait(6000)
                        else:
                            QTest.qWait(3000)
                        self.signal.portfolio_stock_dict[code].update({"average": round(mAlgo.mIndicator.minute_df['average'].iloc[-2])})  # D-1값
                        self.signal.portfolio_stock_dict[code].update({"MA20": round(mAlgo.mIndicator.minute_df['MA20'].iloc[-2])}) # D-1값
                        self.signal.portfolio_stock_dict[code].update({"max10": round(mAlgo.mIndicator.minute_df['max10'].iloc[-2])})  # D-1값
                        self.signal.portfolio_stock_dict[code].update({"min10": round(mAlgo.mIndicator.minute_df['min10'].iloc[-2])}) # D-1값
                except:
                    print("{} sell 코드 오류 발생".format(code))
            time.sleep(90)


class BuyThread(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        i = 0
        max = len(self.signal.condition_stock)
        if max > 0:
            while i == 0:
                for code in self.signal.condition_stock.keys():
                    if code not in self.signal.portfolio_stock_dict:
                        QTest.qWait(500)
                        try:
                            mAlgo = MinuteCandleAlgorithm(code)

                            if len(mAlgo.mIndicator.minute_df['체결가']) >= 20:
                                if self.signal.api.server_gubun == "1":
                                    # is_receive_real = 0이면 자꾸 들어오니까 강제로 1로 바꿈 (나중에 테이블 수정하기!!!) 2021-02-18
                                    if code == '066430' or code == '570045' or code == '036630' or code == '093230':
                                        continue
                                    else:
                                        mAlgo.buy(code, self.signal.real_time_recommand_dict)
                                else:
                                    mAlgo.buy(code, self.signal.real_time_recommand_dict)

                        except:
                            print("{} buy 코드 오류 발생".format(code))

                i += 1
                if i == max:
                    i = 0
        # print("끝났다")


class RealTimeScreenNumbering(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            # self.signal.real_time_recommand_fuc() # real_time_recommand_dict에 넣음
            # QTest.qWait(1000)  # 1초
            self.signal.screen_number_real_time_setting()
            # QTest.qWait(8000)  # 8초
            # df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            # for code in df_copy:
            #     self.signal.checking_minute_candle_func(code)
            time.sleep(70)
