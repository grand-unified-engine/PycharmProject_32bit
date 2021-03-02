from PyQt5.QtCore import QThread
import time
from PyQt5.QtTest import QTest
from Kiwoom.quant.MinuteAlgorithm import MinuteAlgorithm

class MinuteCandle(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            for code in df_copy:
                m_algo = MinuteAlgorithm(code)
                QTest.qWait(4000)
                self.signal.portfolio_stock_dict[code].update({"average": round(m_algo.minute_df['average'].iloc[-2])})  # D-1값
                self.signal.portfolio_stock_dict[code].update({"MA10": round(m_algo.minute_df['MA10'].iloc[-2])}) # D-1값
            time.sleep(90)


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


