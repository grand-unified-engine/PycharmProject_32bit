import pandas as pd
from Kiwoom.quant.MinuteCandleIndicator import MinuteCandleIndicator
from Kiwoom.quant.DayCandleAlgorithm import DayCandleAlgorithm
import time


class MinuteCandleAlgorithm:
    def __init__(self, code):
        self.mIndicator = MinuteCandleIndicator(code)

    def buy(self, code, real_time_recommand_dict):

        if self.mIndicator.minute_df['bandwidth'].iloc[-2] < 2:
            if self.mIndicator.minute_df['min20'].iloc[-2] <= self.mIndicator.minute_df['체결가'].iloc[-2] <= self.mIndicator.minute_df['max20'].iloc[-2]:
                if self.mIndicator.minute_df['lb'].iloc[-2] <= self.mIndicator.minute_df['체결가'].iloc[-2] <= self.mIndicator.minute_df['ub'].iloc[-2]:
                    if self.mIndicator.minute_df['체결가'].iloc[-1] > self.mIndicator.minute_df['max20'].iloc[-2]:
                        if 1 <= self.mIndicator.minute_df['체결가'].iloc[-1] / (
                                self.mIndicator.minute_df['체결가'].iloc[-1] - self.mIndicator.minute_df['전일비'].iloc[-1]) < 1.2:
                            # print(self.mIndicator.minute_df['체결가'][index] / (self.mIndicator.minute_df['체결가'][index] - self.mIndicator.minute_df['전일비'][index]))
                            temp_df = pd.DataFrame(self.mIndicator.minute_df['체결가'].iloc[-15:].ge(
                                self.mIndicator.minute_df['center'].iloc[-15:]), columns=['20선비교'])
                            if temp_df[temp_df['20선비교'] == True].empty:
                                pass
                            if temp_df[temp_df['20선비교'] == False].empty:
                                pass
                            if int(temp_df[temp_df['20선비교'] == True]['20선비교'].value_counts()[True]) < 11:
                                dayAlgo = DayCandleAlgorithm(code)

                                if dayAlgo.pass_yn:
                                    print("매수가: {}, 시간: {} 살 타이밍".format(self.mIndicator.minute_df['체결가'].iloc[-1],
                                                                                 self.mIndicator.minute_df['체결시각'].iloc[-1]))
                                    real_time_recommand_dict.update(
                                        {code: {"time": time.strftime('%H%M%S'), "numbering": False}})
                                    print("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(code,
                                                                                               real_time_recommand_dict[
                                                                                                   code]))


if __name__ == "__main__":
    # start = timeit.default_timer()
    # main = BuyMinuteAlgorithm(code='021080')
    main = MinuteCandleAlgorithm(code='075970')