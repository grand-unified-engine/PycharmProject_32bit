import configparser
import sys

from PyQt5.QtWidgets import QApplication

from kiwoom import Kiwoom, ParameterTypeError, ParameterValueError, KiwoomProcessingError

config = configparser.ConfigParser()
config.read('config\\config.ini')
password = config["KIWOOM"]["password"]

class Jarvis:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.accountList = self.kiwoom.get_login_info("ACCNO").rstrip(';')

    def run(self):
        self.inquiryBalance()

    def inquiryBalance(self):

        try:
            # 예수금상세현황요청
            # self.Kiwoom.set_input_value("계좌번호", self.accountList)
            # self.Kiwoom.set_input_value("비밀번호", password)
            # self.Kiwoom.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

            # 계좌평가잔고내역요청 - opw00018 은 한번에 20개의 종목정보를 반환
            self.kiwoom.reset_opw00018_output()
            self.kiwoom.set_input_value("계좌번호", self.accountList)
            self.kiwoom.set_input_value("비밀번호", password)
            self.kiwoom.set_input_value("조회구분", "1")
            self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")

            # print("single")
            # for i in range(1, 6):
            #     print(self.Kiwoom.opw00018_output['single'][i - 1])

            itemcode = ""
            item_count = len(self.kiwoom.opw00018_output['multi'])
            for j in range(item_count):
                code = self.kiwoom.opw00018_output['multi'][j][0]
                if j == 0:
                    itemcode = code
                else:
                    itemcode += ";"

            print(itemcode)
            # self.Kiwoom.setRealReg("012345", itemcode, "10;15;121;125;228;", "1")
            #
            # while self.Kiwoom.inquiry == '2':
            #     time.sleep(0.2)
            #
            #     self.Kiwoom.setInputValue("계좌번호", self.accountComboBox.currentText())
            #     self.Kiwoom.setInputValue("비밀번호", "0000")
            #     self.Kiwoom.commRqData("계좌평가잔고내역요청", "opw00018", 2, "2")

        except (ParameterTypeError, ParameterValueError, KiwoomProcessingError) as e:
            print('Critical, ', e)

        # # accountEvaluationTable 테이블에 정보 출력
        # item = QTableWidgetItem(self.Kiwoom.opw00001Data)   # d+2추정예수금
        # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        # self.accountEvaluationTable.setItem(0, 0, item)

        # for i in range(1, 6):
        #     item = QTableWidgetItem(self.Kiwoom.opw00018Data['accountEvaluation'][i-1])
        #     item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        #     self.accountEvaluationTable.setItem(0, i, item)
        #
        # self.accountEvaluationTable.resizeRowsToContents()
        #
        # # stocksTable 테이블에 정보 출력
        # cnt = len(self.Kiwoom.opw00018Data['stocks'])
        # self.stocksTable.setRowCount(cnt)
        #
        # for i in range(cnt):
        #     row = self.Kiwoom.opw00018Data['stocks'][i]
        #
        #     for j in range(len(row)):
        #         item = QTableWidgetItem(row[j])
        #         item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        #         self.stocksTable.setItem(i, j, item)
        #
        # self.stocksTable.resizeRowsToContents()
        #
        # # 데이터 초기화
        # self.Kiwoom.opwDataReset()
        #
        # # inquiryTimer 재시작
        # self.inquiryTimer.start(1000*10)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        jarvis = Jarvis()
        jarvis.run()

    except Exception as e:
        print(e)
    sys.exit(app.exec_())  # 메인 이벤트 루프에 진입 후 프로그램이 종료될 때까지 무한 루프 상태 대기, 마지막에 있어야 한다!