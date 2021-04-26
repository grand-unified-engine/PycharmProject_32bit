from datetime import datetime
from Kiwoom.quant.DayCandleIndicator import DayCandleIndicator
# from Kiwoom.quant.MariaDB import MarketDB
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup


class DayCandleAlgorithm():
    def __init__(self, code):

        self.result_dict = {}

        self.dIndicator = DayCandleIndicator(code)

        # if self.long_decline():
        #     print("매수 코드: ", code)
        start = 1
        end = 20
        if len(self.dIndicator.day_candle['Close']) >= end:
            max_high, self.max_close, self.min_close, self.max_open = self.dIndicator.get_max_min_close(start=start, end=end)  # 고점일 때는 High값으로(저항선을 의미)
            # print("전고점: {}, 전저점: {}".format(self.max_open, self.min_close))  # 저점은 종가기준
        #     self.ma20_gradient, self.ma60_gradient = self.dIndicator.get_ma_gradient(interval=5, index=2)

    def long_decline(self):  # 장기하락
        self.result_dict.update({"long_decline": False})
        self.result_dict.update({"score": 0})

        # 10일 안 최저점 찾기
        start = 2
        end = 10
        if len(self.dIndicator.day_candle['Close']) >= 60:
            self.middle, min_close, bandwidth = self.dIndicator.get_max_min_close(start=start, end=end)
            # print(bandwidth)
            if self.dIndicator.day_candle['Close'][-60] > min_close: #하락
                if bandwidth < 14:
                    self.result_dict.update({"long_decline": True})

        return self.result_dict["long_decline"]

    def yesterday(self):  # 종가와 거래량
        self.result_dict.update({"yesterday": False})
        self.result_dict.update({"score": 0})

        # 10일 안 최저점 찾기
        start = 2
        end = 10
        if len(self.dIndicator.day_candle['Close']) >= end:
            self.middle, min_close = self.dIndicator.get_max_min_close(start=start, end=end)

            # print(self.middle, self.dIndicator.day_candle['Low'].iloc[-2])
            if self.dIndicator.color == 'blue': #테스트날
                if self.dIndicator.body_rate > 0.85:
                    if self.middle * 1.03 >= self.dIndicator.day_candle['Close'].iloc[-2] >= self.middle * 0.97:
                        self.result_dict.update({"yesterday": True})

        # if len(self.dIndicator.day_candle['Close']) >= 20:
        #     if self.dIndicator.day_candle['Close'][-2] > 1000:
        #         if max_vol > self.dIndicator.day_candle['MA10V'][-2] > 100000:
        #             self.result_dict.update({"vol_basic": True})
        #             self.result_dict.update({"score": 2})
        return self.result_dict["yesterday"]

    def basic(self, code): #기본 조건
        self.result_dict.update({"basic": False})
        self.result_dict.update({"score": 0})
        fs_url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{code}&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=701'

        req = requests.get(fs_url)
        soup = BeautifulSoup(req.text, 'html.parser')
        roe = soup.find("div", {"id": "svdMainGrid10D"}).find_all('table')[0].find_all('tr')[7].find_all('td')[0].text

        if roe != '완전잠식':
            self.result_dict.update({"basic": True})
            self.result_dict.update({"score": 2})
        return self.result_dict["basic"]

    def basic2(self, max_vol): #기본 조건
        self.result_dict.update({"basic": False})
        self.result_dict.update({"score": 0})

        if len(self.dIndicator.day_candle['Close']) >= 20:
            if self.dIndicator.day_candle['Close'][-2] > 1000:
                if max_vol > self.dIndicator.day_candle['MA10V'][-2] > 100000:
                    self.result_dict.update({"basic": True})
                    self.result_dict.update({"score": 2})
        return self.result_dict["basic"]

    # 20선 아래에서 20선으로 회귀
    def regression20MAbelow(self):
        self.result_dict.update({"regression20MAbelow": False})
        self.result_dict.update({"score": 0})
        # print("MA20 기울기: {}".format(round(ma20_gradient, 4)))
        if self.dIndicator.day_candle['Close'].pct_change(3)[-2] < 0: # D-2까지 하락
            if self.dIndicator.day_candle['Close'][-5] < self.dIndicator.day_candle['MA20'][-5]: # 20선 아래서 내려가다가
                if (self.dIndicator.day_candle['Close'][-6] < self.dIndicator.day_candle['MA20'][-6] < self.dIndicator.day_candle['Open'][-6]) or\
                    (self.dIndicator.day_candle['Close'][-6] > self.dIndicator.day_candle['MA20'][-6] > self.dIndicator.day_candle['Open'][-6]):
                    if self.dIndicator.day_candle['Close'][-2] > self.dIndicator.day_candle['Open'][-2]: #D-1 양봉
                        if self.dIndicator.day_candle['High'][-2] > self.dIndicator.day_candle['Close'][-2]: #D-1 위꼬리 양봉
                            if self.dIndicator.day_candle['High'][-2] < self.dIndicator.day_candle['MA20'][-2]: #D-1 고가가 20선 아래
                                self.result_dict.update({"regression20MAbelow": True})
                                self.result_dict.update({"score": 100})
        return self.result_dict["regression20MAbelow"]

    def accumulate(self): # 수렴
        self.result_dict.update({"accumulate": False})
        # D-1 종가가 전고점 근처에 있을 때
        # print("self.max_Close * 0.96: {}, self.dIndicator.day_candle['Close'][-2]: {}, self.max_Close * 1.02: {}".format(self.max_Close * 0.96, self.dIndicator.day_candle['Close'][-2],
        #                                                               self.max_Close * 1.02))
        if self.max_Close * 0.96 <= self.dIndicator.day_candle['Close'][-2] <= self.max_Close * 1.02:
            self.result_dict.update({"accumulate": True})
            # self.resistance()

        return self.result_dict["accumulate"]

    def resistance(self):
        self.result_dict.update({"resistance": False})
        max_high, max_Close, min_close = self.dIndicator.get_max_min_close(start=1, end=5)

        if self.dIndicator.day_candle['Close'].pct_change(4)[-2] < 0:
            if self.dIndicator.day_candle['Close'][-2] < self.dIndicator.day_candle['Open'][-2]:
                if (self.dIndicator.day_candle['Open'][-2] - self.dIndicator.day_candle['Close'][-2])/ (max_Close - min_close) < 0.06:
                    self.result_dict.update({"resistance": True})
                # print("큰봉 비율: {}, D-1 비율: {}, 비율: {}".format(max_Close - min_close, self.dIndicator.day_candle['Open'][-2] - self.dIndicator.day_candle['Close'][-2],
                #                                              (self.dIndicator.day_candle['Open'][-2] - self.dIndicator.day_candle['Close'][-2])/ (max_Close - min_close)))
        # print("max_high: {}, max_Close: {}, min_close: {}, pct_change: {}".format(max_high, max_Close,
        #                                                               min_close, self.dIndicator.day_candle['Close'].pct_change(4)))
        return self.result_dict["resistance"]

    # 저항선 뚫기 전
    def resistance2(self):
        # print((self.max_high - self.D1_close)/self.D1_close * 100)
        if self.dIndicator.day_candle['MA5'][-2] > self.dIndicator.day_candle['MA10'][-2] > self.dIndicator.day_candle['MA20'][-2]:  # 5, 10, 20 정배열
            if self.dIndicator.day_candle['Open'][-2] > self.dIndicator.day_candle['Close'][-2]:  # D-1 음봉일 때
                if self.dIndicator.day_candle['Close'][-2] >= self.dIndicator.day_candle['Close'][-3]:  # D-2종가보다 높으면
                    self.result_dict.update({"newhigh": True})
                    self.result_dict.update({"score": 100})
            else: # D-1 양봉일 때
                if self.dIndicator.day_candle['Close'][-2] >= self.dIndicator.day_candle['Close'][-3]:  # D-2종가보다 높으면
                    self.result_dict.update({"newhigh": True})
                    self.result_dict.update({"score": 100})
            # else: # 처음 전고점보다 한참 아래 있을 경우
            #     start = 10
            #     end = 60
            #     max_high, max_Close, min_close = self.dIndicator.get_max_min_close(start=start, end=end)  # 고점일 때는 High값으로(저항선을 의미)
            #     # print("전고점: {}, 전저점: {}, 종가(D-1): {}".format(max_high, min_close, self.dIndicator.day_candle['Close'][-2]))
            #
            #     if self.dIndicator.day_candle['Open'][-3] > self.dIndicator.day_candle['Close'][-3]:  # D-1 음봉일 때
            #         if self.dIndicator.day_candle['Close'][-3] < max_high < self.dIndicator.day_candle['Open'][-3]:  # 전고점이 캔들 중간값
            #             if self.dIndicator.day_candle['Close'][-2] >= self.dIndicator.day_candle['Close'][-3]:  # D-2종가보다 높으면
            #                 self.result_dict.update({"newhigh": True})
            #                 self.result_dict.update({"score": 100})
            #     else: # D-1 양봉일 때
            #         if self.dIndicator.day_candle['Low'][-3] < max_high < self.dIndicator.day_candle['High'][-3]:  # 전고점이 캔들 중간값
            #             if self.dIndicator.day_candle['Close'][-2] >= self.dIndicator.day_candle['Close'][-3]:  # D-2종가보다 높으면
            #                 self.result_dict.update({"newhigh": True})
            #                 self.result_dict.update({"score": 100})
        else:
            if self.dIndicator.day_candle['Close'][-2] > self.dIndicator.day_candle['Open'][-2]:  # D-1 양봉일 때
                if self.dIndicator.day_candle['Close'][-2] > self.dIndicator.day_candle['MA20'][-2] > self.dIndicator.day_candle['Low'][-2]:
                    self.result_dict.update({"newhigh": True})
                    self.result_dict.update({"score": 100})


if __name__ == "__main__":
    main = DayCandleAlgorithm(code='195990')


