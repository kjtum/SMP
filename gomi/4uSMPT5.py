import pandas as pd
import streamlit as st

# === 安定マッチングと満足度情報は別スクリプトで取得済みと仮定 ===
# 以下は仮データ。実際はGSマッチングなどのアルゴリズムから取得すること
matchings = [
    [("A", "W"), ("B", "X"), ("C", "Y"), ("D", "Z")],
    [("A", "Y"), ("B", "W"), ("C", "Z"), ("D", "X")],
    [("A", "X"), ("B", "Z"), ("C", "W"), ("D", "Y")],
    [("A", "Z"), ("B", "Y"), ("C", "X"), ("D", "W")],
    [("A", "W"), ("B", "Z"), ("C", "X"), ("D", "Y")]
]

men_prefs = {
    "A": ["W", "X", "Y", "Z"],
    "B": ["X", "W", "Z", "Y"],
    "C": ["Y", "Z", "W", "X"],
    "D": ["Z", "Y", "X", "W"]
}

women_prefs = {
    "W": ["A", "B", "C", "D"],
    "X": ["B", "A", "D", "C"],
    "Y": ["C", "D", "A", "B"],
    "Z": ["D", "C", "B", "A"]
}

# 満足度の計算関数
def calculate_satisfaction(matching):
    men_scores = {m: 3 - men_prefs[m].index(w) for m, w in matching}
    women_scores = {w: 3 - women_prefs[w].index(m) for m, w in matching}
    men_sum = sum(men_scores.values())
    women_sum = sum(women_scores.values())
    diff = abs(men_sum - women_sum)
    minimum = min(min(men_scores.values()), min(women_scores.values()))
    total = men_sum + women_sum
    return [total, men_sum, women_sum, diff, minimum]

# 各マッチングに満足度計算を適用
satisfaction_data = [calculate_satisfaction(m) for m in matchings]
matching_labels = ["(i)", "(ii)", "(iii)", "(iv)", "(v)"]
columns_internal = ["満足度合計", "男性和", "女性和", "差", "最小"]
df = pd.DataFrame(satisfaction_data, columns=columns_internal, index=matching_labels)

# 強調関数
def highlight(val, colname):
    if colname == "男性和" and val == df["男性和"].max():
        return 'color: red'
    if colname == "女性和" and val == df["女性和"].min():
        return 'color: red'
    if colname == "差" and val == df["差"].min():
        return 'color: red'
    return ''

# スタイル適用
styled = df.style.apply(lambda row: [highlight(val, col) for val, col in zip(row, df.columns)], axis=1)

# 表表示
st.markdown("### 8名の満足度を3つの観点から評価する")
st.dataframe(styled.set_table_attributes('class="dataframe"'), use_container_width=True)
