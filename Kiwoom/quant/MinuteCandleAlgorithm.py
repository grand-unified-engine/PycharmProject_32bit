import pandas as pd
import FinanceDataReader as fdr


class MinuteCandleAlgorithm:
    def __init__(self):

        self.minute_candle = pd.DataFrame()

    def buy(self):
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


    def shoulder(self, code, buy_time, buy_price):  # 어깨에 판다
        for i, index in enumerate(self.minute_candle.index):
            if self.minute_candle['체결시각'][index] > buy_time:  # 매수시간 이후(테스트용)
                if self.minute_candle['체결가'][index] > buy_price:
                    if self.minute_candle['체결가'][index - 1] < self.minute_candle['ub'][index - 1]:  # 고가에 팔기
                        if self.minute_candle['체결가'][index] < self.minute_candle['체결가'][index - 1]:
                            if self.minute_candle['bandwidth'][index] > 28:
                                print("코드: {}, 매도가: {}, 시간: {} 팔 타이밍, bandwidth: {}".format(code,
                                                                                            self.minute_candle['체결가'][
                                                                                                index],
                                                                                            self.minute_candle['체결시각'][
                                                                                                index],
                                                                                            self.minute_candle[
                                                                                                'bandwidth'][
                                                                                                index]))
                                print(
                                    "수익률: {}%".format((self.minute_candle['체결가'][index] - buy_price) / buy_price * 100))
                                # print("지수이평5: {}".format(self.minute_candle['지수이평5'][index]))
                                # print("지수이평10: {}".format(self.minute_candle['지수이평10'][index]))
                                # print("지수이평20: {}".format(self.minute_candle['지수이평20'][index]))
                                # print("지수이평60: {}".format(self.minute_candle['지수이평60'][index]))
                                break
