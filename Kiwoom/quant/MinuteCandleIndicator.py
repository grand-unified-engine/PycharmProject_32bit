from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime as dt


class MinuteCandleIndicator:
    def __init__(self, code):

        self.temp_df = pd.DataFrame()
        self.minute_df = pd.DataFrame()

        self.session = requests.session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)' \
                                      'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;' \
                                  'q=0.9,image/webp,*/*;q=0.8'}

        self.df = None #분봉 크롤링 DataFrame

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
        yesterday = today - dt.timedelta(days=1)
        if dt.date.strftime(yesterday, '%A') == 'Sunday':
            yesterday = yesterday - dt.timedelta(days=2)
        self.minute_candle(code, "".join(str(yesterday).split("-")) + '153000')
        self.temp_df = self.temp_df.append(self.df)
        ########################################################################

        # 진짜 돌릴 때 풀기
        # if self.t_now.strftime('%Y-%m-%d %H:%M:%S') < self.t_9_22.strftime('%Y-%m-%d %H:%M:%S'): # 9시22분전까지만 portfolio_stock_dict에 D-1값 저장하므로
        #     yesterday = today - dt.timedelta(days=1)
        #     if dt.date.strftime(yesterday, '%A') == 'Sunday':
        #         yesterday = yesterday - dt.timedelta(days=2)
        #
        #     self.minute_candle(code, "".join(str(yesterday).split("-")) + '153000')
        #     self.temp_df = self.temp_df.append(self.df)

        self.minute_candle(code, "".join(str(today).split("-")) + '153000')
        self.temp_df = self.temp_df.append(self.df)

        self.minute_df = self.temp_df  # append는 새로 주소를 할당한다.

        if len(self.minute_df['체결가']) >= 20:
            # 1: 체결시각, 2:체결가, 3:전일비, 4:매도, 5:매수, 6:거래량, 7:변동량
            # self.minute_df['MA5'] = self.minute_df['체결가'].rolling(window=5).mean()  # 8
            # self.minute_df['MA10'] = self.minute_df['체결가'].rolling(window=10).mean() # 9
            self.minute_df['MA20'] = self.minute_df['체결가'].rolling(window=20).mean()  # 10
            # self.minute_df['average'] = self.minute_df['체결가'].rolling(window=10).sum() / 10 # 11
            # self.minute_df['max10'] = self.minute_df['체결가'].rolling(window=10).max()   # 12
            # self.minute_df['min10'] = self.minute_df['체결가'].rolling(window=10).min()  # 13
            # self.minute_df['max20'] = self.minute_df['체결가'].rolling(window=20).max()   # 14
            # self.minute_df['min20'] = self.minute_df['체결가'].rolling(window=20).min()  # 15

            n = 20
            sigma = 2
            self.bollinger_band(code=code, n=n, sigma=sigma)

            self.minute_df.reset_index(inplace=True)
            self.minute_df.drop(['index'], axis=1, inplace=True)  # inplace는 데이터프레임을 그대로 사용하고자 할 때

    def minute_candle(self, code, thistime):
        # 네이버에서 분봉은 일주일치 데이터 제공함 21.03.25 확인
        url = f'https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={thistime}'
        res = self.session.get(url, headers=self.headers)
        res.raise_for_status()
        html = BeautifulSoup(res.text, "html.parser")

        self.df = pd.DataFrame()
        pgrr = html.find('td', class_='pgRR')
        if pgrr is not None:
            s = str(pgrr.a['href']).split('=')
            last_page = s[-1]

            # if "".join(str(dt.date.today()).split("-")) + '153000' == thistime:
            #     if int(last_page) >= 3:
            #         last_page = 3

            for page in range(1, int(last_page) + 1):
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

    '''
    이전 거래량 최고점
    '''
    def get_max_vol_ago(self, now_index):
        try:
            copy_df = self.minute_df.copy()[now_index-10:now_index-1]

            max_vol = max(copy_df['변동량'])
            return max_vol
            # max_close = copy_df.loc[copy_df['Close']==copy_df['Close'].max()]
            # return max['Close'].iloc[0]

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_max_min() -> exception! {} ".format(str(ex)))
            return None

    def bollinger_band(self, code, n, sigma): # 볼린저 밴드
        '''
        볼린저 밴드
        :param code:
        :return:
        '''
        try:
            df = self.minute_df

            df['center'] = df['체결가'].rolling(n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['체결가'].rolling(n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['체결가'].rolling(n).std()  # 하단 밴드
            df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None

    '''
    이평선 기울기
    '''
    def get_ma_gradient(self, interval=5):
        try:
            df = self.minute_df

            global ma20_gradient
            global ma60_gradient
            if len(df['체결가']) <= 20:  # 20일 이평선을 이용해야 하므로
                ma20_gradient = 0
            else:
                ma20_dpc = df['MA20'].pct_change(interval)
                ma20_gradient = ma20_dpc[-2] # D-1

            if len(df['Close']) <= 60:  # 60일 이평선을 이용해야 하므로
                ma60_gradient = 0
            else:
                df['MA60'] = df['Close'].rolling(window=60).mean()
                ma60_dpc = df['MA60'].pct_change(interval)
                ma60_gradient = ma60_dpc[-2] # D-1
                if -0.01 < round(ma60_gradient, 4) < 0:
                    ma60_gradient = 0

            return ma20_gradient, ma60_gradient

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_ma_gradient() -> exception! {} ".format(str(ex)))
            return None