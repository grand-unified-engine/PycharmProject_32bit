# from datetime import datetime
import pandas as pd
import copy
from datetime import datetime
# from Kiwoom.quant.MariaDB import MarketDB
import FinanceDataReader as fdr

class DayCandleIndicator:
    def __init__(self, code):

        self.day_candle = pd.DataFrame()
        # self.mk = MarketDB(code)

        # self.pass_yn = False
        end_date = datetime.today().strftime('%Y-%m-%d')
        end_date = '2021-03-12' #과거꺼 테스트할 때만 사용
        # self.day_candle = self.mk.get_daily_price(code, start_date='2020-07-01', end_date=end_date)
        self.day_candle = fdr.DataReader(code, '2020-07-01', end_date)

        if len(self.day_candle['Close']) >= 20:
            self.day_candle['MA5'] = self.day_candle['Close'].rolling(window=5).mean()
            self.day_candle['MA10'] = self.day_candle['Close'].rolling(window=10).mean()
            self.day_candle['MA20'] = self.day_candle['Close'].rolling(window=20).mean()
            # self.day_candle['MA120'] = self.day_candle['Close'].rolling(window=120).mean()
            # self.day_candle['MA240'] = self.day_candle['Close'].rolling(window=240).mean()
            self.day_candle['MA10V'] = self.day_candle['Volume'].rolling(window=10).mean()

    '''
    전고점, 전저점 가져오기
    '''
    def get_max_min_close(self, start, end):
        try:
            copy_df = self.day_candle.copy()[end*-1:start*-1]

            max_high = max(copy_df['High']) #Start자르고 end개수 사이에서 max값을 구함
            max_Close = max(copy_df['Close'])
            min_close = min(copy_df['Close'])
            return max_high, max_Close, min_close
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

            org_df = self.day_candle

            df = pd.DataFrame()
            if len(org_df['Close']) > 20: # 20일 이평선을 이용해야 하므로
                df = org_df[['Close']].copy()

                df['center'] = df['Close'].rolling(n).mean()  # 중앙 이동평균선
                df['ub'] = df['center'] + sigma * df['Close'].rolling(n).std()  # 상단 밴드
                df['lb'] = df['center'] - sigma * df['Close'].rolling(n).std()  # 하단 밴드
                df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100
            return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None



if __name__ == "__main__":
    analy = Analyzer()
    mk = MarketDB()
    code = '024900'
    end_date = datetime.today().strftime('%Y-%m-%d')
    # end_date = '2021-02-16'
    df = mk.get_daily_price(code, end_date=end_date)
    final_df = df.sort_index(ascending=False)
    # print(final_df)


