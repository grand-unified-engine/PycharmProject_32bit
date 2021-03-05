from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime, date, timedelta
from Kiwoom.quant.MinuteCandleAnalyzer import Analyzer

class SellMinuteAlgorithm():
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
        self.t_9_22 = self.t_now.replace(hour=9, minute=22, second=0, microsecond=0)

        today = date.today()
        # today = date.today() - timedelta(days=1)

        if self.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime('%Y-%m-%d %H:%M:%S'): # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - timedelta(days=1)

            minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
            self.minute_df = self.minute_df.append(self.df)

        minute_candle(self, code, "".join(str(today).split("-")) + '153000')
        self.minute_df = self.minute_df.append(self.df)
        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean() #8
        self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean() # 9
        self.minute_df['MA20'] = self.minute_df['체결가'].rolling(window=20).mean()  # 10
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=3).sum() / 3 # 11
        self.minute_df['max10'] = self.minute_df['체결가'].rolling(window=10).max()   # 12
        self.minute_df['min10'] = self.minute_df['체결가'].rolling(window=10).min()  # 13

class BuyMinuteAlgorithm():
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
        self.t_9_22 = self.t_now.replace(hour=9, minute=22, second=0, microsecond=0)

        today = date.today()
        # today = date.today() - timedelta(days=1)

        if self.datetime.now().strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime(
                '%Y-%m-%d %H:%M:%S'):  # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - timedelta(days=1)

            minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
            self.minute_df = self.minute_df.append(self.df)

        minute_candle(self, code, "".join(str(today).split("-")) + '153000')
        self.minute_df = self.minute_df.append(self.df)
        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean()  # 8
        self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean()  # 9
        self.minute_df['MA20'] = self.minute_df['체결가'].rolling(window=20).mean()  # 10
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=3).sum() / 3  # 11
        self.minute_df['max10'] = self.minute_df['체결가'].rolling(window=10).max()  # 12
        self.minute_df['min10'] = self.minute_df['체결가'].rolling(window=10).min()  # 13

        # 만족하면 담기
        # if self.analyzer_daily.get_side_by_side_rise(df) or self.analyzer_daily.get_disparity(df):
        #     top_data.append(row[0])


def minute_candle(self, code, thistime):
    print(thistime)
    url = f'https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={thistime}'
    res = self.session.get(url, headers=self.headers)
    res.raise_for_status()
    html = BeautifulSoup(res.text, "html.parser")

    self.df = pd.DataFrame()
    pgrr = html.find('td', class_='pgRR')
    if pgrr is not None:
        s = str(pgrr.a['href']).split('=')
        last_page = s[-1]

        if "".join(str(date.today()).split("-")) + '153000' == thistime:
            if int(last_page) >= 3:
                last_page = 3

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

