import pandas as pd
import pymysql
from datetime import datetime
from datetime import timedelta
import re


class MarketDB:
    def __init__(self):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='localhost', port=3308, user='root',
                                    password='mariadb', db='INVESTAR', charset='utf8')

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close()

    def get_company_info(self, code=None):
        """종목정보를 데이터프레임 형태로 반환
        """
        if code is None:
            sql = "SELECT * FROM company_info"
        else:
            sql = "SELECT * FROM company_info where code = '{}'".format(code)
        df = pd.read_sql(sql, self.conn)
        # print("df : {}".format(df))
        return df

    def get_portfolio(self):
        """포트폴리오를 데이터프레임 형태로 반환
        """
        # sql = "SELECT code FROM portfolio_stock"
        sql = "SELECT code FROM portfolio_stock where is_receive_real IS FALSE OR is_receive_real IS NULL"
        # sql = "SELECT * FROM portfolio_stock WHERE workdate = '{}'".format(datetime.today().strftime('%Y-%m-%d'))
        # sql = "SELECT * FROM portfolio_stock WHERE workdate = '{}'".format('2020-09-29') # 따옴표 넣어야 함
        df = pd.read_sql(sql, self.conn)
        # print("get_portfolio sql df : {}".format(df))
        return df

    def get_vol_uprise_stock(self, code=None):
        """거래량 급증 데이터를 데이터프레임 형태로 반환
        """
        if code is None:
            sql = "SELECT * FROM vol_uprise_stock"
        else:
            sql = "SELECT * FROM vol_uprise_stock where code = '{}'".format(code)
        df = pd.read_sql(sql, self.conn)
        return df

    def get_buy_stock_info_max_seq(self, code, buy_date, state=None):
        """
        매입한 종목 시퀀스 가져오기
        """
        if state is None:
            sql = "SELECT max(seq) AS seq FROM buy_stock_info where code = '{}' and buy_date = '{}'".format(code,
                                                                                                            buy_date)
        else:
            sql = "SELECT max(seq) AS seq FROM buy_stock_info where code = '{}' and buy_date = '{}' and state = '{}'".format(
                code, buy_date, state)
        seq = self.conn.cursor().execute(sql)

        if seq is None:
            seq = 0
        return seq

    def get_buy_stock_info(self, code, buy_date, seq, state):
        """
        매입한 종목 정보 가져오기
        """
        sql = "SELECT * FROM buy_stock_info where code = '{}' and buy_date = '{}' and seq = '{}' and state = '{}'".format(
            code, buy_date, seq, state)
        df = pd.read_sql(sql, self.conn)
        return df

    def get_daily_price(self, code, start_date=None, end_date=None):
        """KRX 종목의 일별 시세를 데이터프레임 형태로 반환
            - code       : KRX 종목코드('005930') 또는 상장기업명('삼성전자')
            - start_date : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
            - end_date   : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """
        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d')
            # print("start_date is initialized to '{}'".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            if start_lst[0] == '':
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                # print(f"ValueError: start_year({start_year:d}) is wrong.")
                return
            if start_month < 1 or start_month > 12:
                # print(f"ValueError: start_month({start_month:d}) is wrong.")
                return
            if start_day < 1 or start_day > 31:
                # print(f"ValueError: start_day({start_day:d}) is wrong.")
                return
            # start_date=f"{start_year:04d}-{start_month:02d}-{start_day:02d}"
            start_date = "{:04d}-{:02d}-{:02d}".format(start_year, start_month, start_day)

        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
            # print("end_date is initialized to '{}'".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            if end_lst[0] == '':
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1800 or end_year > 2200:
                # print(f"ValueError: end_year({end_year:d}) is wrong.")
                return
            if end_month < 1 or end_month > 12:
                # print(f"ValueError: end_month({end_month:d}) is wrong.")
                return
            if end_day < 1 or end_day > 31:
                # print(f"ValueError: end_day({end_day:d}) is wrong.")
                return
            # end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"
            end_date = "{:04d}-{:02d}-{:02d}".format(end_year, end_month, end_day)

        sql = "SELECT * FROM daily_price WHERE code = '{}' and date >= '{}' and date <= '{}'".format(code, start_date,
                                                                                                     end_date)
        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        return df
