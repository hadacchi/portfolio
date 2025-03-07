def return():
    target = close_df['ｅＭＡＸＩＳ　Ｓｌｉｍ米国株式（Ｓ＆Ｐ５００）']
    target.loc[target.index[-1]+datetime.timedelta(days=3)] = target.iloc[-1]  # 2月末までしかデータがないので，1営業日のばす
    for N in [6,12,36,60]:
        # diffは先頭がNaNになることを利用し，月始めにTrueとなる判定式を1つシフト
        # 結果，月次の終値の系列となる
        monthly = target[:-1][target.index.month.diff().dropna()!=0]
        returns = monthly.pct_change().dropna()[-N:]  # 月次リターン
        N = min(N,returns.size)  # 系列が不足している場合に系列超に上書き
        print(f'N={N}, return = {(returns+1).prod()**(12/N)-1:.4f}')  # Nヶ月の年率リターン
