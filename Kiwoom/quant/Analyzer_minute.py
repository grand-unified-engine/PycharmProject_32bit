from datetime import datetime
import pandas as pd

class Analyzer():
    '''
    매도 타이밍
    '''
    def get_sell_timing(self, minute_df, stock_code):
        try:

            df = minute_df

            is_sell_timing = False

            ma5 = df['close'].rolling(window=5).mean()
            ma5_dpc = (ma5 / ma5.shift(1) - 1) * 100
            ma10 = df['close'].rolling(window=10).mean()
            ma10_dpc = (ma10 / ma10.shift(1) - 1) * 100
            ma20 = df['close'].rolling(window=20).mean()
            ma20_dpc = (ma20 / ma20.shift(1) - 1) * 100
            ma60 = df['close'].rolling(window=60).mean()
            ma60_dpc = (ma60 / ma60.shift(1) - 1) * 100
            ma120 = df['close'].rolling(window=120).mean()
            ma120_dpc = (ma120 / ma120.shift(1) - 1) * 100

            ma240 = df['close'].rolling(window=240).mean()

            # 홀딩해서 수익 극대화 하는 방법 찾기 - 일봉, 주봉 좋은 종목으로 판단?
            '''
            1. 종가가 240선 위일 때
            '''
            if df['close'][-1] > ma240[-1]:

                if ma5_dpc[-1] > 0 and ma10_dpc[-1] > 0 and ma20_dpc[-1] > 0:
                    if ma5[-1] > ma10[-1] > ma20[-1]:
                        is_sell_timing = False
                        # portfolio_stock_dict.update({"전환점여부": False})
                        # portfolio_stock_dict.update({"대량체결여부": False})
                else:
                    '''
                    고점매도. 
                    '''
                    is_candle_rise = False
                    for i in range(2, 5):  # end값은 반복범위에 포함되지 않음
                        if df['close'][-i] >= df['open'][-i]:
                            is_candle_rise = True
                        else:
                            is_candle_rise = False

                    if ma5[-1] > ma10[-1] and ma20[-1]: # 5, 10, 20선 다 상승
                        if is_candle_rise: # 2~4전 캔들이 모두 양봉
                            if df['close'][-1] <= df['open'][-1]: # 현재 분봉이 음봉일 때
                                is_sell_timing = True
                                print("고점매도 : {} ".format(stock_code))

                    '''
                    추세 이탈 매도
                    2020.10.22 호가잔량으로 확인하도록 변경해서 우선 막음
                    '''
                    # if "홀딩판단" not in portfolio_stock_dict:
                    #     portfolio_stock_dict.update({"홀딩판단": {"확인할시간": ""}})
                    #
                    # if ma5_dpc[-1] < 0  and ma10_dpc[-1] < 0 and ma20_dpc[-1] < 0: # 5, 10, 20선 아래로 내려가고
                    #     if df['close'][-1] * 1.02 <= ma20[-1]: # 종가가 20일 2% 이탈하면 추세 꺾인걸로 보고 매도
                    #             # is_sell_timing = True
                    #             portfolio_stock_dict["홀딩판단"].update({"확인할시간": datetime.now().replace(minute=datetime.now().minute+2, second=00)})
                    #     # elif df['close'][-1] * 1.02 < ma20[-1] < df['close'][-1] * 1.01: # 종가가 20일 1% 이탈하면
                    #     #     if df['close'][-1] * 1.015 < df['open'][-1]: # 장대음봉일 때 매도
                    #     #         is_sell_timing = True
                    #
                    # if portfolio_stock_dict["홀딩판단"]["확인할시간"] == datetime.now().replace(second=00):
                    #     if df['close'][-2] < df['open'][-2]: #다시 확인했더니 1전 분봉이 음봉이면 매도
                    #         is_sell_timing = True
                    #         portfolio_stock_dict["홀딩판단"].update({"확인할시간": datetime.now().hour-1})
                    #         print("추세 이탈 매도 : {} ".format(stock_code))
                    #     else:
                    #         is_sell_timing = False


                '''
                무조건 매도
                '''
                if ma5_dpc[-1] < 0 and ma10_dpc[-1] < 0 and ma20_dpc[-1] < 0 and ma60_dpc[-1] < 0 and ma120_dpc[-1] < 0:  # 모든 선 다 내려가면
                    is_sell_timing = True
                    print("무조건 매도 : {} ".format(stock_code))

            else:
                '''
                2. 종가가 240선 아래일 때
                '''
                '''
                무조건 매도
                '''
                if ma5_dpc[-1] < 0 and ma10_dpc[-1] < 0 and ma20_dpc[-1] < 0 and ma60_dpc[-1] < 0:  # 모든 선 다 내려가면
                    is_sell_timing = True
                    print("무조건 매도 : {} ".format(stock_code))

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

            df['ma5'] = df['close'].rolling(window=5).mean()
            # ma5_dpc = (ma5 / ma5.shift(1) - 1) * 100
            ma10 = df['close'].rolling(window=10).mean()
            # ma10_dpc = (ma10 / ma10.shift(1) - 1) * 100
            ma20 = df['close'].rolling(window=20).mean()
            # ma20_dpc = (ma20 / ma20.shift(1) - 1) * 100
            ma60 = df['close'].rolling(window=60).mean()
            # ma60_dpc = (ma60 / ma60.shift(1) - 1) * 100
            ma120 = df['close'].rolling(window=120).mean()
            # ma120_dpc = (ma120 / ma120.shift(1) - 1) * 100

            ma240 = df['close'].rolling(window=240).mean()


            '''
            1. 종가가 240선 위일 때
            '''
            if df['close'][-1] > ma240[-1]:
                '''
                1차로 5 > 10 > 20 > 60 
                '''
                if df['ma5'][-1] > ma10[-1] and ma10[-1] > ma20[-1] and ma20[-1] > ma60[-1]:
                    is_buy_timing = True

            else:
                '''
                2. 종가가 240선 아래일 때
                '''
                m5_pct_change = df['ma5'].pct_change(3) #5일선 3봉 변화율

                if m5_pct_change[-1] < 0: # 5일선 3봉 하강이다가
                    if df['close'][-1] > df['open'][-1]: # 양봉
                        is_buy_timing = True

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

            org_df = minute_df.copy()
            df = org_df[['close', 'low']]
            sigma = 2
            n = 20
            df['center'] = df['close'].rolling(n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['close'].rolling(n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['close'].rolling(n).std()  # 하단 밴드

            return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None
