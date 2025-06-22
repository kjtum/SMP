import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# 選好情報
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

matchings = [
    [("A", "W"), ("B", "X"), ("C", "Y"), ("D", "Z")],
    [("A", "Y"), ("B", "W"), ("C", "Z"), ("D", "X")],
    [("A", "X"), ("B", "Z"), ("C", "W"), ("D", "Y")],
    [("A", "Z"), ("B", "Y"), ("C", "X"), ("D", "W")],
    [("A", "W"), ("B", "Z"), ("C", "X"), ("D", "Y")]
]

labels = ["(i)", "(ii)", "(iii)", "(iv)", "(v)"]

def draw_matching(matching, label, men_prefs, women_prefs):
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.axis("off")
    for i, (m, w) in enumerate(matching):
        ax.text(0, i, f"{m}", fontsize=10, ha="right")
        ax.text(0.5, i, f"⇔", fontsize=10, ha="center")
        ax.text(1, i, f"{w}", fontsize=10, ha="left")
    # 満足度表示用
    men_scores = {m: 3 - men_prefs[m].index(w) for m, w in matching}
    women_scores = {w: 3 - women_prefs[w].index(m) for m, w in matching}
    men_sum = sum(men_scores.values())
    women_sum = sum(women_scores.values())
    diff = abs(men_sum - women_sum)
    min_satis = min(min(men_scores.values()), min(women_scores.values()))
    total = men_sum + women_sum
    ax.text(0.5, -0.8, f"{label} 満足度: 男={men_sum} 女={women_sum}\n差={diff} 合計={total} 最小={min_satis}", fontsize=8, ha="center")
    return fig

# 2列×3行でマッチング図を表示
cols = st.columns(2)
for i, matching in enumerate(matchings):
    with cols[i % 2]:
        st.pyplot(draw_matching(matching, labels[i], men_prefs, women_prefs))
    if i % 2 == 1:
        cols = st.columns(2)

# 表生成
def calculate_satisfaction(matching):
    men_scores = {m: 3 - men_prefs[m].index(w) for m, w in matching}
    women_scores = {w: 3 - women_prefs[w].index(m) for m, w in matching}
    men_sum = sum(men_scores.values())
    women_sum = sum(women_scores.values())
    diff = abs(men_sum - women_sum)
    minimum = min(min(men_scores.values()), min(women_scores.values()))
    total = men_sum + women_sum
    return [total, men_sum, women_sum, diff, minimum]

satisfaction_data = [calculate_satisfaction(m) for m in matchings]
columns = ["満足度の和\n最大化", "最小\n満足度\n最大化", "両性\n満足度\n公平"]
df = pd.DataFrame(satisfaction_data, columns=["合計", "男性和", "女性和", "差", "最小"], index=labels)

# 表スタイル関数
def highlight(val, colname):
    if colname == "男性和" and val == df["男性和"].max():
        return "color: red"
    if colname == "女性和" and val == df["女性和"].min():
        return "color: red"
    if colname == "差" and val == df["差"].min():
        return "color: red"
    return ""

styled = df.style.apply(lambda row: [highlight(val, col) for val, col in zip(row, df.columns)], axis=1)

# 表の見出し
st.markdown("### 8名の満足度を3つの観点から評価する")
st.dataframe(styled.set_table_attributes('class="dataframe"'), use_container_width=True)
