# 以下、すべての安定マッチングを図で表示しつつ、表で比較するStreamlitアプリ

import streamlit as st
import itertools
import matplotlib.pyplot as plt
import os
from PIL import Image
import pandas as pd

MEN = ["A", "B", "C", "D"]
WOMEN = ["W", "X", "Y", "Z"]
IMAGE_DIR = "img"

# サンプル選好（自由に変更可）
men_prefs = {
    "A": ["W", "X", "Y", "Z"],
    "B": ["X", "Z", "W", "Y"],
    "C": ["Y", "W", "Z", "X"],
    "D": ["Z", "Y", "X", "W"]
}
women_prefs = {
    "W": ["A", "B", "C", "D"],
    "X": ["B", "C", "A", "D"],
    "Y": ["C", "A", "D", "B"],
    "Z": ["D", "C", "B", "A"]
}

# 安定マッチング判定
def is_stable(matching):
    m2w = {m: w for m, w in matching}
    w2m = {w: m for m, w in matching}
    for m, w in matching:
        mpref = men_prefs[m]
        wpref = women_prefs[w]
        for w_dash in mpref:
            if w_dash == w:
                break
            m_dash = w2m[w_dash]
            if women_prefs[w_dash].index(m) < women_prefs[w_dash].index(m_dash):
                return False
        for m_dash in wpref:
            if m_dash == m:
                break
            w_dash = m2w[m_dash]
            if men_prefs[m_dash].index(w) < men_prefs[m_dash].index(w_dash):
                return False
    return True

# 満足度計算（不満度 = index → 満足度 = 3 - index）
def calc_satisfaction(matching):
    m_scores = {m: 3 - men_prefs[m].index(w) for m, w in matching}
    w_scores = {w: 3 - women_prefs[w].index(m) for m, w in matching}
    m_sum = sum(m_scores.values())
    w_sum = sum(w_scores.values())
    min_satis = min(list(m_scores.values()) + list(w_scores.values()))
    diff = abs(m_sum - w_sum)
    total = m_sum + w_sum
    return total, m_sum, w_sum, diff, min_satis

# マッチング描画
def draw_matching(matching):
    fig, ax = plt.subplots(figsize=(6, 2.4), dpi=300)
    ax.axis('off')
    spacing = 0.3
    x_men, x_women = 0.2, 0.8
    icon_w, icon_h = 45, 36
    hoff = icon_h * 0.5 / icon_w * 0.25
    woff = 0.10
    for m, w in matching:
        y_m = -MEN.index(m) * spacing
        y_w = -WOMEN.index(w) * spacing
        ax.plot([x_men, x_women], [y_m, y_w], 'k-', lw=1.2, zorder=1)
        pm = os.path.join(IMAGE_DIR, f"{m}.png")
        if os.path.exists(pm):
            img = Image.open(pm).resize((icon_w, icon_h), Image.LANCZOS)
            ax.imshow(img, extent=(x_men-woff, x_men+woff, y_m-hoff, y_m+hoff), zorder=2)
        ax.text(x_men-woff-0.02, y_m, f"({3 - men_prefs[m].index(w)}) {m}", va='center', ha='right', fontsize=10)
        pw = os.path.join(IMAGE_DIR, f"{w}.png")
        if os.path.exists(pw):
            img = Image.open(pw).resize((icon_w, icon_h), Image.LANCZOS)
            ax.imshow(img, extent=(x_women-woff, x_women+woff, y_w-hoff, y_w+hoff), zorder=2)
        ax.text(x_women+woff+0.02, y_w, f"({3 - women_prefs[w].index(m)}) {w}", va='center', ha='left', fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.2, 0.3)
    return fig

# すべての安定マッチングを列挙
all_matches = []
for perm in itertools.permutations(WOMEN):
    mlist = list(zip(MEN, perm))
    if is_stable(mlist):
        all_matches.append(mlist)

# ローマ数字ラベル
roman_labels = ['(i)', '(ii)', '(iii)', '(iv)', '(v)', '(vi)', '(vii)', '(viii)']

# 表用データ格納
table_data = []

st.title("安定マッチングと満足度比較")

# マッチングを2列で表示
for i in range(0, len(all_matches), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j >= len(all_matches):
            continue
        match = all_matches[i + j]
        with cols[j]:
            label = roman_labels[i + j]
            total, msum, wsum, diff, min_satis = calc_satisfaction(match)
            st.markdown(f"**{label} 満足度: {total} (男={msum} 女={wsum})<br>差={diff} 最小={min_satis}**", unsafe_allow_html=True)
            st.pyplot(draw_matching(match))
            table_data.append([label, total, msum, wsum, diff, min_satis])

# 表の作成と表示
st.markdown("### 安定マッチング比較表")
df = pd.DataFrame(table_data, columns=["マッチング", "満足度合計", "男性和", "女性和", "差", "最小"])
df.set_index("マッチング", inplace=True)
st.dataframe(df)
