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

                if m_algo.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < m_algo.t_9_22.strftime(
                        '%Y-%m-%d %H:%M:%S'):  # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
                    QTest.qWait(6000)
                else:
                    QTest.qWait(5000)
                self.signal.portfolio_stock_dict[code].update({"average": round(m_algo.minute_df['average'].iloc[-2])})  # D-1값
                self.signal.portfolio_stock_dict[code].update({"MA20": round(m_algo.minute_df['MA20'].iloc[-2])}) # D-1값
                self.signal.portfolio_stock_dict[code].update({"max10": round(m_algo.minute_df['max10'].iloc[-2])})  # D-1값
                self.signal.portfolio_stock_dict[code].update({"min10": round(m_algo.minute_df['min10'].iloc[-2])}) # D-1값
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


class BuyMinuteCandle(QThread):
    def __init__(self, signal):
        QThread.__init__(self)
        self.signal = signal

    def run(self):
        i = 0
        max = len(self.signal.condition_stock)
        while i == 0:

            for code in self.signal.condition_stock.keys():
                QTest.qWait(1000)
                m_algo = MinuteAlgorithm(code)

                if m_algo.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < m_algo.t_9_22.strftime(
                        '%Y-%m-%d %H:%M:%S'):  # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
                    QTest.qWait(6000)
                else:
                    QTest.qWait(5000)

                if m_algo.minute_df['체결가'].iloc[-1] / (m_algo.minute_df['체결가'].iloc[-1] - m_algo.minute_df['전일비'].iloc[-1]) > 17:
                    continue
                else:
                    self.signal.real_time_recommand_dict.update(
                        {code: {"time": time.strftime('%H%M%S'), "numbering": False}})
                    self.logging.logger.debug("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(code,
                                                                                                   self.real_time_recommand_dict[
                                                                                                       code]))
                i += 1
                if i == max:
                    i = 0
