import datetime
import re
import pandas as pd

import yfinance as yf

def pick_yfinance_data(tickers, start='1970-01-01', end=None, join='inner'):
    '''yfinanceからtickerリストのデータを取得し結合してDataFrameとして返却する

    Parameters
    ----------
    tickers : list
        yfinance で識別可能な ticker 文字列のリスト
    start : datetime string or object
        yyyy-mm-dd 形式の文字列または datetime.datetime で可能
    end : datetime string or object
    join : string
        系列の結合方式

    Result
    ------
    close_df : pandas.DataFrame
        取得したヒストリカルデータのうち、終値の系列
    dividend_df : pandas.DataFrame
        取得したヒストリカルデータのうち、配当金・分配金の系列
    '''

    yf_tickers = {key: yf.Ticker(key) for key in tickers}
    close_list = []
    dividend_list = []
    key_list = []
    for key,ticker in yf_tickers.items():
        datum = ticker.history(start=start, end=end)
        datum.index = datum.index.tz_localize(None)  # JST ローカライズを消す
        close_list.append(datum['Close'])
        dividend_list.append(datum['Dividends'])
        key_list.append(key)
    # 終値の時系列
    close_df = pd.concat(close_list, axis=1, join=join)
    close_df.columns = key_list

    # 分配金の時系列
    dividend_df = pd.concat(dividend_list, axis=1, join=join)
    dividend_df.columns = key_list

    # 分配金の額面に対する率
    #div_rate_df = dividends_df/close_df
    return close_df.loc[start:end], dividend_df.loc[start:end]

def to_date(datestr, date_splitter=re.compile('[年月日/]')):
    '''input is date string joined by date_splitter

    Parameters
    ----------
    datestr : string
    date_splitter : re.Pattern

    Result
    ------
    datetime : datetime.datetime
    '''
    date_list = date_splitter.split(datestr)
    return datetime.datetime(*list(map(int, date_list[:3])))

def pick_csv_data(names, start='1970-01-01', end=None):
    '''csvからデータを取得し結合してDataFrameとして返却する
    csvの形式は、投信協会のCSVデータとし、文字コードは932

    ```
    年月日,基準価額(円),純資産総額（百万円）,分配金,決算期
    2018年07月03日,10038,1,,
    2018年07月04日,9936,1,,
    2018年07月05日,9942,105,,
    ```

    Parameters
    ----------
    names : list
        csvファイルの拡張子を除いたファイル名、時系列名として用いる
    start : datetime string or object
        yyyy-mm-dd 形式の文字列または datetime.datetime で可能
    end : datetime string or object
    join : string
        系列の結合方式

    Result
    ------
    close_df : pandas.DataFrame
        基準価額の系列
    dividend_df : pandas.DataFrame
        配当金・分配金の系列
    '''

    index_column = '年月日'
    data_column = '基準価額(円)'
    div_column = '分配金'

    close_data = {}
    dividend_data = {}

    for name in names:
        datum = pd.read_csv(name+'.csv', encoding='932')
        datum[index_column] = datum[index_column].apply(to_date)
        close_data[name] = datum.set_index(index_column)[data_column]
        dividend_data[name] = datum.set_index(index_column)[div_column]

    # 終値の時系列
    close_df = pd.DataFrame(close_data).dropna()

    # 分配金の時系列
    # 現状，分配金のあるファンドが落とした範囲にはなかったので省略
    #dividend_df = pd.DataFrame(dividend_data)

    return close_df.loc[start:end], None  #, dividend_df.loc[start:end]