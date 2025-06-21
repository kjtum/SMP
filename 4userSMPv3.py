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
    man_score = sum(men_prefs[m].index(w) for m, w in matching)
    woman_score = sum(women_prefs[w].index(m) for m, w in matching)
    total = man_score + woman_score
    diff = abs(man_score - woman_score)
    max_score = max(max(men_prefs[m].index(w), women_prefs[w].index(m)) for m, w in matching)
    return total, man_score, woman_score, diff, max_score

def draw_state_with_proposals(matching, proposals, men_prefs, women_prefs):
    fig, ax = plt.subplots(figsize=(3, 1.2), dpi=300)
    ax.axis('off')
    spacing = 0.25
    x_men, x_women = 0.2, 0.8
    icon_w, icon_h = 10, 8
    hoff = icon_h * 0.5 / icon_w * 0.25
    woff = 0.07

    for i, m in enumerate(MEN):
        y = -i * spacing
        pm = os.path.join(IMAGE_DIR, f"{m}.png")
        if os.path.exists(pm):
            img = Image.open(pm)
            ax.imshow(img, extent=(x_men-woff, x_men+woff, y-hoff, y+hoff))
        ax.text(x_men-woff-0.015, y, m, va='center', ha='right', fontsize=8)
    for i, w in enumerate(WOMEN):
        y = -i * spacing
        pw = os.path.join(IMAGE_DIR, f"{w}.png")
        if os.path.exists(pw):
            img = Image.open(pw)
            ax.imshow(img, extent=(x_women-woff, x_women+woff, y-hoff, y+hoff))
        ax.text(x_women+woff+0.015, y, w, va='center', ha='left', fontsize=8)

    for m, w in matching:
        y_m = -MEN.index(m) * spacing
        y_w = -WOMEN.index(w) * spacing
        ax.plot([x_men, x_women], [y_m, y_w], color='blue', lw=1.0)

    for w in WOMEN:
        for m in proposals[w]:
            if (m, w) not in matching:
                y_m = -MEN.index(m) * spacing
                y_w = -WOMEN.index(w) * spacing
                ax.plot([x_men, x_women], [y_m, y_w], color='black', lw=0.8)

    ax.set_xlim(0,1)
    ax.set_ylim(- (len(MEN)-1) * spacing - 0.2, 0.2)
    plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0)
    return fig

def gs_step():
    if not st.session_state.free_women:
        return

    w = st.session_state.free_women[0]
    prefs = st.session_state.women_prefs[w]

    for m in prefs:
        if m not in st.session_state.proposals[w]:
            st.session_state.proposals[w].append(m)
            st.session_state.received[m].append(w)

            if m not in st.session_state.engaged:
                st.session_state.engaged[m] = w
                st.session_state.free_women.pop(0)
            else:
                current_w = st.session_state.engaged[m]
                men_prefs = st.session_state.men_prefs[m]
                if men_prefs.index(w) < men_prefs.index(current_w):
                    st.session_state.engaged[m] = w
                    st.session_state.free_women.pop(0)
                    st.session_state.free_women.append(current_w)
            break

st.button("次のステップ", on_click=gs_step)

st.markdown("### 各男性の現在の婚約者")
for m in MEN:
    if m in st.session_state.engaged:
        st.markdown(f"{m} ❤️ {st.session_state.engaged[m]}")
    else:
        st.markdown(f"{m} ❤️ （未婚）")

st.markdown("### 現在の状態（図示）")
current_matching = [(m, w) for m, w in st.session_state.engaged.items()]
fig = draw_state_with_proposals(current_matching, st.session_state.proposals, st.session_state.men_prefs, st.session_state.women_prefs)
st.pyplot(fig)
