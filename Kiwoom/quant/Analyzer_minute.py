class Analyzer():
    '''
    매수 타이밍
    '''
    def get_sell_timing(self, minute_df):
        try:

            df = minute_df

            is_sell_timing = False

            df['MA3'] = df['close'].rolling(window=3).mean()
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            # ma120 = df['close'].rolling(window=120).mean()
            # ma240 = df['close'].rolling(window=240).mean()
            df['MA3_dpc'] = df['MA3'].pct_change()
            df['MA10_dpc'] = df['MA10'].pct_change()
            df['MA20_dpc5'] = df['MA20'].pct_change(5)

            max_close = max(df['close'][-50:])
            min_close = min(df['close'][-50:])

            self.bollinger_band(df)

            if round(df['ub'][-1]) == round(df['lb'][-1]):
                if df['close'][-1] == max_close:
                    is_sell_timing = True
            else:
                if df['close'][-1] > min_close * 1.05:
                    if df['MA20_dpc5'][-1] < 0:
                        if df['MA3_dpc'][-2] >= 0 and df['MA3_dpc'][-1] < 0:  # 3일선이 상향에서 하향으로 변경
                            # if df['MA10_dpc'][-2] > 0 and df['MA20_dpc'][-2] > 0:
                                if df['close'][-1] < df['open'][-1]:  # 현재 음봉
                                    if df['close'][-1] < df['MA3'][-1] < df['open'][-1]:
                                        is_sell_timing = True

            return is_sell_timing

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_sell_timing() -> exception! {} ".format(str(ex)))
            return None

    '''
    매수 타이밍
    '''
    def get_buy_timing(self, minute_df):
        try:

            df = minute_df

            is_buy_timing = False

            df['MA5'] = df['close'].rolling(window=5).mean()
            # df['MA10'] = df['close'].rolling(window=10).mean()
            # df['MA20'] = df['close'].rolling(window=20).mean()
            # df['MA10_dpc'] = df['MA10'].pct_change()
            # df['stddev'] = df['close'].rolling(window=20).std()
            # df['upper'] = df['MA20'] + (df['stddev'] * 2)
            # df['lower'] = df['MA20'] - (df['stddev'] * 2)
            # df['bandwidth'] = (df['upper'] - df['lower']) / df['MA20'] * 100
            self.bollinger_band(df)

            if 1 < df['bandwidth'][-2] <= 2.5:  # 밴드폭이 1~2 사이
                if df['MA5'][-2] > df['MA5'][-1]:
                    if df['close'][-1] > df['open'][-1]:  # 현재 양봉
                        if df['close'][-1] > df['ub'][-1] > df['open'][-1]:  # 볼린저 밴드 상향선 돌파
                            if df['volumn'][-1] > df['volumn'][-2] * 2.9:  # 거래량 급증
                                is_buy_timing = True
            # if df['MA5'][-2] > df['MA20'][-2]: # 5일선이 20일선보다 위에 있을 때
            #     if 1 < df['bandwidth'][-2] <= 2:  # 밴드폭이 1~2 사이
            #         if df['close'][-1] > df['open'][-1]: # 현재 양봉
            #             # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
            #             if df['close'][-1] > df['ub'][-1] > df['open'][-1]:  # 볼린저 밴드 상향선 돌파
            #                 if df['volumn'][-1] > df['volumn'][-2] * 4:  # 거래량 급증
            #                     is_buy_timing = True
            #     elif df['bandwidth'][-2] > 2:
            #         if df['MA10_dpc'][-2] > 0.00075:
            #             if df['close'][-1] > df['open'][-1]:  # 현재 양봉
            #                 # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
            #                 if (df['close'][-1] > df['ub'][-1] > df['open'][-1]) \
            #                                 or (df['ub'][-1] > df['close'][-1] > df['MA5'][-1]): #
            #                     if df['volumn'][-1] > df['volumn'][-2] * 2:  #
            #                         is_buy_timing = True
            # else: # 5일선이 20일선 아래 있을 때
            #     if df['bandwidth'][-2] > 5:
            #         if df['close'][-1] > df['open'][-1]:  # 현재 양봉
            #             # if final_df.loc[i, 'open'] == final_df.loc[i, 'low']: # 저가와 시가가 같을 때
            #             if df['close'][-1] > df['MA20'][-1] > df['open'][-1]:  # 20일선 상향선 돌파
            #                 if df['volumn'][-1] > df['volumn'][-2] * 2:  #
            #                     is_buy_timing = True

            return is_buy_timing

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_buy_timing() -> exception! {} ".format(str(ex)))
            return None


        
    def bollinger_band(self, minute_df): # 볼린저 밴드
        '''
        볼린저 밴드
        :param code:
        :return:
        '''
        try:

            df = minute_df
            sigma = 2
            n = 20
            df['center'] = df['close'].rolling(window=n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['close'].rolling(window=n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['close'].rolling(window=n).std()  # 하단 밴드
            df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100

            return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None
