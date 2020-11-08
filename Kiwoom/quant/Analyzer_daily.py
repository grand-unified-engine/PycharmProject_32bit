# from datetime import datetime
import pandas as pd
import copy

class Analyzer():
    '''
    5, 10 , 20 이평선이 정배열상태인지
    '''
    def get_side_by_side_rise(self, maria_df):
        try:

            df = maria_df

            is_sabasa = False
            if len(df['close']) <= 20: # 20일 이평선을 이용해야 하므로
                is_sabasa = False
            else:
                # df는 과거에서 현재로, final_df는 현재에서 과거로
                ma5 = df['close'].rolling(window=5).mean()
                ma10 = df['close'].rolling(window=10).mean()
                ma20 = df['close'].rolling(window=20).mean()
                for i in range(1, 3):
                    if ma5[i * -1] > ma10[i * -1] > ma20[i * -1]:
                        is_sabasa = True
                    else:
                        is_sabasa = False
                        break

                if is_sabasa == True:
                    if df['close'][-1] > df['open'][-1]:  # 양봉일 때
                        if df['close'][-1] > df['open'][-1] * 1.17:  # 장대양봉일 때
                            is_sabasa = False

            return is_sabasa

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_side_by_side_rise() -> exception! {} ".format(str(ex)))
            return None

    '''
    조정 패턴
    '''
    def get_adjust_pattern(self, maria_df):

        try:
            df = maria_df

            is_adjust_pattern = False

            if len(df['close']) <= 5:
                is_adjust_pattern = False
            else:

                df['MA5'] = df['close'].rolling(window=5).mean()
                df['MA10'] = df['close'].rolling(window=10).mean()
                df['MA20'] = df['close'].rolling(window=20).mean()

                close = df['close']
                open = df['open']

                df.drop(['close', 'volume', 'open', 'high', 'low'], axis=1, inplace=True)

                df['max'] = pd.concat([df.max(axis=1)], axis=1)
                df['min'] = pd.concat([df.min(axis=1)], axis=1)
                df['나누기'] = df['max'] / df['min']
                # final_df['minus'] = final_df['max'] - final_df['min']
                # final_df['minus_dpc'] = (final_df['minus'] / final_df['minus'].shift(1) - 1) * 100  # 082850(10-06)
                # final_df['diff'] = final_df['minus'].diff().abs()
                # final_df['diff5'] = final_df['diff'].rolling(window=5).mean()

                # print(final_df)

                # 거래량 급증 할 때이므로 -1
                # 1차 조건
                if df['나누기'][-1] <= 1.01:
                    is_adjust_pattern = True

                if is_adjust_pattern == True:  # 1차 조건이 성립해야 함
                    if close[-1] > df['MA5'][-1] and close[-2] > df['MA5'][-2] and close[-3] > df['MA5'][-3]:
                        is_adjust_pattern = True
                    else:
                        is_adjust_pattern = False

                # 분석 날 장대음봉일 때 탈락
                if is_adjust_pattern == True:
                    if open[-1] > close[-1]:  # 음봉일 때
                        if open[-1] > close[-1] * 1.1:
                            is_adjust_pattern = False

            return is_adjust_pattern

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_side_by_side_rise() -> exception! {} ".format(str(ex)))
            return None


    def get_disparity(self, maria_df): # 이격도
        '''
        이격도 100 부근에서 매집봉 출현을 신호로 거래를 하는 것이 바로 눌림목 매매이다.
        모멘텀지표에 있다.
        :param code:
        :return:
        '''
        try:

            df = maria_df

            disparity = {'dispar': []}
            is_d_round = False
            if len(df['close']) < 5:
                is_d_round = False
            else:
                ma20 = df['close'].rolling(window=20).mean()
                # df['MA20'] = np.round(df['close'].rolling(window=20).mean(), 2)  # import numpy as np
                for i in range(1, 6): # end값은 반복범위에 포함되지 않음
                    dispar = (df['close'].iloc[i * -1] / ma20[i * -1]) * 100
                    disparity['dispar'].append(dispar)

                # print(disparity['dispar'])

                for val in disparity['dispar']:
                    if val <= 101.5 and val >= 90:
                        is_d_round = True
                    else:
                        is_d_round = False
                        break

            return is_d_round

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_disparity() -> exception! {} ".format(str(ex)))
            return None



    def get_demark(self, code): # Demark
        '''
        30분 봉에서 사용
        :param code:
        :return:
        '''
        try:
            d_high = 0.0
            d_low = 0.0
            # df = self.mk.get_daily_price(code)
            df = self.df.loc[self.df['code'] == code]

            pre_open = int(df['open'].shift(1).iloc[-1])
            pre_high = int(df['high'].shift(1).iloc[-1])
            pre_low = int(df['low'].shift(1).iloc[-1])
            pre_close = int(df['close'].shift(1).iloc[-1])

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

            print("d_high : {} ".format(d_high))

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


    def get_trix(self, code): # get_trix
        '''

        :param code:
        :return:
        '''
        try:

            # df = self.mk.get_daily_price(code, end_date=self.end_date)
            df = self.df.loc[self.df['code'] == code]

            ewm1 = df['close'].ewm(span=7).mean()
            ewm2 = ewm1.ewm(span=7).mean()
            ewm3 = ewm2.ewm(span=7).mean()

            pre_ewm1 = df['close'].shift(1).ewm(span=7).mean()
            pre_ewm2 = pre_ewm1.ewm(span=7).mean()
            pre_ewm3 = pre_ewm2.ewm(span=7).mean()

            trix = ((ewm3 / pre_ewm3) - 1) * 100

            signal = trix.ewm(span=5).mean()

            # print("trix : {}, signal : {}".format(trix, signal))

            is_signal_on_trix = False
            if trix.iloc[-1] > signal.iloc[-1] and trix.iloc[-2] > signal.iloc[-2]:
                is_signal_on_trix = True

            return is_signal_on_trix

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_trix() -> exception! {} ".format(str(ex)))
            return None



    def get_trix_today_value(self, code):
        '''
        :param code:
        :return:
        '''
        try:

            df = self.day_candle_dict[code]['일봉']

            ewm1 = df['close'].ewm(span=7).mean()
            ewm2 = ewm1.ewm(span=7).mean()
            ewm3 = ewm2.ewm(span=7).mean()

            pre_ewm1 = df['close'].shift(1).ewm(span=7).mean()
            pre_ewm2 = pre_ewm1.ewm(span=7).mean()
            pre_ewm3 = pre_ewm2.ewm(span=7).mean()

            trix = ((ewm3 / pre_ewm3) - 1) * 100

            signal = trix.ewm(span=5).mean()

            return trix[-1], signal[-1]

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("get_trix_value() -> exception! {} ".format(str(ex)))
            return None