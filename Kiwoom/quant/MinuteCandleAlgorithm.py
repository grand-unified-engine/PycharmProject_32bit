import pandas as pd
import FinanceDataReader as fdr
import time

class MinuteCandleAlgorithm:
    def __init__(self):

        self.minute_candle = pd.DataFrame()

    def buy(self, code, real_time_recommand_dict):
        if self.minute_candle['bandwidth'].iloc[-2] < 2:
            if self.minute_candle['min20'].iloc[-2] <= self.minute_candle['체결가'].iloc[-2] <= self.minute_candle['max20'].iloc[-2]:
                if self.minute_candle['lb'].iloc[-2] <= self.minute_candle['체결가'].iloc[-2] <= self.minute_candle['ub'].iloc[-2]:
                    if self.minute_candle['체결가'].iloc[-1] > self.minute_candle['max20'].iloc[-2]:
                        if 1 <= self.minute_candle['체결가'].iloc[-1] / (
                                self.minute_candle['체결가'].iloc[-1] - self.minute_candle['전일비'].iloc[-1]) < 1.2:
                            # print(self.minute_candle['체결가'][index] / (self.minute_candle['체결가'][index] - self.minute_candle['전일비'][index]))
                            temp_df = pd.DataFrame(self.minute_candle['체결가'].iloc[-15:].ge(
                                self.minute_candle['center'].iloc[-15:]), columns=['20선비교'])
                            if temp_df[temp_df['20선비교'] == True].empty:
                                pass
                            if temp_df[temp_df['20선비교'] == False].empty:
                                pass
                            if int(temp_df[temp_df['20선비교'] == True].value_counts()[True]) < 11:
                                print("매수가: {}, 시간: {} 살 타이밍".format(self.minute_candle['체결가'].iloc[-1],
                                                                             self.minute_candle['체결시각'].iloc[-1]))
                                real_time_recommand_dict.update(
                                    {code: {"time": time.strftime('%H%M%S'), "numbering": False}})
                                print("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(code,
                                                                                           real_time_recommand_dict[
                                                                                               code]))

