from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime as dt
from Kiwoom.quant.MinuteCandleAlgorithm import MinuteCandleAlgorithm
from Kiwoom.quant.MinuteCandleIndicator import MinuteCandleIndicator


class MinuteCandleController:
    def __init__(self, code):
        self.mAlgo = MinuteCandleAlgorithm()

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
        #     yesterday = yesterday - dt.timedelta(days=2)
        # minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
        # self.m_analy.minute_candle = self.m_analy.minute_candle.append(self.df)
        ########################################################################

        # 진짜 돌릴 때 풀기
        if self.t_now.strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime('%Y-%m-%d %H:%M:%S'): # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
            yesterday = today - dt.timedelta(days=1)
            if dt.date.strftime(yesterday, '%A') == 'Sunday':
                yesterday = yesterday - dt.timedelta(days=2)

            minute_candle(self, code, "".join(str(yesterday).split("-")) + '153000')
            self.mAlgo.minute_candle = self.mAlgo.minute_candle.append(self.df)

        minute_candle(self, code, "".join(str(today).split("-")) + '153000')
        self.mAlgo.minute_candle = self.mAlgo.minute_candle.append(self.df)

        self.minute_df = self.mAlgo.minute_candle  # append는 새로 주소를 할당한다.

        # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
        self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean()  # 8
        self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean()  # 9
        self.minute_df['average'] = self.minute_df['체결가'].rolling(window=10).sum() / 10  # 10
        self.minute_df['max20'] = self.minute_df['체결가'].rolling(window=20).max()  # 11
        self.minute_df['min20'] = self.minute_df['체결가'].rolling(window=20).min()  # 12

        self.mIndicator = MinuteCandleIndicator(self.minute_df)

        n = 20
        sigma = 2
        self.mIndicator.bollinger_band(code=code, n=n, sigma=sigma)

        self.mAlgo.buy()


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
    main = MinuteCandleController(code='075970')
