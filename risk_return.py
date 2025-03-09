import datetime
import numpy as np

def anualized_return(target_df, period=12):
    '''年率リターンを計算する

    Parameters
    ----------
    target_df : pandas.DataFrame
        資産時系列
    period : integer
        リターンを計算する期間を月数で指定する

    Result
    ------
    return : pandas.Series
        年率リターン
    '''
    if period <= 0:
        raise Exception('invalid period')
    d1 = datetime.timedelta(days=1)
    t1 = target_df.index[-1]
    tmp = target_df.copy()
    if t1.day >= 28:
        tmp.loc[t1+d1*3] = tmp.iloc[-1]  # 最後のデータが28日以降の場合は3営業日のばして，それが本当に月末の場合に最終データを計算対象に含める
    monthly = tmp[:-1][tmp.index.month.diff().dropna()!=0]
    returns = monthly.pct_change().dropna()[-period:]  # 月次リターン
    period = min(period, returns.size)  # 系列が不足している場合に系列長で上書き
    return (returns+1).prod()**(12/period)-1

def anualized_risk(target_df, period=12):
    '''年率リスクを計算する

    Parameters
    ----------
    target_df : pandas.DataFrame
        資産時系列
    period : integer
        リスクを計算する期間を月数で指定する
        1年～3年の場合は，12, 24, 36 に丸めて計算

    Result
    ------
    risk : float
        年率リターン
    '''
    if period <= 0:
        raise Exception('invalid period')

    if period <= 6:
        y, m, d = target_df.index[-1].timetuple()[:3]
        if m-period > 0:
            m -= period
        else:
            y -= 1
            m += 12 - period
        # dayly
        tmp = target_df.loc[datetime.datetime(y,m,d):]
        returns = tmp.pct_change().dropna()
        sqrt_N = np.sqrt(252)
    elif period < 36:
        N = 52 * period//12
        d1 = datetime.timedelta(days=1)
        t1 = target_df.index[-1]
        tmp = target_df.copy()
        tmp.loc[t1+d1*3] = tmp.iloc[-1]  # 金曜で終わる系列は月曜に金曜の値をコピーして最終日を計算対象に含める
        # weekly
        weekly = tmp.iloc[:-1][tmp.index.weekday.diff().dropna()<=0]
        returns = weekly.pct_change().dropna()[-N:]
        sqrt_N = np.sqrt(N)
    else:
        N = period  # 3年～は月次リターンの分散から計算
        d1 = datetime.timedelta(days=1)
        t1 = target_df.index[-1]
        tmp = target_df.copy()
        if t1.day >= 28:
            tmp.loc[t1+d1*3] = tmp.iloc[-1]  # 最後のデータが28日以降の場合は3営業日のばして，それが本当に月末の場合に最終データを計算対象に含める
        # monthly
        monthly = tmp[:-1][tmp.index.month.diff().dropna()!=0]
        returns = monthly.pct_change().dropna()[-N:]  # 月次リターン
        sqrt_N = np.sqrt(12)
    return returns.std()*sqrt_N