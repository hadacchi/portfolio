import pandas as pd

TAX_RATE=0.20315

def buy_fund(target_df, t):
    '''時刻 t の価額を1とした場合の正規化時系列を返却
    '''
    tmp_df = target_df[target_df.index >= t]
    return tmp_df/tmp_df.head(1).values

def rebalance_buy(assets, portfolio, buy_amount = 1):
    '''購入結果がportfolioの比になるよう購入額を調整し購入比率を返却する

    Parameters
    ----------
    assets : pandas.Series
        資産時系列のDataFrameのうち，リバランスしたい時刻インデックスのスライス
        資産が N 個の時，assets.size == N
    portfolio : pandas.Series
        columns が資産時系列の名前, value がその資産のウェイトであり正規化済のもの

    Result
    ------
    buy_rate : pandas.Series
        columns が資産時系列の名前, value がその資産のウェイトであり正規化済のもの
        今回購入の比率
    '''

    #assets = assets.iloc[0]  # pandas.Seriesに変換
    total = assets.sum() + buy_amount
    delta = total*portfolio - assets
    # 負になっているものがある場合、売却になってしまうので0にし、他の資産の購入に均等配分
    delta[delta<0] = 0
    delta = delta/delta.sum()

    return delta

def rebalance(assets, principle, portfolio):
    '''任意の数の資産に対応したリバランス関数。
    利益が出ている資産の売却に税金を考慮して理想のポートフォリオに近づける。

    Parameters
    ----------
    assets : pandas.Series
        リバランス対象時点の各資産の評価額
    principle : pandas.Series
        各資産の元本
    portfolio : pandas.Series
        正規化された理想のポートフォリオ比率

    Returns
    -------
    sell_buy : pandas.Series
        各資産の売買額（正の値は購入、負の値は売却）
    total_tax : float
        売却益に対する課税合計
    '''

    t = assets.name
    total_value = assets.sum()

    # 理想の資産配分額
    target_values = total_value * portfolio

    # 売買差額の計算
    delta = target_values - assets

    sell_buy = pd.Series(0.0, index=assets.index)
    total_tax = 0.0

    # まず利益の出ている資産について、売却側の税金を考慮
    for asset in assets.index:
        if delta[asset] < 0:
            profit = assets[asset] - principle[asset]
            sell_amount = -delta[asset]
            if profit > 0:
                # 課税対象利益に対する税額計算
                taxable_ratio = profit / assets[asset]
                tax = sell_amount * taxable_ratio * TAX_RATE
                sell_amount += tax
                total_tax += tax
            sell_buy[asset] = -sell_amount

    # 売却で得た金額を再配分（税金控除後の資金を利用）
    available_cash = -sell_buy[sell_buy < 0].sum() - total_tax
    buy_targets = delta[delta > 0]
    if not buy_targets.empty:
        buy_ratios = buy_targets / buy_targets.sum()
        for asset in buy_targets.index:
            sell_buy[asset] = available_cash * buy_ratios[asset]

    sell_buy.name = t
    return sell_buy, total_tax
