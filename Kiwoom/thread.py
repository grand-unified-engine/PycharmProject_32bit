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
            # if not self.signal.another_job_stop:
            # self.signal.real_time_new_portfolio_fuc() # 포트폴리오 테이블에 넣을 때
            self.signal.real_time_condition_stock_fuc()
            QTest.qWait(500)  # 1초
            self.signal.screen_number_real_time_setting()
            # QTest.qWait(8000)  # 8초
            # df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            # for code in df_copy:
            #     self.signal.checking_minute_candle_func(code)
            # self.signal.another_job_stop = True
            # cnt = 0
            # df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            # for code in df_copy:
            #     if "스크린번호" in self.signal.portfolio_stock_dict[code]:
            #         cnt += 1
            # print("실시간 도는 종목 수 : {}".format(cnt))
            t = 0
            if self.signal.real_stock_cnt <= 10:
                t = 30
            elif 10 < self.signal.real_stock_cnt <= 20:
                t = 60
            elif 20 < self.signal.real_stock_cnt <= 30:
                t = 90

            time.sleep(t)


