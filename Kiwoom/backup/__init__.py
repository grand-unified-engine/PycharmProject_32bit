import sys

import pandas as pd
from PyQt5.QtWidgets import QApplication

from kiwoom import Kiwoom

class OneDayDBSave:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

    def run(self):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        # opt10081 TR 요청
        self.kiwoom.set_input_value("종목코드", "035720")
        self.kiwoom.set_input_value("기준일자", "20200519")
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        # while Kiwoom.remained_data == True:
        #     time.sleep(TR_REQ_TIME_INTERVAL)
        #     Kiwoom.set_input_value("종목코드", "039490")
        #     Kiwoom.set_input_value("기준일자", "20170224")
        #     Kiwoom.set_input_value("수정주가구분", 1)
        #     Kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

        df = pd.DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                          index=self.kiwoom.ohlcv['date'])

        print(df)


# new_df = df[df['Volume'] !=0]
#
# con = sqlite3.connect("d:/finance_data/sqlite/kospi.db")
# df.to_sql('078930', con, if_exists='replace')
#
# readed_df = pd.read_sql("select * from '078930'", con, index_col = 'Date')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        stockdbsave = OneDayDBSave()
        stockdbsave.run()

    except Exception as e:
        print(e)
    # sys.exit(app.exec_())  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기, 마지막에 있어야 한다!



    # con = sqlite3.connect("c:/Users/Jason/stock.db")
    # df.to_sql('039490', con, if_exists='replace')