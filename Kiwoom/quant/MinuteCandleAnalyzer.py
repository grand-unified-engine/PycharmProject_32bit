import pandas as pd

class Analyzer():
    def __init__(self):

        self.minute_candle = pd.DataFrame()

    '''
    전고점, 전저점 가져오기
    '''
    def get_max_min_close(self, start, end):
        try:
            copy_df = self.minute_candle.copy()[:start*-1]

            max_high = max(copy_df['High'][end*-1:])
            min_close = min(copy_df['Close'][end*-1:])
            return max_high, min_close
            # max_close = copy_df.loc[copy_df['Close']==copy_df['Close'].max()]
            # return max['Close'].iloc[0]

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_max_min_close() -> exception! {} ".format(str(ex)))
            return None

    def bollinger_band(self, code, n, sigma): # 볼린저 밴드
        '''
        볼린저 밴드
        :param code:
        :return:
        '''
        try:
            org_df = self.minute_candle
            df = org_df[['체결가']].copy()

            df['center'] = df['Close'].rolling(n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['Close'].rolling(n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['Close'].rolling(n).std()  # 하단 밴드
            df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100

            return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None