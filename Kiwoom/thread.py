from PyQt5.QtCore import QThread
# from PyQt5.QtCore import pyqtSignal, pyqtSlot
# from Kiwoom.Signal import Signal
import time

class MinuteCandle(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            # print("sche_minute_candle self.signal.another_job_stop : {}".format(self.signal.another_job_stop))
            # if self.signal.another_job_stop:
            df_copy = self.signal.portfolio_stock_dict.copy()  # 반복문 오류를 피하기 위해
            for code in df_copy:
                self.signal.make_minute_candle_func(code)
                # self.signal.another_job_stop = False
            time.sleep(10)


class RealTimeScreenNumbering(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        while True:
            # print("RealTimeScreenNumbering self.signal.another_job_stop : {}".format(self.signal.another_job_stop))
            # if not self.signal.another_job_stop:
            self.signal.real_time_new_portfolio_fuc()
            self.signal.real_time_condition_stock_fuc()
            self.signal.screen_number_real_time_setting()
            # self.signal.another_job_stop = True
            time.sleep(3)


