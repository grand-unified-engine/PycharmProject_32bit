def candle_info(Open, High, Low, Close):
    try:
        color = ''
        rise_rate = 0.0
        body_rate = 0.0
        top_tail_rate = 0.0
        bottom_tail_rate = 0.0
        if (Close - Open) > 0: # 양봉일 때
            color = 'red'
            rise_rate = (1 - (Close / Open)) * 100
            if (High - Low) > 0:
                body_rate = ((Close - Open) / (High - Low))
                top_tail_rate = ((High - Close) / (High - Low))
                bottom_tail_rate = ((Open - Low) / (High - Low))
        else:
            color = 'blue'
            rise_rate = (1 - (Open / Close)) * 100
            if (High - Low) > 0:
                body_rate = ((Open - Close) / (High - Low))
                top_tail_rate = ((High - Open) / (High - Low))
                bottom_tail_rate = ((Close - Low) / (High - Low))

        return color, rise_rate, body_rate, top_tail_rate, bottom_tail_rate
    except Exception as ex:
        print("candle_info() -> exception! {} ".format(str(ex)))
        return None

def weather_vane(Open, High, Low, Close):
    try:
        is_wv = False
        if (Close - Open) > 0: # 양봉일 때
            # print("Open: {}, High: {}, Low: {}, Close: {}".format(Open, High, Low, Close))
            if (High - Low) > 0: # 오류방지
                if ((Close - Open) / (High - Low)) < 0.02:
                    is_wv = True
        return is_wv
    except Exception as ex:
        print("weather_vane() -> exception! {} ".format(str(ex)))
        return None

def long_red_candle(PreClose, Open, High, Low, Close):
    try:
        is_long = False
        if (Close - PreClose) > 0: # 양봉일 때
            if PreClose > 0:
                # print("상승률: {}".format((Close - PreClose) / PreClose))
                if 30 > (Close - PreClose) / PreClose * 100 > 20:
                    is_long = True
            elif Close == Open == High == Low: # 갭상한가
                is_long = True

        return is_long
    except Exception as ex:
        print("long_red_candle() -> exception! {} ".format(str(ex)))
        return None

def is_short_candle(code, Open, High, Low, Close):
    try:
        is_short_candle = False
        if (Close - Open) > 0: # 양봉일 때
            if Open > 0:
                if (Close - Open) / Open * 100 < 1:
                    is_short_candle = True
        else:
            if (Open - Close) / Close * 100 < 1:
                is_short_candle = True
        return is_short_candle
    except Exception as ex:
        print("is_short_candle() -> exception! {} ".format(str(ex)))
        print("code: ", code)
        return None