from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime, date, timedelta
from Kiwoom.quant.MinuteCandleAnalyzer import Analyzer

class MinuteAlgorithm():
    def __init__(self, code):
        self.m_analy = Analyzer()

        self.session = requests.session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)' \
                                 'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;' \
                             'q=0.9,image/webp,*/*;q=0.8'}

        self.df = None
        self.minute_df = self.m_analy.minute_candle

        self.datetime = datetime
        self.t_now = self.datetime.now()
        self.t_9_12 = self.t_now.replace(hour=9, minute=12, second=0, microsecond=0)

        today = date.today()
        # today = date.today() - timedelta(days=1)

        if self.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_9_12.strftime('%Y-%m-%d %H:%M:%S'): # 9시12분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - timedelta(days=1)

            self.minute_candle(code, "".join(str(yesterday).split("-")) + '153000')
            self.minute_df = self.minute_df.append(self.df)

        self.minute_candle(code, "".join(str(today).split("-")) + '153000')
        self.minute_df = self.minute_df.append(self.df)
        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean() #8
        self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean() # 9
        # self.minute_df['MA20'] = self.minute_df['체결가'].rolling(window=20).mean()  # 10
        # self.minute_df['MA60'] = self.minute_df['체결가'].rolling(window=60).mean()  # 11
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=3).sum() / 3 # 12
        # self.minute_df['상승률'] = (self.minute_df['체결가'] - self.minute_df['전일비']) / self.minute_df['체결가'] #9
        # self.minute_df['상한가'] = (self.minute_df['체결가'] - self.minute_df['전일비']) * 1.3 #10
        # self.minute_df['stddev'] = self.minute_df['체결가'].rolling(window=20).std() #11
        # self.minute_df['upper'] = self.minute_df['MA20'] + (self.minute_df['stddev'] * 2) #12
        # self.minute_df['upper_pct'] = self.minute_df['upper'].pct_change(5) #13
        # self.minute_df['lower'] = self.minute_df['MA20'] - (self.minute_df['stddev'] * 2) #14
        # self.minute_df['bandwidth'] = (self.minute_df['upper'] - self.minute_df['lower']) / self.minute_df['MA20'] * 100 #15

        # self.shoulder()

    # def shoulder(self): # 어깨에 판다
    #     self.result_dict.update({"shoulder": False})
    #     start = 2
    #     end = 5
    #     max_high, min_close = self.minAnaly.get_max_min_close(start=start, end=end)  # 고점일 때는 High값으로(저항선을 의미)
    #     print("전고점: {}, 전저점: {}, 종가(D-1): {}".format(max_high, min_close, self.D1_close))

        # buytiming_ma20 = 0
        # for row in self.minute_df.itertuples():
        #     if row[1] == '20210226 09:25':
        #         buytiming_ma20 = row[8]
        #     if row[1] > '20210226 09:25':  # 매수시간
        #         diff_close_ma20 = row[2] - buytiming_ma20 # 종가 - 매수할 때 ma20
        #
        #         if diff_close_ma20 < 0: # 종가가 매수 때 ma20보다 낮아졌을 때
        #             if (abs(diff_close_ma20) / row[2] * 100) > 0.6:
        #                 print("시간: {}, 매수할 때 ma20 - 종가: {}, 비율: {}".format(row[1], diff_close_ma20,
        #                                                                    abs(diff_close_ma20) / row[2] * 100))

    def minute_candle(self, code, thistime):

        url = f'https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={thistime}'
        res = self.session.get(url, headers=self.headers)
        res.raise_for_status()
        html = BeautifulSoup(res.text, "html.parser")

        self.df = pd.DataFrame()
        pgrr = html.find('td', class_='pgRR')
        if pgrr is not None:
            s = str(pgrr.a['href']).split('=')
            last_page = s[-1]

            for page in range(1, int(last_page)+1):
                pg_url = '{}&page={}'.format(url, page)
                res2 = self.session.get(pg_url, headers=self.headers)
                res2.raise_for_status()
                html2 = BeautifulSoup(res2.text, "html.parser")
                table = html2.find("table", {'class': "type2"})
                self.df = self.df.append(pd.read_html(str(table), header=0)[0])

            self.df = self.df.dropna()
            self.df = self.df.sort_values('체결시각')
            self.df['체결시각'] = self.df['체결시각'].apply(lambda x: thistime[:8] + ' ' + x)

        else:
            table = html.find("table", {'class': "type2"})
            self.df = self.df.append(pd.read_html(str(table), header=0)[0])
            self.df = self.df.dropna()
            # print(self.df)
