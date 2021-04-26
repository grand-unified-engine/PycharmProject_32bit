import pandas as pd
import numpy as np
from Kiwoom.quant.MinuteCandleIndicator import MinuteCandleIndicator
from Kiwoom.quant.DayCandleAlgorithm import DayCandleAlgorithm
import time
import datetime as dt
from PyQt5.QtTest import QTest

class MinuteCandleAlgorithm:
    def __init__(self, code, code_name):

        self.mIndicator = None

        self.dayAlgo = DayCandleAlgorithm(code)

        # self.assist_dict = dict()
        #
        # self.real_time_recommand_dict = real_time_recommand_dict
        #
        # 요일체크
        today = dt.date.today()
        if dt.date.strftime(today, '%A') == 'Sunday':
            today = today - dt.timedelta(days=2)
        elif dt.date.strftime(today, '%A') == 'Saturday':
            today = today - dt.timedelta(days=1)

        self.buy210424_238090(code=code, code_name=code_name, today="".join(str(today).split("-")))

        # print("code: {}, ma20_gradient: {}, ma60_gradient: {}".format(code, self.dayAlgo.ma20_gradient,
        #                                                               self.dayAlgo.ma60_gradient))
        # if self.dayAlgo.ma20_gradient < -0.004:
        #     self.buy210312_025880(code=code, today="".join(str(today).split("-")))
        # elif self.dayAlgo.ma20_gradient < 0.09:
        #     self.buy210312_189980(code=code, today="".join(str(today).split("-")))
        # elif self.dayAlgo.ma20_gradient < 0.12:
        #     self.buy210312_068290(code=code, today="".join(str(today).split("-")))

    def buy210424_238090(self, code, code_name, today):
            self.mIndicator = MinuteCandleIndicator(code)
            for i, index in enumerate(self.mIndicator.minute_df.index):
                if self.mIndicator.minute_df['체결시각'][index].split(" ")[0] == today: # 실제로 돌릴 때는 주석처리?
                    if self.mIndicator.minute_df['체결가'][index] > (self.dayAlgo.max_close * 1.02):
                        if self.mIndicator.minute_df['변동량'][index] > self.mIndicator.get_max_vol_ago(i): #거래량이 최근 max값보다 높을 때
                            if self.mIndicator.minute_df['체결가'][index] > self.mIndicator.minute_df['체결가'][index-1]:
                                self.buy_timing = self.mIndicator.minute_df['체결시각'][index]
                                print("종목코드: {}, 종목명: {}. 매수가: {}, 체결시각: {}".format(code, code_name, self.mIndicator.minute_df['체결가'][index], self.mIndicator.minute_df['체결시각'][index]))
                                break
            self.shoulder(code=code, code_name=code_name, buy_time=self.mIndicator.minute_df['체결시각'][index],
                                                                          buy_price=self.mIndicator.minute_df['체결가'][index])
                # if self.mIndicator.minute_df['체결시각'][index] > self.buy_timing:




    def buy210420_037440(self, code, today): # 거래량 분봉기준 5만 이상
            self.mIndicator = MinuteCandleIndicator(code)
            for i, index in enumerate(self.mIndicator.minute_df.index):
                if self.mIndicator.minute_df['체결시각'][index].split(" ")[0] == today:
                    if self.mIndicator.minute_df['변동량'][index] > 50000:
                        print("종목: {}, 거래량증가시간: {}".format(code, self.mIndicator.minute_df['체결시각'][index]))
                        break

    def buy210312_025880(self, code, today):
        if self.dayAlgo.basic2(max_vol=1000000): #백만
            if self.dayAlgo.regression20MAbelow():
                self.mIndicator = MinuteCandleIndicator(code)
                for i, index in enumerate(self.mIndicator.minute_df.index):
                    if self.mIndicator.minute_df['체결시각'][index].split(" ")[0] == today:
                        if self.mIndicator.minute_df['체결시각'][index] == "20210312 09:38":
                            self.shoulder(code=code, buy_time=self.mIndicator.minute_df['체결시각'][index], buy_price=self.mIndicator.minute_df['ub'][index])

    def buy210312_189980(self, code, today):
        if self.dayAlgo.basic2(max_vol=15000000): #천오백만
            if self.dayAlgo.accumulate():
                self.mIndicator = MinuteCandleIndicator(code)
                QTest.qWait(3000)
                # print("분봉: {}".format(self.mIndicator.minute_df))
                self.assist_dict.update({'갭상승': False})
                first_time = np.where(self.mIndicator.minute_df['체결시각'] == today + " 09:00")[0]
                # print("첫: {}".format(self.mIndicator.minute_df.loc[first_time, '체결가'].iloc[-1]))
                if self.mIndicator.minute_df.loc[first_time, '체결가'].iloc[-1] > self.dayAlgo.dIndicator.day_candle['Close'][-2]:
                    self.assist_dict.update({'갭상승': True})
                    self.assist_dict.update({'첫봉갭상승률': self.mIndicator.minute_df.loc[first_time, '체결가'].iloc[-1] / (
                                self.mIndicator.minute_df.loc[first_time, '체결가'].iloc[-1] - self.mIndicator.minute_df.loc[first_time, '전일비'].iloc[-1])})
                    if '갭상승' in self.assist_dict and '첫봉갭상승률' in self.assist_dict:
                        if self.assist_dict['갭상승']:
                            if self.mIndicator.minute_df['체결시각'].iloc[-1] > self.mIndicator.minute_df['체결시각'].iloc[-2]:
                                if self.assist_dict['첫봉갭상승률'] < 1.03:
                                    ma10_dpc = self.mIndicator.minute_df['MA10'].pct_change(3)
                                    if int(ma10_dpc.iloc[-1]) > 0:
                                        if self.mIndicator.minute_df['MA10'].iloc[-1] < self.mIndicator.minute_df['체결가'].iloc[-1] < self.mIndicator.minute_df['ub'].iloc[-1]:
                                            print("매수가: {}, 시간: {} 살 타이밍".format(
                                                self.mIndicator.minute_df['체결가'].iloc[-1],
                                                self.mIndicator.minute_df['체결시각'].iloc[-1]))
                                            self.real_time_recommand_dict.update(
                                                {code: {"time": time.strftime('%H%M%S'), "numbering": False}})
                                            print("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(code,
                                                                                                       self.real_time_recommand_dict[
                                                                                                           code]))
                                elif self.assist_dict['첫봉갭상승률'] < 1.1:
                                    ma5_dpc = self.mIndicator.minute_df['MA5'].pct_change(5)
                                    if ma5_dpc.iloc[-1] < 0:
                                        if self.mIndicator.minute_df['체결가'].iloc[-4] > self.mIndicator.minute_df['체결가'].iloc[-3] > self.mIndicator.minute_df['체결가'].iloc[-2]:
                                            if self.mIndicator.minute_df['체결가'].iloc[-1] > self.mIndicator.minute_df['체결가'].iloc[-2]:
                                                if self.mIndicator.minute_df['체결가'][-10:0].max() > self.mIndicator.minute_df['체결가'].iloc[-1] > self.mIndicator.minute_df['체결가'][-10:0].min():
                                                    print("코드: {}, 매수가: {}, 시간: {} 살 타이밍".format(code,
                                                                                                 self.mIndicator.minute_df[
                                                                                                     '체결가'].iloc[-1],
                                                                                                 self.mIndicator.minute_df[
                                                                                                     '체결시각'].iloc[-1]))
                                                    self.real_time_recommand_dict.update(
                                                        {code: {"time": time.strftime('%H%M%S'), "numbering": False}})
                                                    print("새로 들어온 종목: {}, real_time_recommand_dict: {}".format(code,
                                                                                                               self.real_time_recommand_dict[
                                                                                                                   code]))


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

    def shoulder(self, code, code_name, buy_time, buy_price): # 어깨에 판다
        for i, index in enumerate(self.mIndicator.minute_df.index):
            if self.mIndicator.minute_df['체결가'][index] > self.dayAlgo.dIndicator.highlimit: # 당일 상한가 - 반영
                print("종목코드: {}, 종목명: {}, 매도가: {}, 시간: {} 팔 타이밍, bandwidth: {}".format(code, code_name, self.mIndicator.minute_df['체결가'][index], self.mIndicator.minute_df['체결시각'][index], self.mIndicator.minute_df['bandwidth'][index]))
                print("수익률: {}%".format((self.mIndicator.minute_df['체결가'][index] - buy_price) / buy_price * 100))
                break
            else:
                if self.mIndicator.minute_df['체결시각'][index] > buy_time: # 매수시간 이후(테스트용)
                    if self.mIndicator.minute_df['체결가'][index] > self.dayAlgo.max_open:
                        if self.mIndicator.minute_df['체결가'][index] < self.mIndicator.minute_df['ub'][index]: # 고가에 팔기
                            if self.mIndicator.minute_df['체결가'][index] < self.mIndicator.minute_df['체결가'][index - 1]:
                                if self.mIndicator.minute_df['bandwidth'][index] > 16:
                                    if self.mIndicator.minute_df['체결가'][index] > self.mIndicator.minute_df['MA20'][index]:
                                        pass
                                    else:
                                        print("종목코드: {}, 종목명: {}, 매도가: {}, 시간: {} 팔 타이밍, bandwidth: {}".format(code, code_name, self.mIndicator.minute_df['체결가'][index], self.mIndicator.minute_df['체결시각'][index], self.mIndicator.minute_df['bandwidth'][index]))
                                        print("수익률: {}%".format((self.mIndicator.minute_df['체결가'][index] - buy_price) / buy_price * 100))
                                        break
                    else: #손절
                        if (self.mIndicator.minute_df['체결가'][index] - buy_price) / buy_price * 100 < -5:
                            print("종목코드: {}, 종목명: {}, 매도가: {}, 시간: {} 팔 타이밍, bandwidth: {}".format(code, code_name, self.mIndicator.minute_df[
                                '체결가'][index], self.mIndicator.minute_df['체결시각'][index], self.mIndicator.minute_df[
                                                                                            'bandwidth'][index]))
                            print("수익률: {}%".format(
                                (self.mIndicator.minute_df['체결가'][index] - buy_price) / buy_price * 100))
                            break

if __name__ == "__main__":
    # start = timeit.default_timer()
    # main = BuyMinuteAlgorithm(code='021080')
    main = MinuteCandleAlgorithm(code='189980')