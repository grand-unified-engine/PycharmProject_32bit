from datetime import datetime
import pandas as pd

class Analyzer():
    '''
    매도 타이밍
    '''
    def get_sell_timing(self, minute_df, stock_code):
        try:

            df = minute_df.copy()

            is_sell_timing = False

            df['MA3'] = df['close'].rolling(window=3).mean()
            df['MA5'] = df['close'].rolling(window=5).mean()
            ma10 = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            ma120 = df['close'].rolling(window=120).mean()
            ma240 = df['close'].rolling(window=240).mean()
            df['bandwidth3-20'] = ((df['MA3'] - df['MA20']) / (
                        (df['MA3'] + df['MA20']) / 2)) * 100

            # 홀딩해서 수익 극대화 하는 방법 찾기 - 일봉, 주봉 좋은 종목으로 판단?
            '''
            1. 종가가 240선 위일 때
            '''
            if df['close'][-1] > ma240[-1]:
                '''
                단기에 끌어올림
                2020.11.14
                '''
                if df['bandwidth3-20'][-1] > 8 or df['bandwidth3-20'][-2] > 8:
                    is_sell_timing = True
                '''
                세력이탈 이탈 매도
                2020.11.14 
                '''
                if (df['MA60'][-1] > df['MA20'][-1]) or (df['MA60'][-2] > df['MA20'][-2]): # 60선이 20선 위로 올라섰을 때
                    if df['open'][-1] > df['close'][-1] and df['open'][-2] > df['close'][-2] and df['open'][-3] > df['close'][-3]: #연속 3음봉이면
                        is_sell_timing = True
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
                # if ma5_dpc[-1] < 0 and ma10_dpc[-1] < 0 and ma20_dpc[-1] < 0 and ma60_dpc[-1] < 0:  # 모든 선 다 내려가면
                #     is_sell_timing = True
                #     print("무조건 매도 : {} ".format(stock_code))

            # else:
            #     '''
            #     2. 종가가 240선 아래일 때
            #     '''
            #     '''
            #     무조건 매도
            #     '''
            #     if ma5_dpc[-1] < 0 and ma10_dpc[-1] < 0 and ma20_dpc[-1] < 0 and ma60_dpc[-1] < 0:  # 모든 선 다 내려가면
            #         is_sell_timing = True
            #         print("무조건 매도 : {} ".format(stock_code))

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
            ma10 = df['close'].rolling(window=10).mean()
            ma20 = df['close'].rolling(window=20).mean()
            ma60 = df['close'].rolling(window=60).mean()
            ma120 = df['close'].rolling(window=120).mean()
            ma240 = df['close'].rolling(window=240).mean()


            '''
            1. 종가가 240선 위일 때
            '''
            if df['close'][-1] > ma240[-1]:
                '''
                1차로 5 > 10 > 20
                '''
                if df['ma5'][-1] > ma10[-1] > ma20[-1]:
                    b_df = self.bollinger_band(minute_df)
                    if (2 < b_df['bandwidth'][-1] < 3.1) or (2 < b_df['bandwidth'][-2] < 3.1): #밴드폭이 2~3.1 사이
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
            df['center'] = df['close'].rolling(window=n).mean()  # 중앙 이동평균선
            df['ub'] = df['center'] + sigma * df['close'].rolling(window=n).std()  # 상단 밴드
            df['lb'] = df['center'] - sigma * df['close'].rolling(window=n).std()  # 하단 밴드
            df['bandwidth'] = (df['ub'] - df['lb']) / df['center'] * 100

            return df

        except Exception as ex:
            # self.logging.logger.debug("get_target_price() -> exception! {} ".format(str(ex)))
            print("bollinger_band() -> exception! {} ".format(str(ex)))
            return None
