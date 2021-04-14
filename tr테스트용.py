import sys
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
from Kiwoom.Signal import Signal  # 클래스가 와도 되고 파일명(모듈)이 와도 된다.
from Kiwoom.thread import SellThread
# from apscheduler.schedulers.background import BackgroundScheduler
import time
from Kiwoom.quant.DayCandleAlgorithm import DayCandleAlgorithm

if __name__  == "__main__":
    print("Main() start")

    app = QApplication(sys.argv)

    signal = Signal()

    ############### 초기 셋팅 함수들 ################
    signal.login_commConnect()  # 로그인 요청 함수
    # signal.get_account_info()  # 계좌번호 가져오기, 접속서버 구분 포함
    # signal.detail_account_info() #예수금 요청 시그널 포함
    # signal.detail_account_mystock()  # 계좌평가잔고내역 --> account_stock_dict에 담는다.
    # QTimer.singleShot(5000, signal.not_concluded_account) # 5초 뒤에 미체결 종목들 가져오기 실행(동시성 지원. 다음 메소드를 실행하면서 이 메소드만 5초 뒤에 실행)
    #############################################

    # signal.not_concluded_account()
    # QTest.qWait(1000)
    # signal.screen_number_setting()
    # QTest.qWait(1000) #1초

    # sched = BackgroundScheduler()
    # sched.add_job(signal.gathering_money_fuc, 'cron', second=30, start_date=signal.event_loop.today + ' 09:02:00',
    #               end_date=signal.event_loop.today + ' 15:30:00', args=(['2']))
    # sched.add_job(signal.get_condition_load, 'cron', hour='09', minute='02', second="59", id='test')
    # sched.add_job(signal.get_condition_load, 'interval', seconds=10)
    # sched.start()

    # signal.get_condition_load()

    # QTest.qWait(1000)  # 1초
    # for code in signal.condition_stock.keys():
    #     QTest.qWait(3000)
    #     try:
    #         if signal.api.server_gubun == "1":
    #             # is_receive_real = 0이면 자꾸 들어오니까 강제로 1로 바꿈 (나중에 테이블 수정하기!!!) 2021-02-18
    #             if code == '066430' or code == '570045' or code == '036630' or code == '093230':
    #                 continue
    #             else:
    #                 signal.condition_stock[code].update({'d_high': {DayCandleAlgorithm(code).dIndicator.get_demark()}})
    #                 signal.minute_candle_req(code=code)
    #         else:
    #             signal.condition_stock[code].update({'d_high': {DayCandleAlgorithm(code).dIndicator.get_demark()}})
    #             signal.minute_candle_req(code=code)
    #
    #     except:
    #         print("{} buy 코드 오류 발생".format(code))

    # QTest.qWait(2000)  # 1초
    # sThread = SellThread(signal)
    # sThread.start()

    # signal.event_loop.sign_volume_req(code="289080")
    # d_high = DayCandleAlgorithm(code="000440").dIndicator.get_demark()
    # print(d_high)
    signal.minute_candle_req(code="900310")

    # signal.volume_uprise_req("1", "500", "1") # 거래량 급증 요청

    app.exec_()

    # count = 0
    # while True:  # 이걸 안 하면 sched가 끝나버린다고 함
    #     print("Running main process...............")
    #     time.sleep(1)
    #     count += 1
    #     if count == 10:
    #         sched.remove_job("test")



