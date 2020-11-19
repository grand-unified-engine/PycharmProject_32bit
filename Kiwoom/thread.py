from PyQt5.QtCore import QThread
# from PyQt5.QtCore import pyqtSignal, pyqtSlot
# from Kiwoom.Signal import Signal
import time
from PyQt5.QtTest import QTest

class MinuteCandle(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            # print("sche_minute_candle self.signal.another_job_stop : {}".format(self.signal.another_job_stop))
            if self.signal.another_job_stop:
                df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
                for code in df_copy:
                    self.signal.make_minute_candle_func(code)
            self.signal.another_job_stop = False
            time.sleep(20)


class RealTimeScreenNumbering(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            # print("RealTimeScreenNumbering self.signal.another_job_stop : {}".format(self.signal.another_job_stop))
            if not self.signal.another_job_stop:
            # self.signal.real_time_new_portfolio_fuc() # 포트폴리오 테이블에 넣을 때
                self.signal.real_time_condition_stock_fuc()
                self.signal.screen_number_real_time_setting()
            # QTest.qWait(8000)  # 8초
            # df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            # for code in df_copy:
            #     self.signal.make_minute_candle_func(code)
            self.signal.another_job_stop = True
            time.sleep(30)


