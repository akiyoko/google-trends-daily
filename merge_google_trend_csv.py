from pathlib import Path

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd

"""
参考
https://www.monotalk.xyz/blog/Merge-Google-Trend-results-with-pytrends/
"""

# See https://note.nkmk.me/python-pandas-option-display/
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 150)
pd.set_option('display.unicode.east_asian_width', True)


BASE_DIR = Path(__file__).resolve(strict=True).parent
INPUT_DIR = BASE_DIR / "inputs"

# データフレームを格納するリスト
df_trends = []

# 各CSVファイルを読み込んでリストに追加
for csv_path in INPUT_DIR.glob("*.csv"):
    df = pd.read_csv(csv_path, index_col="date", parse_dates=True)
    df_trends.append(df)

# データフレームを開始時期（最小の日付）で並び替え
df_trends = sorted(df_trends, key=lambda x: x.index.min())
print(f"{df_trends=}")

df = None
for df_trend in df_trends:
    if df is None:
        df = df_trend

    # オーバーラップ期間を抽出
    df_overlap = pd.merge(df, df_trend, on="date", suffixes=("_df1", "_df2"))
    print(f"{df_overlap=}")
    
    # オーバーラップ期間の平均値を計算
    mean_df1 = df_overlap["trend_df1"].mean()
    mean_df2 = df_overlap["trend_df2"].mean()
    print(f"{mean_df1=}")
    print(f"{mean_df2=}")
    
    # 小さい方を調整する
    if mean_df1 < mean_df2:
        # df1を調整
        adjust_value = mean_df2 / mean_df1
        df = df * adjust_value
    else:
        # df2を調整
        adjust_value = mean_df1 / mean_df2
        df_trend = df_trend * adjust_value
    
    # データフレームをマージ
    df = pd.concat([df, df_trend])
    
    # 重複を避けるために再度日付でグループ化し、平均を計算
    df = df.groupby("date").mean()

    print("^" * 100)
    print(df)
    print("^" * 100)

    # マージされたデータフレームの最大値が100になるようにスケールを調整
    max_value = df["trend"].max()
    print(f"{max_value=}")
    df = df * (100 / max_value)

# マージされたデータフレームをCSVに保存
df.to_csv("merged_df.csv")

# グラフを描画
df.plot()
plt.show()
