from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtTest import QTest

class Api:
    def __init__(self):

        self.ocx = QAxWidget(
            "KHOPENAPI.KHOpenAPICtrl.1")  # 키움증권 Open API+의 ProgID를 사용하여 생성된 QAxWidget을 Kiwoom 변수에 할당
        # QAxWidget는 마이크로소프트사에서 제공하는 프로세스를 가지고 화면을 구성하는 데 필요한 기능들이 담겨있다.
        self.server_gubun = None # 접속서버 구분을 알려준다. 1 : 모의투자 접속, 나머지 : 실서버 접속
    ###############################################################
    # 로그인 버전처리                                              #
    ###############################################################
    def comm_connect(self):
        self.ocx.dynamicCall("CommConnect()")

    def get_connect_state(self):
        """
        현재 접속상태를 반환합니다.
        0: 미연결, 1: 연결
        :return: int
        """
        state = self.ocx.dynamicCall("GetConnectState()")
        return state

    def get_login_info(self, tag, isConnectState=False, code=None):
        """
        사용자의 tag에 해당하는 정보를 반환한다.
        tag에 올 수 있는 값은 아래와 같다.
        ACCOUNT_CNT: 전체 계좌의 개수를 반환한다.
        ACCNO: 전체 계좌 목록을 반환한다. 계좌별 구분은 ;(세미콜론) 이다.
        USER_ID: 사용자 ID를 반환한다.
        USER_NAME: 사용자명을 반환한다.
        GetServerGubun: 접속서버 구분을 반환합니다.("1": 모의투자, 그외(빈 문자열포함): 실서버)
        :param tag: string
        :param isConnectState: bool - 접속상태을 확인할 필요가 없는 경우 True로 설정.
        :return: string
        """

        if not isConnectState:
            if not self.get_connect_state():
                raise KiwoomConnectError()

        if not isinstance(tag, str):
            raise ParameterTypeError()

        if tag not in ['ACCOUNT_CNT', 'ACCNO', 'USER_ID', 'USER_NAME', 'GetServerGubun', 'GetMasterStockInfo']:
            raise ParameterValueError()

        if tag == "GetServerGubun":
            info = self.get_server_gubun()
        elif tag == "GetMasterStockInfo":
            info = self.get_master_stock_info(code)
        else:
            cmd = 'GetLoginInfo("%s")' % tag
            info = self.ocx.dynamicCall(cmd)

        return info

    ###############################################################
    # 조회와 실시간데이터처리                                      #
    ###############################################################
    def comm_rq_data(self, rqname, trcode, prevnext, screenno): # 조회요청 함수
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, prevnext, screenno)

    def set_input_value(self, id, value): # 조회요청시 tr의 input값을 지정하는 함수
        self.ocx.dynamicCall("SetInputValue(QString, QString)", id, value)

    def disconnect_real_data(self, scrno=None): # 스크린 번호 연결 끊기. 해당 스크린 번호로 요청된 모든 데이터의 연결을 끊는다
        self.ocx.dynamicCall("DisconnectRealData(QString)", scrno)

    def get_repeat_cnt(self, trcode, recordname): #  조회수신한 멀티데이터의 갯수(반복)수를 얻을수 있습니다.
        cnt = self.ocx.dynamicCall("GetrepeatCnt(QString, QString", trcode, recordname)
        return cnt

    def get_comm_data(self, trcode, recordname, index, itemname): # OnReceiveTRData()이벤트가 호출될때 조회데이터를 얻어오는 함수
        ret = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, index, itemname)
        return ret

    def get_comm_real_data(self, code, fid): # OnReceiveRealData()이벤트가 호출될때 조회데이터를 얻어오는 함수
        ret = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return ret

    #  600일 치 데이터 가져오는 함수.
    def get_comm_data_ex(self, trcode, recordname):
        """
        멀티데이터 획득 메서드
        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        :param trCode: string
        :param recordname: string - KOA에 명시된 멀티데이터명
        :return: list - 중첩리스트, 최신 날짜순
        """
        # 600일치 데이터를 받고 나서 이전의 과거 데이터는 가져올 수 없으므로 과거 데이터가 필요하면 getcommdata함수를 사용

        # if not (isinstance(trCode, str)
        #         and isinstance(multiDataName, str)):
        #     raise ParameterTypeError()

        data = self.ocx.dynamicCall("GetCommDataEx(QString, QString)", trcode, recordname)
        return data
        
    ###############################################################
    # 주문과 잔고처리                                              #
    ###############################################################

    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        QTest.qWait(300) # 1초에 5회만 주문 가능하고 그 이상 주문하면 에러 -308을 리턴한다.
        # order_success = self.ocx.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [rqname, screen_no, acc_no, int(order_type), code, int(quantity), int(price), hoga, order_no])
        returnCode = self.ocx.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])

        # print("returnCode : {}".format(returnCode))
        # self.orderLoop.exec_()

        return returnCode

        # if returnCode != 0:
        #     raise KiwoomProcessingError("sendOrder(): " + ErrorCode.errors(returnCode))
        # if returnCode != 0:
        #     raise KiwoomProcessingError("sendOrder(): " + ErrorCode.errors(returnCode))
        # receiveTrData() 에서 루프종료 - 이렇게 하면 다른 tr이 안됨 2020-10-16 확인


    def get_chejan_data(self, fid):
        ret = self.ocx.dynamicCall("GetChejanData(int)", fid)
        return ret

    ###############################################################
    # 조건검색                                                     #
    ###############################################################
    # 조건식 로딩 하기
    def get_condition_load(self):
        self.ocx.dynamicCall("GetConditionLoad()")

    def get_condition_name_list(self):
        ret = self.ocx.dynamicCall("GetConditionNameList()")
        return ret

    def send_condition(self, screenno, conditionname, index, search):
        self.ocx.dynamicCall("SendCondition(QString, QString, int, int)", screenno, conditionname, index, search)

    def send_condition_stop(self, screenno, conditionname, index):
        self.ocx.dynamicCall("SendCondition(QString, QString, int)", screenno, conditionname, index)

    def set_real_reg(self, screenno, codelist, fidlist, opttype):
        """
        실시간 데이터 요청 메서드
        종목코드와 fid 리스트를 이용해서 실시간 데이터를 요청하는 메서드입니다.
        한번에 등록 가능한 종목과 fid 갯수는 100종목, 100개의 fid 입니다.
        실시간등록타입을 0으로 설정하면, 등록한 종목들은 실시간 해지되고 등록한 종목만 실시간 시세가 등록
        실시간등록타입을 1로 설정하면, 먼저 등록한 종목들과 함께 실시간 시세가 등록된다.
        실시간 데이터는 실시간 타입 단위로 receiveRealData() 이벤트로 전달되기 때문에,
        이 메서드에서 지정하지 않은 fid 일지라도, 실시간 타입에 포함되어 있다면, 데이터 수신이 가능하다.
        :param screenno: string
        :param codelist: string - 종목코드 리스트(종목코드;종목코드;...) 종목코드가 없으면 종목이 아니라 주식 장의 시간 상태를 실시간으로 체크해서 슬롯으로 받을 수 있다.
        :param fidlist: string - fid 리스트(fid;fid;...)
        :param opttype: string - 실시간등록타입(0: 첫 등록, 1: 추가 등록)
        "0"은 새로운 실시간 요청을 할 때 사용하고, "1"은 실시간으로 받고 싶은 정보를 추가할 때 사용한다. 그래서 실시간 정보를 요청할 때 종목을 "0"으로 등록하면 이전에 등록된 실시간 연결은 모두 초기화되고 새롭게 등록된다.
        ex) 장운영구분은 "0"으로 초기화, 이후에 추가할 종목들은 모두 "1"
        """

        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                         screenno, codelist, fidlist, opttype)

    def set_real_remove(self, scrno=None, delcode=None): # 스크린 번호와 종목코드를 인자로 전달하면 스크린번호로 그룹화된 지정 종목의 연결만 끊는다.
        self.ocx.dynamicCall("SetRealRemove(QString, QString)", scrno, delcode)

    ###############################################################
    # 기타 종목정보관련 함수                                        #
    ###############################################################
    def get_code_list_by_market(self, market): # 종목코드 리스트 가져오기
        '''
        종목코드 리스트 받기
        #0: 장내 10: 코스닥 3: ELW 8: ETF 50: KONEX 4: 뮤추얼펀드 5: 신주인수권 6: 리츠 9: 하이얼펀드 30: K - OTC, NULL은 전체

        :param market: 시장코드 입력
        :return:
        '''
        code_list = self.ocx.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(";")[:-1]
        return code_list

    def get_master_code_name(self, code): # 종목코드에 해당하는 종목명을 전달
        code_name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_master_listed_stock_cnt(self, code): # 입력한 종목코드에 해당하는 종목 상장주식수를 전달
        cnt = self.ocx.dynamicCall("GetMasterListedStockCnt(QString)", code)
        return cnt

    def get_master_stock_state(self, code):
        state = self.ocx.dynamicCall("GetMasterStockState(QString)", code)
        return state

    def get_server_gubun(self):
        """
        서버구분 정보를 반환한다.
        리턴값이 "1"이면 모의투자 서버이고, 그 외에는 실서버(빈 문자열포함).
        :return: string
        """
        ret = self.ocx.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    def get_master_stock_info(self, code):
        """
        서버구분 정보를 반환한다.
        리턴값이 "1"이면 모의투자 서버이고, 그 외에는 실서버(빈 문자열포함).
        :return: string
        """
        ret = self.ocx.dynamicCall("KOA_Functions(QString, QString)", "GetMasterStockInfo", code)
        return ret


class RealType(object): # 손가락 하나 까딱
    SENDTYPE = {
        '거래구분': {
            '지정가': '00',
            '시장가': '03',
            '조건부지정가': '05',
            '최유리지정가': '06',
            '최우선지정가': '07',
            '지정가IOC': '10',
            '시장가IOC': '13',
            '최유리IOC': '16',
            '지정가FOK': '20',
            '시장가FOK': '23',
            '최유리FOK': '26',
            '장전시간외종가': '61',
            '시간외단일가매매': '62',
            '장후시간외종가': '81'
        }
    }

    REALTYPE = {
        # 장 중에 해당 종목이 체결될 때 받는다.
        '주식체결': {
            '체결시간': 20,
            '현재가': 10, #체결가
            '전일대비': 11,
            '등락율': 12,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '거래량': 15,
            '누적거래량': 13,
            '누적거래대금': 14,
            '시가': 16,
            '고가': 17,
            '저가': 18,
            '전일대비기호': 25,
            '전일거래량대비(계약,주)': 26,
            '거래대금증감': 29,
            '전일거래량대비(비율)': 30,
            '거래회전율': 31,
            '거래비용': 32,
            '체결강도': 228,
            '시가총액(억)': 311,
            '장구분': 290,
            'KO접근도': 691,
            '상한가발생시간': 567,
            '하한가발생시간': 568
        },
        # 주식 장이 시작 전, 시작, 종료 전, 종료 중 어떤 상태인지 알려준다.
        '장시작시간': {
            '장운영구분': 215,
            '시간': 20, #(HHMMSS)
            '장시작예상잔여시간':214
        },
        # 주문을 넣을 때 받는 데이터
        '주문체결': {
            '계좌번호': 9201,
            '주문번호': 9203,
            '관리자사번': 9205,
            '종목코드': 9001,
            '주문업무분류': 912, #(jj:주식주문)
            '주문상태': 913, #(접수, 확인, 체결) (10:원주문, 11:정정주문, 12:취소주문, 20:주문확인, 21:정정확인, 22:취소확인, 90,92:주문거부) #https://bbn.kiwoom.com/bbn.openAPIQnaBbsDetail.do
            '종목명': 302,
            '주문수량': 900,
            '주문가격': 901,
            '미체결수량': 902,
            '체결누계금액': 903,
            '원주문번호': 904,
            '주문구분': 905, #(+매수, -매도, -매도정정, +매수정정, 매수취소, 매도취소)
            '매매구분': 906, #(보통, 시장가등)
            '매도수구분': 907, # 매도(매도정정, 매도취도 포함)인 경우 1, 매수(매수정정, 매수취소 포함)인 경우 2
            '주문/체결시간': 908, #(HHMMSS)
            '체결번호': 909,
            '체결가': 910,
            '체결량': 911,
            '현재가': 10,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '단위체결가': 914,
            '단위체결량': 915,
            '당일매매수수료': 938,
            '당일매매세금': 939,
            '거부사유': 919,
            '화면번호': 920,
            '터미널번호': 921,
            '신용구분(실시간 체결용)': 922,
            '대출일(실시간 체결용)': 923,
        },
        '주식호가잔량':{
            '호가시간': 21,
            '매도호가1': 41,
            '매도호가수량1': 61,
            '매도호가직전대비1': 81,
            '매수호가1': 51,
            '매수호가수량1': 71,
            '매수호가직전대비1': 91,
            '매도호가총잔량': 121,
            '매수호가총잔량': 125,
            '순매수잔량': 128,
            '순매도잔량': 138
        },

        '매도수구분': {
            '1': '매도',
            '2': '매수'
        },
        # 매매주문이 체결돼서 계좌의 정보가 변경될 때 받는 데이터.
        '잔고': {
            '계좌번호': 9201,
            '종목코드': 9001,
            '종목명': 302,
            '현재가': 10,
            '보유수량': 930,
            '매입단가': 931,
            '총매입가': 932,
            '주문가능수량': 933,
            '당일순매수량': 945,
            '매도매수구분': 946,
            '당일총매도손익': 950,
            '예수금': 951,
            '(최우선)매도호가': 27,
            '(최우선)매수호가': 28,
            '기준가': 307,
            '손익율': 8019
        },
    }


class ErrorCode:
    def errors(err_code):
        err_dic = {0: ('OP_ERR_NONE', '정상처리'),
                   -10: ('OP_ERR_FAIL', '실패'),
                   -100: ('OP_ERR_LOGIN', '사용자정보교환실패'),
                   -101: ('OP_ERR_CONNECT', '서버접속실패'),
                   -102: ('OP_ERR_VERSION', '버전처리실패'),
                   -103: ('OP_ERR_FIREWALL', '개인방화벽실패'),
                   -104: ('OP_ERR_MEMORY', '메모리보호실패'),
                   -105: ('OP_ERR_INPUT', '함수입력값오류'),
                   -106: ('OP_ERR_SOCKET_CLOSED', '통신연결종료'),
                   -200: ('OP_ERR_SISE_OVERFLOW', '시세조회과부하'),
                   -201: ('OP_ERR_RQ_STRUCT_FAIL', '전문작성초기화실패'),
                   -202: ('OP_ERR_RQ_STRING_FAIL', '전문작성입력값오류'),
                   -203: ('OP_ERR_NO_DATA', '데이터없음'),
                   -204: ('OP_ERR_OVER_MAX_DATA', '조회가능한종목수초과'),
                   -205: ('OP_ERR_DATA_RCV_FAIL', '데이터수신실패'),
                   -206: ('OP_ERR_OVER_MAX_FID', '조회가능한FID수초과'),
                   -207: ('OP_ERR_REAL_CANCEL', '실시간해제오류'),
                   -300: ('OP_ERR_ORD_WRONG_INPUT', '입력값오류'),
                   -301: ('OP_ERR_ORD_WRONG_ACCTNO', '계좌비밀번호없음'),
                   -302: ('OP_ERR_OTHER_ACC_USE', '타인계좌사용오류'),
                   -303: ('OP_ERR_MIS_2BILL_EXC', '주문가격이20억원을초과'),
                   -304: ('OP_ERR_MIS_5BILL_EXC', '주문가격이50억원을초과'),
                   -305: ('OP_ERR_MIS_1PER_EXC', '주문수량이총발행주수의1 % 초과오류'),
                   -306: ('OP_ERR_MIS_3PER_EXC', '주문수량은총발행주수의3 % 초과오류'),
                   -307: ('OP_ERR_SEND_FAIL', '주문전송실패'),
                   -308: ('OP_ERR_ORD_OVERFLOW', '주문전송과부하'),
                   -309: ('OP_ERR_MIS_300CNT_EXC', '주문수량300계약초과'),
                   -310: ('OP_ERR_MIS_500CNT_EXC', '주문수량500계약초과'),
                   -340: ('OP_ERR_ORD_WRONG_ACCTINFO', '계좌정보없음'),
                   -500: ('OP_ERR_ORD_SYMCODE_EMPTY', '종목코드없음')
                   }

        tuple = err_dic[err_code]

        return tuple


class ParameterTypeError(Exception):
    """ 파라미터 타입이 일치하지 않을 경우 발생하는 예외 """

    def __init__(self, msg="파라미터 타입이 일치하지 않습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParameterValueError(Exception):
    """ 파라미터로 사용할 수 없는 값을 사용할 경우 발생하는 예외 """

    def __init__(self, msg="파라미터로 사용할 수 없는 값 입니다."):
        self.msg = msg

    def __str__(self):
        return self.msg


class KiwoomProcessingError(Exception):
    """ 키움에서 처리실패에 관련된 리턴코드를 받았을 경우 발생하는 예외 """

    def __init__(self, msg="처리 실패"):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return self.msg


class KiwoomConnectError(Exception):
    """ 키움서버에 로그인 상태가 아닐 경우 발생하는 예외 """

    def __init__(self, msg="로그인 여부를 확인하십시오"):
        self.msg = msg

    def __str__(self):
        return self.msg

