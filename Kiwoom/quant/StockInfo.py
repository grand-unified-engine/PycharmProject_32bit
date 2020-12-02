import FinanceDataReader as fdr
import datetime as dt

def get_current_price(code):
    df = fdr.DataReader(code, '2020-11-01')
    # df = fdr.DataReader("DJI", '2017-05-10')
    # df = df[['Close']]
    # df['daily_rtn'] = df['Close'].pct_change()
    # df['st_rtn'] = (1+df['daily_rtn']).cumprod()
    return df