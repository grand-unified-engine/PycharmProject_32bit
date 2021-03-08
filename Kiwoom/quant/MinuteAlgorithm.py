from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime as dt
from Kiwoom.quant.MinuteCandleAnalyzer import Analyzer
from Kiwoom.config.log_class import Logging

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

        # 시분초
        self.t_now = dt.datetime.now()
        self.t_9_22 = self.t_now.replace(hour=9, minute=22, second=0, microsecond=0)

        # 요일체크
        today = dt.date.today()
        if dt.date.strftime(today, '%A') == 'Sunday':
            today = today - dt.timedelta(days=2)
        elif dt.date.strftime(today, '%A') == 'Saturday':
            today = today - dt.timedelta(days=1)

        ###### 테스트용 ##########################################################
        # yesterday = today - dt.timedelta(days=1)
        # if dt.date.strftime(yesterday, '%A') == 'Sunday':
        #     yesterday = today - dt.timedelta(days=2)
        # elif dt.date.strftime(yesterday, '%A') == 'Saturday':
        #     yesterday = today - dt.timedelta(days=1)
        # minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
        # self.minute_df = self.minute_df.append(self.df)
        ########################################################################

        # 진짜 돌릴 때 풀기
        if self.t_now.strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime('%Y-%m-%d %H:%M:%S'): # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - dt.timedelta(days=1)
            if dt.date.strftime(yesterday, '%A') == 'Sunday':
                yesterday = today - dt.timedelta(days=2)
            elif dt.date.strftime(yesterday, '%A') == 'Saturday':
                yesterday = today - dt.timedelta(days=1)

            minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
            self.minute_df = self.minute_df.append(self.df)

        minute_candle(self, code, "".join(str(today).split("-")) + '153000')
        self.minute_df = self.minute_df.append(self.df)
        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean()  # 8
        self.minute_df['MA20'] = self.minute_df['체결가'].rolling(window=20).mean() # 9
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=10).sum() / 10 # 10
        self.minute_df['max10'] = self.minute_df['체결가'].rolling(window=10).max()   # 11
        self.minute_df['min10'] = self.minute_df['체결가'].rolling(window=10).min()  # 12


class BuyMinuteAlgorithm():
    def __init__(self, code):
        self.m_analy = Analyzer()
        self.logging = Logging()

        self.session = requests.session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)' \
                                      'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;' \
                                  'q=0.9,image/webp,*/*;q=0.8'}

        self.df = None

        # 시분초
        self.t_now = dt.datetime.now()
        self.t_9_22 = self.t_now.replace(hour=9, minute=22, second=0, microsecond=0)

        # 요일체크
        today = dt.date.today()
        if dt.date.strftime(today, '%A') == 'Sunday':
            today = today - dt.timedelta(days=2)
        elif dt.date.strftime(today, '%A') == 'Saturday':
            today = today - dt.timedelta(days=1)

        ###### 테스트용 ##########################################################
        # yesterday = today - dt.timedelta(days=1)
        # if dt.date.strftime(yesterday, '%A') == 'Sunday':
        #     yesterday = today - dt.timedelta(days=2)
        # elif dt.date.strftime(yesterday, '%A') == 'Saturday':
        #     yesterday = today - dt.timedelta(days=1)
        # minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
        # self.m_analy.minute_candle = self.m_analy.minute_candle.append(self.df)
        ########################################################################

        # 진짜 돌릴 때 풀기
        if self.t_now.strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime('%Y-%m-%d %H:%M:%S'): # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - dt.timedelta(days=1)
            if dt.date.strftime(yesterday, '%A') == 'Sunday':
                yesterday = today - dt.timedelta(days=2)
            elif dt.date.strftime(yesterday, '%A') == 'Saturday':
                yesterday = today - dt.timedelta(days=1)

            minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
            self.m_analy.minute_candle = self.m_analy.minute_candle.append(self.df)

        minute_candle(self, code, "".join(str(today).split("-")) + '153000')
        self.m_analy.minute_candle = self.m_analy.minute_candle.append(self.df)

        self.minute_df = self.m_analy.minute_candle  # append는 새로 주소를 할당한다.

        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean()  # 8
        self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean()  # 9
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=10).sum() / 10  # 10
        self.minute_df['max20'] = self.minute_df['체결가'].rolling(window=20).max()  # 11
        self.minute_df['min20'] = self.minute_df['체결가'].rolling(window=20).min()  # 12

        n = 20
        sigma = 2
        self.m_analy.bollinger_band(code=code, n=n, sigma=sigma)

        # self.minute_df.reset_index(inplace=True)
        # self.minute_df.drop(['index'], axis=1, inplace=True)  # inplace는 데이터프레임을 그대로 사용하고자 할 때

        self.buy()

    def shoulder(self, code, buy_time, buy_price):  # 어깨에 판다
        for i, index in enumerate(self.minute_df.index):
            if self.minute_df['체결시각'][index] > buy_time:  # 매수시간 이후(테스트용)
                if self.minute_df['체결가'][index] > buy_price:
                    if self.minute_df['체결가'][index - 1] < self.minute_df['ub'][index - 1]:  # 고가에 팔기
                        if self.minute_df['체결가'][index] < self.minute_df['체결가'][index - 1]:
                            if self.minute_df['bandwidth'][index] > 28:
                                print("코드: {}, 매도가: {}, 시간: {} 팔 타이밍, bandwidth: {}".format(code,
                                                                                            self.minute_df['체결가'][
                                                                                                index],
                                                                                            self.minute_df['체결시각'][
                                                                                                index],
                                                                                            self.minute_df[
                                                                                                'bandwidth'][
                                                                                                index]))
                                print(
                                    "수익률: {}%".format((self.minute_df['체결가'][index] - buy_price) / buy_price * 100))
                                # print("지수이평5: {}".format(self.minute_df['지수이평5'][index]))
                                # print("지수이평10: {}".format(self.minute_df['지수이평10'][index]))
                                # print("지수이평20: {}".format(self.minute_df['지수이평20'][index]))
                                # print("지수이평60: {}".format(self.minute_df['지수이평60'][index]))
                                break

    def buy(self):
        if self.minute_df['bandwidth'].iloc[-2] < 2:
            if self.minute_df['min20'].iloc[-2] <= self.minute_df['체결가'].iloc[-2] <= self.minute_df['max20'].iloc[-2]:
                if self.minute_df['lb'].iloc[-2] <= self.minute_df['체결가'].iloc[-2] <= self.minute_df['ub'].iloc[-2]:
                    if self.minute_df['체결가'].iloc[-1] > self.minute_df['max20'].iloc[-2]:
                        if 1 <= self.minute_df['체결가'].iloc[-1] / (
                                self.minute_df['체결가'].iloc[-1] - self.minute_df['전일비'].iloc[-1]) < 1.2:
                            # print(self.minute_df['체결가'][index] / (self.minute_df['체결가'][index] - self.minute_df['전일비'][index]))
                            temp_df = pd.DataFrame(self.minute_df['체결가'].iloc[-15:].ge(
                                self.minute_df['center'].iloc[-15:]), columns=['20선비교'])
                            if temp_df[temp_df['20선비교'] == True].empty:
                                pass
                            if temp_df[temp_df['20선비교'] == False].empty:
                                pass
                            if int(temp_df[temp_df['20선비교'] == True].value_counts()[True]) < 11:
                                self.logging.logger.debug("매수가: {}, 시간: {} 살 타이밍".format(self.minute_df['체결가'].iloc[-1],
                                                                             self.minute_df['체결시각'].iloc[-1]))



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

        # if "".join(str(date.today()).split("-")) + '153000' == thistime:
        #     if int(last_page) >= 3:
        #         last_page = 3

        for page in range(1, int(last_page)+1):
            pg_url = '{}&page={}'.format(url, page)
            res2 = self.session.get(pg_url, headers=self.headers)
            res2.raise_for_status()
            html2 = BeautifulSoup(res2.text, "html.parser")
            table = html2.find("table", {'class': "type2"})
            imgs = table.findAll('img')
            for i in imgs:
                if i.findNext('span', {'class': "nv01"}):
                    i.findNext('span').string.replace_with('-' + i.findNext('span').string.strip())
            self.df = self.df.append(pd.read_html(str(table), header=0)[0])

        self.df = self.df.dropna()
        self.df = self.df.sort_values('체결시각')
        self.df['체결시각'] = self.df['체결시각'].apply(lambda x: thistime[:8] + ' ' + x)

    else:
        table = html.find("table", {'class': "type2"})
        imgs = table.findAll('img')
        for i in imgs:
            if i.findNext('span', {'class': "nv01"}):
                i.findNext('span').string.replace_with('-' + i.findNext('span').string.strip())
        self.df = self.df.append(pd.read_html(str(table), header=0)[0])
        self.df = self.df.dropna()
        self.df = self.df.sort_values('체결시각')
        self.df['체결시각'] = self.df['체결시각'].apply(lambda x: thistime[:8] + ' ' + x)

if __name__ == "__main__":
    # start = timeit.default_timer()
    # main = BuyMinuteAlgorithm(code='021080')
    main = SellMinuteAlgorithm(code='021080')
