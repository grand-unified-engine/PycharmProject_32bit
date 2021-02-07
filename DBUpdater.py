import sys
from PyQt5.QtWidgets import QApplication
from Kiwoom.Signal import Signal  # 클래스가 와도 되고 파일명이 와도 된다.
from Kiwoom.config.MariaDB import MarketDB
from PyQt5.QtTest import QTest

class DBUpdater:  
    def __init__(self):

        self.app = QApplication(sys.argv)

        self.mk = MarketDB()

        self.signal = Signal()
        ############### 초기 셋팅 함수들 ################
        self.signal.login_commConnect()  # 로그인 요청 함수

        # [시장구분값]
        # 0: 장내
        # 10: 코스닥
        # 3: ELW
        # 8: ETF
        # 50: KONEX
        # 4: 뮤추얼펀드
        # 5: 신주인수권
        # 6: 리츠
        # 9: 하이얼펀드
        # 30: K - OTC
        code_list = self.signal.api.get_code_list_by_market("8")
        # code_list.append(self.signal.api.get_code_list_by_market("10"))
        # code_list.append(self.signal.api.get_code_list_by_market("8"))

        # code_df = self.mk.get_company_info()
        # print("code_list : {}".format(code_list))
        #
        # # code_list.remove('000075')
        # # code_list.remove('000080')
        # # self.signal.corp_info_req(code="000075")
        # # print("code_list : {}".format(len(code_list)))
        #
        # for row in code_df.itertuples():
        #     self.signal.corp_info_req(code=row[1])

        # code_list = ['000087']
        #
        # for code in code_list:
        #     print("code : {}".format(code))
        #     self.signal.corp_info_req(code=code)
        # QTest.qWait(10000)
        #
        for code in code_list:
            # print(self.mk.get_company_info(code=code)['code'].isnull())
            code_name = self.signal.api.get_master_code_name(code)
            state = self.signal.api.get_master_stock_state(code) # 종목 상태 업데이트
            with self.mk.conn.cursor() as curs:
                sql = "REPLACE INTO company_info(code, company, stock_state) VALUES ('{}', '{}', '{}')".format(code, code_name, state)
                curs.execute(sql)
                self.mk.conn.commit()

        print("code_list : {}".format(len(code_list)))

        self.app.exec_()
               
    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.mk.conn.close()

if __name__ == '__main__':
    dbu = DBUpdater()

