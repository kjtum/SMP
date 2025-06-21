import streamlit as st
import random
import matplotlib.pyplot as plt
from PIL import Image
import os
from best20_prefs import BEST_PREFS

# 定数
MEN = ["A", "B", "C", "D"]
WOMEN = ["X", "Y", "Z", "W"]
IMAGE_DIR = "img"

st.set_page_config(layout="wide")
st.title("安定結婚問題 - GS法（女性からの提案）段階シミュレーション")

# プリセット呼び出し
preset_keys = sorted(BEST_PREFS.keys())
choice = st.sidebar.selectbox("好みパターン番号を選択", preset_keys)
if st.sidebar.button("このパターンで初期化"):
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[choice]
    st.session_state.step = 0
    st.session_state.proposals = {w: [] for w in WOMEN}
    st.session_state.engaged = {}
    st.session_state.free_women = WOMEN[:]
    st.session_state.received = {m: [] for m in MEN}

# ランダム初期化
if st.sidebar.button("好みをランダム初期化"):
    def generate_random_prefs():
        men = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
        women = {w: random.sample(MEN, len(MEN)) for w in WOMEN}
        return men, women
    st.session_state.men_prefs, st.session_state.women_prefs = generate_random_prefs()
    st.session_state.step = 0
    st.session_state.proposals = {w: [] for w in WOMEN}
    st.session_state.engaged = {}
    st.session_state.free_women = WOMEN[:]
    st.session_state.received = {m: [] for m in MEN}

# セッションステート初期化
if 'men_prefs' not in st.session_state:
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[preset_keys[0]]
    st.session_state.step = 0
    st.session_state.proposals = {w: [] for w in WOMEN}
    st.session_state.engaged = {}
    st.session_state.free_women = WOMEN[:]
    st.session_state.received = {m: [] for m in MEN}

def calculate_dissatisfaction(matching, men_prefs, women_prefs):
    if not matching:
        return 0, 0, 0, 0, 0
    man_score = sum(men_prefs[m].index(w) for m, w in matching)
    woman_score = sum(women_prefs[w].index(m) for m, w in matching)
    total = man_score + woman_score
    diff = abs(man_score - woman_score)
    max_score = max(max(men_prefs[m].index(w), women_prefs[w].index(m)) for m, w in matching)
    return total, man_score, woman_score, diff, max_score

def draw_state_with_proposals(matching, proposals, men_prefs, women_prefs):
    fig, ax = plt.subplots(figsize=(2.4, 1.2), dpi=300)
    ax.axis('off')
    spacing = 0.6
    x_men, x_women = 0.2, 0.8
    hoff, woff = 0.1, 0.1

    for i, m in enumerate(MEN):
        y = -i * spacing
        pm = os.path.join(IMAGE_DIR, f"{m}.png")
        if os.path.exists(pm):
            img = Image.open(pm)
            ax.imshow(img, extent=(x_men-woff, x_men+woff, y-hoff, y+hoff), zorder=2)
        ax.text(x_men - 0.13, y, f"(0) {m}", fontsize=10, va='center', ha='right')

    for i, w in enumerate(WOMEN):
        y = -i * spacing
        pw = os.path.join(IMAGE_DIR, f"{w}.png")
        if os.path.exists(pw):
            img = Image.open(pw)
            ax.imshow(img, extent=(x_women-woff, x_women+woff, y-hoff, y+hoff), zorder=2)
        ax.text(x_women + 0.13, y, f"(0) {w}", fontsize=10, va='center', ha='left')

    for m, w in st.session_state.engaged.items():
        y_m = -MEN.index(m) * spacing
        y_w = -WOMEN.index(w) * spacing
        ax.plot([x_men, x_women], [y_m, y_w], color='black', lw=1.0, zorder=1)

    if len(st.session_state.free_women) == 0:
        for m, w in matching:
            y_m = -MEN.index(m) * spacing
            y_w = -WOMEN.index(w) * spacing
            ax.plot([x_men, x_women], [y_m, y_w], color='blue', lw=1.5, zorder=1)

    ax.set_xlim(0, 1)
    ax.set_ylim(- (len(MEN)-1) * spacing - 0.3, 0.3)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0)
    return fig

# GS法の1ステップ実行
if st.button("1ステップ進める") and st.session_state.free_women:
    woman = st.session_state.free_women[0]
    prefs = st.session_state.women_prefs[woman]
    for man in prefs:
        if man not in st.session_state.proposals[woman]:
            st.session_state.proposals[woman].append(man)
            st.session_state.received[man].append(woman)
            if man not in st.session_state.engaged.values():
                st.session_state.engaged[man] = woman
            else:
                current = st.session_state.engaged[man]
                if st.session_state.men_prefs[man].index(woman) < st.session_state.men_prefs[man].index(current):
                    st.session_state.engaged[man] = woman
                    st.session_state.free_women.append(current)
            break
    st.session_state.free_women.remove(woman)
    st.session_state.step += 1

# 状態表示
matching = [(m, w) for m, w in st.session_state.engaged.items()]
total, man_score, woman_score, diff, max_score = calculate_dissatisfaction(matching, st.session_state.men_prefs, st.session_state.women_prefs)
st.markdown(f"#### 不満度: 合計={total}, 男性側={man_score}, 女性側={woman_score}, 差={diff}, 最大不満度={max_score}")
fig = draw_state_with_proposals(matching, st.session_state.proposals, st.session_state.men_prefs, st.session_state.women_prefs)
col1, col2 = st.columns([1, 1])
with col1:
    st.pyplot(fig)
