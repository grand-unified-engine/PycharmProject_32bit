from datetime import datetime
from Kiwoom.quant.DayCandleAnalyzer import Analyzer
# from Kiwoom.quant.MariaDB import MarketDB
import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup


class DayAlgorithm():
    def __init__(self, code):

        self.dayAnaly = Analyzer()
        # self.mk = MarketDB(code)

        self.pass_yn = False
        end_date = datetime.today().strftime('%Y-%m-%d')
        # end_date = '2021-02-24' #과거꺼 테스트할 때만 사용
        # self.dayAnaly.day_candle = self.mk.get_daily_price(code, start_date='2020-07-01', end_date=end_date)
        self.dayAnaly.day_candle = fdr.DataReader(code, '2020-07-01', end_date)

        self.day_df = self.dayAnaly.day_candle

        if len(self.day_df['Close']) >= 20:
            self.day_df['MA5'] = self.day_df['Close'].rolling(window=5).mean()
            self.day_df['MA10'] = self.day_df['Close'].rolling(window=10).mean()
            self.day_df['MA20'] = self.day_df['Close'].rolling(window=20).mean()
            self.day_df['D3OPENMIN'] = self.day_df['Open'].rolling(window=3).min()
            # self.day_df['MA120'] = self.day_df['Close'].rolling(window=120).mean()
            # self.day_df['MA240'] = self.day_df['Close'].rolling(window=240).mean()
            self.day_df['MA20V'] = self.day_df['Volume'].rolling(window=20).mean()

            self.D1_close = self.day_df['Close'].iloc[-2]

            self.result_dict = {}

            if self.basic(code):
                if self.newhigh():
                    self.pass_yn = True

            # self.regression(code)
            # print("결과dict : {}, 판단시간 : {}".format(self.result_dict, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        # print("최종결과: {}".format(self.pass_yn))

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

    def newhigh(self): # 신고가
        self.result_dict.update({"newhigh": False})
        start = 5
        end = 120
        self.max_high, self.min_close = self.dayAnaly.get_max_min_close(start=start, end=end) # 고점일 때는 High값으로(저항선을 의미)
        # print("전고점: {}, 전저점: {}, 종가(D-1): {}".format(self.max_high, self.min_close, self.D1_close)) # 저점은 종가기준

        interval = 5
        ma20_gradient, ma60_gradient = self.dayAnaly.get_ma_gradient(interval) # D-1 이평선 기울기 확인
        # print("20일선(D-1) 기울기 : {}".format(ma20_gradient))

        if ma20_gradient >= 0: # 20일선이 상승일 때만 저항선 판단
            if self.max_high - self.D1_close > 0: # 전고점 아래 있을 경우
                self.resistance()

        return self.result_dict["newhigh"]

    # 저항선 뚫기 전
    def resistance(self):
        # print((self.max_high - self.D1_close)/self.D1_close * 100)
        if self.day_df['MA5'][-2] > self.day_df['MA10'][-2] > self.day_df['MA20'][-2]:  # 5, 10, 20 정배열

            if ((self.max_high - self.D1_close)/self.D1_close * 100) < 13:

                if self.day_df['Open'][-2] > self.day_df['Close'][-2]:  # D-1 음봉일 때
                    if self.day_df['Close'][-2] < self.max_high < self.day_df['Open'][-2]:  # 전고점이 캔들 중간값
                        if self.day_df['Close'][-2] >= self.day_df['Close'][-3]:  # D-2종가보다 높으면
                            self.result_dict.update({"newhigh": True})
                            self.result_dict.update({"score": 100})
                else: # D-1 양봉일 때
                    if self.day_df['Low'][-2] < self.max_high < self.day_df['High'][-2]:  # 전고점이 캔들 중간값
                        if self.day_df['Close'][-2] >= self.day_df['Close'][-3]:  # D-2종가보다 높으면
                            self.result_dict.update({"newhigh": True})
                            self.result_dict.update({"score": 100})
            else: # 처음 전고점보다 한참 아래 있을 경우
                start = 10
                end = 60
                max_high, min_close = self.dayAnaly.get_max_min_close(start=start, end=end)  # 고점일 때는 High값으로(저항선을 의미)
                # print("전고점: {}, 전저점: {}, 종가(D-1): {}".format(max_high, min_close, self.D1_close))

                if self.day_df['Open'][-3] > self.day_df['Close'][-3]:  # D-1 음봉일 때
                    if self.day_df['Close'][-3] < max_high < self.day_df['Open'][-3]:  # 전고점이 캔들 중간값
                        if self.day_df['Close'][-2] >= self.day_df['Close'][-3]:  # D-2종가보다 높으면
                            self.result_dict.update({"newhigh": True})
                            self.result_dict.update({"score": 100})
                else: # D-1 양봉일 때
                    if self.day_df['Low'][-3] < max_high < self.day_df['High'][-3]:  # 전고점이 캔들 중간값
                        if self.day_df['Close'][-2] >= self.day_df['Close'][-3]:  # D-2종가보다 높으면
                            self.result_dict.update({"newhigh": True})
                            self.result_dict.update({"score": 100})
        else:
            if self.day_df['Close'][-2] > self.day_df['Open'][-2]:  # D-1 양봉일 때
                if self.day_df['Close'][-2] > self.day_df['MA20'][-2] > self.day_df['Low'][-2]:
                    self.result_dict.update({"newhigh": True})
                    self.result_dict.update({"score": 100})


    # def regression(self, code):
    #     if self.day_df['Close'].iloc[-2] > self.day_df['MA20'].iloc[-2]: # 20일선 위에 있는데
    #         if self.day_df['MA60'].iloc[-2] < self.day_df['Close'].iloc[-2]: # 60일선이 아래서 잡아당기려고 할 때
    #             print("60일선이 아래서 잡아당긴다")
    #             self.pass_yn = False


if __name__ == "__main__":
    main = DayAlgorithm(code='126560')


