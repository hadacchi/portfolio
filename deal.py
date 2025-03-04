import pandas as pd

TAX_RATE=0.20315

def buy_fund(target_df, t):
    '''時刻 t の価額を1とした場合の正規化時系列を返却
    '''
    tmp_df = target_df[target_df.index >= t]
    return tmp_df/tmp_df.head(1).values

def rebalance_buy(assets, portfolio, buy_amount = 1):
    '''購入結果がportfolioの比になるよう購入額を調整する

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
    '''リバランスをちゃんとやるための関数
    この関数が呼ばれた時点で，リバランス条件を満たしており，この関数はportfolioにピッタリ合わせることを目的とする
    本当は、売却益の TAX_RATE とするべきだが、現状は売却総額の TAX_RATEになっている

    Parameters
    ----------
    assets : pandas.Series
        資産時系列のDataFrameのうち，リバランスしたい時刻インデックスのスライス
        資産が N 個の時，assets.size == N
    principle : pandas.Series
        元本
    portfolio : pandas.Series
        columns が資産時系列の名前, value がその資産のウェイトであり正規化済のもの
    '''

    t = assets.name

    # 利益率計算
    benefit = assets-principle
    bene_rate = (assets/principle-1)

    # 逆比の差
    r2x1_r1x2 = portfolio.iloc[1]*assets.iloc[0] - portfolio.iloc[0]*assets.iloc[1]

    if r2x1_r1x2>0:
        # 1の資産を売って2の資産を買う
        if benefit.iloc[0]>0:
            # 利益が出てたら税金を考慮して売却額を決定
            dx1 = r2x1_r1x2/(1-portfolio.iloc[0]*TAX_RATE*benefit.iloc[0]/assets.iloc[0])  # 売却額
            tax = benefit.iloc[0]*dx1/assets.iloc[0]*TAX_RATE  # 税額
            dx2 = dx1 - tax  # 税引き後受け渡し額=購入額

            sell_buy = pd.Series([-dx1,dx2],name=t)
        else:
            # 利益が出てない時は税金を無視して売却額を決定
            tax = 0
            sell_buy = pd.Series([-r2x1_r1x2,r2x1_r1x2],name=t)
        sell_buy.index=assets.index
    else:
        # 2の資産を売って1の資産を買う
        if benefit.iloc[1]>0:
            # 利益が出てたら税金を考慮して売却額を決定
            dx2 = -r2x1_r1x2/(1-portfolio.iloc[1]*TAX_RATE*benefit.iloc[1]/assets.iloc[1])  # 売却額
            tax = benefit.iloc[1]*dx2/assets.iloc[1]*TAX_RATE  # 税額
            dx1 = dx2 - tax  # 税引き後受け渡し額=購入額

            sell_buy = pd.Series([dx1,-dx2],name=t)
        else:
            # 利益が出てない時は税金を無視して売却額を決定
            tax = 0
            sell_buy = pd.Series([-r2x1_r1x2,r2x1_r1x2],name=t)
        sell_buy.index=assets.index

    return sell_buy, tax.sum()
