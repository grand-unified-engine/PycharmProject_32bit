from datetime import date
import pandas as pd
import copy
from Kiwoom.quant.MariaDB import MarketDB
import FinanceDataReader as fdr
from Kiwoom.quant.CandleShape import candle_info

class DayCandleIndicator:
    def __init__(self, code):

        # self.day_candle = pd.DataFrame()
        self.mk = MarketDB(code)

        start_date = '2018-08-03'
        self.end_date = date.today()
        self.str_end_date = self.end_date.strftime('%Y-%m-%d')
        # self.end_date = '2021-04-02' #과거꺼 테스트할 때만 사용
        self.day_candle = self.mk.get_daily_price(code, start_date=start_date, end_date=self.str_end_date)
        # self.day_candle = fdr.DataReader(code, start_date, self.end_date)

        # self.color, self.rise_rate, self.body_rate, self.top_tail_rate, self.bottom_tail_rate = candle_info(self.day_candle['Open'].iloc[-2], self.day_candle['High'].iloc[-2], self.day_candle['Low'].iloc[-2], self.day_candle['Close'].iloc[-2])

        # print("color : {}, 상승률: {}, 몸통비율(전체대비): {}, 위꼬리비율: {}, 아래꼬리비율: {}".format(self.color, self.rise_rate, self.body_rate, self.top_tail_rate, self.bottom_tail_rate))

        if self.day_candle.empty is False:  # 비어 있지 않으면
            self.highlimit = self.day_candle['Close'].iloc[-2] * 1.298 # 상한가

        # if len(self.day_candle['Close']) >= 20:
        #     n = 20
        #     sigma = 2
        #     self.bollinger_band(n=n, sigma=sigma)
        #     self.day_candle['MA5'] = self.day_candle['Close'].rolling(window=5).mean()
        #     self.day_candle['MA10'] = self.day_candle['Close'].rolling(window=10).mean()
        #     self.day_candle['MA20'] = self.day_candle['Close'].rolling(window=20).mean()
        #     # self.day_candle['MA120'] = self.day_candle['Close'].rolling(window=120).mean()
        #     # self.day_candle['MA240'] = self.day_candle['Close'].rolling(window=240).mean()
        #     self.day_candle['MA10V'] = self.day_candle['Volume'].rolling(window=10).mean()



    '''
    전고점, 전저점 가져오기
    '''
    def get_max_min_close(self, start, end):
        try:
            copy_df = self.day_candle.copy()[end*-1:start*-1] #start만큼 최근일자를 자른다

            max_high = max(copy_df['High']) #Start자르고 end개수 사이에서 max값을 구함
            max_close = max(copy_df['Close'])
            min_close = min(copy_df['Close'])
            max_open = max(copy_df['Open'])

            max_day = copy_df.loc[copy_df['High'] == copy_df['High'][end * -1:].max()]
            min_day = copy_df.loc[copy_df['Close'] == copy_df['Close'][end * -1:].min()]
            # print(min_day)

            maxdayOpen = max_day['Open'][-1]
            maxdayHigh = max_day['High'][-1]
            maxdayLow = max_day['Low'][-1]
            maxdayClose = max_day['Close'][-1]

            # color, rise_rate, body_rate, top_tail_rate, bottom_tail_rate = candle_info(maxdayOpen, maxdayHigh, maxdayLow, maxdayClose)

            # return (maxdayClose + maxdayOpen) / 2, min_day['Close'][-1], min_day['bandwidth'][-1]
            return max_high, max_close, min_close, max_open
            # max_high = copy_df.loc[copy_df['High']==copy_df['High'][end*-1:].max()]
            # min_close = copy_df.loc[copy_df['Close'] == copy_df['Close'][end*-1:].min()]
            # return max_high, min_close

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_max_min_close() -> exception! {} ".format(str(ex)))
            return None

    '''
    이평선 기울기
    '''
    def get_ma_gradient(self, interval, index):
        try:
            df = self.day_candle

            global ma20_gradient
            global ma60_gradient
            if len(df['Close']) <= 20:  # 20일 이평선을 이용해야 하므로
                ma20_gradient = 0
            else:
                ma20_dpc = df['MA20'].pct_change(interval)
                ma20_gradient = ma20_dpc[index*-1] # D-1

            if len(df['Close']) <= 60:  # 60일 이평선을 이용해야 하므로
                ma60_gradient = 0
            else:
                df['MA60'] = df['Close'].rolling(window=60).mean()
                ma60_dpc = df['MA60'].pct_change(interval)
                ma60_gradient = ma60_dpc[index*-1] # D-1
                if -0.01 < round(ma60_gradient, 4) < 0:
                    ma60_gradient = 0

            return ma20_gradient, ma60_gradient

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_ma_gradient() -> exception! {} ".format(str(ex)))
            return None

    '''
    볼린저 밴드
    '''
    def bollinger_band(self, n, sigma):
        '''
        볼린저 밴드
        :param code:
        :return:
        '''
        try:
            df = self.day_candle

            df['center'] = df['Close'].rolling(n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['Close'].rolling(n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['Close'].rolling(n).std()  # 하단 밴드
            df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100
            # org_df = self.day_candle
            #
            # df = pd.DataFrame()
            # if len(org_df['Close']) > 20: # 20일 이평선을 이용해야 하므로
            #     df = org_df[['Close']].copy()
            #
            #     df['center'] = df['Close'].rolling(n).mean()  # 중앙 이동평균선
            #     df['ub'] = df['center'] + sigma * df['Close'].rolling(n).std()  # 상단 밴드
            #     df['lb'] = df['center'] - sigma * df['Close'].rolling(n).std()  # 하단 밴드
            #     df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100
            # return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None

    def get_demark(self): # Demark
        '''
        :param code:
        :return:
        '''
        try:
            d_high = 0
            d_low = 0
            # df = self.mk.get_daily_price(code)
            df = self.day_candle

            pre_open = int(df['Open'].shift(1).iloc[-1])
            pre_high = int(df['High'].shift(1).iloc[-1])
            pre_low = int(df['Low'].shift(1).iloc[-1])
            pre_close = int(df['Close'].shift(1).iloc[-1])

            '''
            if(predayclose()>predayopen(),
              (predayhigh()+predaylow()+predayclose()+predayhigh())/2-predaylow(),
              (if(predayclose()<predayopen(),
                  (predayhigh()+predaylow()+predayclose()+predaylow())/2-predaylow()
                  (predayhigh()+predaylow()+predayclose()+predayclose())/2-predaylow())
               )
            )
            '''
            if pre_close > pre_open :
                d_high = (pre_high  + pre_low  + pre_close  + pre_high )/ 2 - pre_low
            elif pre_close < pre_open :
                d_high = (pre_high  + pre_low  + pre_close  + pre_low )/ 2 - pre_low
            else:
                d_high = (pre_high + pre_low + pre_close + pre_close) / 2 - pre_low

            # print("d_high : {} ".format(d_high))

            '''
            if(predayclose()>predayopen(),
              (predayhigh()+predaylow()+predayclose()+predayhigh())/2-predayhigh(),
              (if(predayclose()<predayopen(),
                  (predayhigh()+predaylow()+predayclose()+predaylow())/2-predayhigh()
                  (predayhigh()+predaylow()+predayclose()+predayclose())/2-predayhigh())
                )
              )  
            '''
            #
            # if df['close'].shift(1) > df['open'].shift(1):
            #     d_low = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1) + df['high'].shift(1))/ 2 - df['high'].shift(1)
            # else:
            #     d_low = (df['high'].shift(1) + df['low'].shift(1) + df['close'].shift(1) + df['low'].shift(1))/ 2 - df['high'].shift(1)
            #
            # print("d_high : {} , d_high : {} ".format(d_high, d_high))

            return d_high

            # return d_high, d_high

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_get_demark() -> exception! {} ".format(str(ex)))
            return None

if __name__ == "__main__":
    code = '001380'
    d_high = DayCandleIndicator(code).get_demark()
    print(d_high)

