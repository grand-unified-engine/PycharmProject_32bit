import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
from Kiwoom.Signal import Signal  # 클래스가 와도 되고 파일명이 와도 된다.
from Kiwoom.thread import MinuteCandle, RealTimeScreenNumbering
# from apscheduler.schedulers.background import BackgroundScheduler

import time

if __name__  == "__main__":
    # print("Main() start")
    app = QApplication(sys.argv) # 프로그램을 앱처럼 실행하고 그래픽적인 요소를 제어하는 기능을 포함. 동시성 처리할 수 있는 함수도 포함되어 있다.

    signal = Signal()

    ############### 초기 셋팅 함수들 ################
    signal.login_commConnect()  # 로그인 요청 함수
    signal.get_account_info()  # 계좌번호 가져오기, 접속서버 구분 포함
    signal.detail_account_info() #예수금 요청 시그널 포함
    signal.detail_account_mystock()  # 계좌평가잔고내역 --> account_stock_dict에 담는다.
    QTimer.singleShot(5000, signal.not_concluded_account) # 5초 뒤에 미체결 종목들 가져오기 실행(동시성 지원. 다음 메소드를 실행하면서 이 메소드만 5초 뒤에 실행)
    #############################################

    QTest.qWait(5000)
    signal.screen_number_setting() # 여기에서도 5초 딜레이 준다
    QTest.qWait(5000) #5초
    #
    # sched = BackgroundScheduler()
    # sched.add_job(signal.get_condition_load, 'cron', hour='09', minute='03', second="00", id='test')
    # sched.start()

    # signal.get_condition_load()
    # QTest.qWait(2000)  # 2초

    # signal.real_time_condition_stock_fuc()
    # QTest.qWait(500)  # 1초
    # signal.screen_number_real_time_setting()

    screenNumbering = RealTimeScreenNumbering(signal)
    screenNumbering.start()

    # QTest.qWait(2000)  # 2초
    # minuteCandle = MinuteCandle(signal)
    # minuteCandle.start()

    # sched.add_job(signal.gathering_money_fuc, 'cron', second=30, start_date=signal.event_loop.today + ' 09:02:00',
    #               end_date=signal.event_loop.today + ' 15:30:00', args=(['2']))

    # sched.add_job(signal.get_condition_load, 'interval', seconds=10)
    # sched.start()

    app.exec_() # 이벤트 루프 실행

    # count = 0
    # while True:  # 이걸 안 하면 sched가 끝나버린다고 함
    #     print("Running main process...............")
    #     time.sleep(1)
    #     count += 1
    #     if count == 10:
    #         sched.remove_job("test")



