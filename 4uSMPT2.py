import streamlit as st
import random
import itertools
import matplotlib.pyplot as plt
from PIL import Image
import os
import pandas as pd
from best20_prefs import BEST_PREFS

MEN = ["A", "B", "C", "D"]
WOMEN = ["X", "Y", "Z", "W"]
IMAGE_DIR = "img"

st.title("安定マッチング問題")
st.markdown("""
<div style='font-size: small; margin-bottom: 10px;'>
    <a href="explain.html" target="_blank">▶ 安定結婚問題の説明</a><br>
    <a href="https://jht72mtp85txu9zih7gn5m.streamlit.app/" target="_blank">▶ 安定マッチング使用方法</a><br>
    <a href="https://ja.wikipedia.org/wiki/安定結婚問題" target="_blank">▶ Wikipedia（安定結婚問題）</a>
</div>
""", unsafe_allow_html=True)

preset_keys = sorted(BEST_PREFS.keys())
choice = st.sidebar.selectbox("好みパターン番号を選択", preset_keys)
if st.sidebar.button("このパターンで初期化"):
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[choice]

if st.sidebar.button("好みをランダム初期化"):
    def generate_random_prefs():
        men = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
        women = {w: random.sample(MEN, len(MEN)) for w in WOMEN}
        return men, women
    st.session_state.men_prefs, st.session_state.women_prefs = generate_random_prefs()

if 'men_prefs' not in st.session_state:
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[preset_keys[0]]

def is_stable(matching, men_prefs, women_prefs):
    man2woman = {m: w for m, w in matching}
    woman2man = {w: m for m, w in matching}
    for m, w in matching:
        for w2 in men_prefs[m][:men_prefs[m].index(w)]:
            if women_prefs[w2].index(m) < women_prefs[w2].index(woman2man[w2]):
                return False
    for w, m in woman2man.items():
        for m2 in women_prefs[w][:women_prefs[w].index(m)]:
            if men_prefs[m2].index(w) < men_prefs[m2].index(man2woman[m2]):
                return False
    return True

def all_stable_matchings(men_prefs, women_prefs):
    stable = []
    for perm in itertools.permutations(WOMEN):
        mlist = list(zip(MEN, perm))
        if is_stable(mlist, men_prefs, women_prefs):
            stable.append(mlist)
    return stable

def calculate_dissatisfaction(matching, men_prefs, women_prefs):
    man_score = sum(men_prefs[m].index(w) for m, w in matching)
    woman_score = sum(women_prefs[w].index(m) for m, w in matching)
    total = man_score + woman_score
    diff = abs(man_score - woman_score)
    max_score = max(max(men_prefs[m].index(w), women_prefs[w].index(m)) for m, w in matching)
    return total, man_score, woman_score, diff, max_score

def draw_matching_with_images(matching, men_prefs, women_prefs):
    fig, ax = plt.subplots(figsize=(6, 2.4), dpi=800)
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
        satisfaction_m = 3 - men_prefs[m].index(w)
        ax.text(x_men-woff-0.02, y_m, f"({satisfaction_m}) {m}", va='center', ha='right', fontsize=10, zorder=3)
        pw = os.path.join(IMAGE_DIR, f"{w}.png")
        if os.path.exists(pw):
            img = Image.open(pw).resize((icon_w, icon_h), Image.LANCZOS)
            ax.imshow(img, extent=(x_women-woff, x_women+woff, y_w-hoff, y_w+hoff), zorder=2)
        satisfaction_w = 3 - women_prefs[w].index(m)
        ax.text(x_women+woff+0.02, y_w, f"({satisfaction_w}) {w}", va='center', ha='left', fontsize=10, zorder=3)
    ax.set_xlim(0,1)
    ax.set_ylim(- (len(MEN)-1) * spacing - 0.3, 0.3)
    plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0)
    return fig

# 現在の好み表示
st.subheader("現在の好み")
col1, col2 = st.columns(2)
with col1:
    for m in MEN:
        row_cols = st.columns([0.3, 3])
        with row_cols[0]:
            img_path = os.path.join(IMAGE_DIR, f"{m}.png")
            if os.path.exists(img_path):
                st.image(img_path, width=30)
        with row_cols[1]:
            new = st.multiselect(f"{m} の好み", WOMEN, default=st.session_state.men_prefs[m], key=f"men_{m}")
            if len(new) == len(WOMEN):
                st.session_state.men_prefs[m] = new
with col2:
    for w in WOMEN:
        row_cols = st.columns([0.3, 3])
        with row_cols[0]:
            img_path = os.path.join(IMAGE_DIR, f"{w}.png")
            if os.path.exists(img_path):
                st.image(img_path, width=30)
        with row_cols[1]:
            new = st.multiselect(f"{w} の好み", MEN, default=st.session_state.women_prefs[w], key=f"women_{w}")
            if len(new) == len(MEN):
                st.session_state.women_prefs[w] = new

# マッチングと表の表示
st.markdown("---")
st.subheader("安定マッチング一覧")
matchings = all_stable_matchings(st.session_state.men_prefs, st.session_state.women_prefs)
results = []
roman_labels = ['(i)', '(ii)', '(iii)', '(iv)', '(v)', '(vi)', '(vii)', '(viii)', '(ix)', '(x)']

for i in range(0, len(matchings), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j >= len(matchings): break
        mlist = matchings[i + j]
        total, ms, ws, diff, maxd = calculate_dissatisfaction(mlist, st.session_state.men_prefs, st.session_state.women_prefs)
        total_satis = 3 * 2 * len(mlist) - total
        ms_satis = 3 * len(mlist) - ms
        ws_satis = 3 * len(mlist) - ws
        diff_satis = abs(ms_satis - ws_satis)
        max_satis = 3 - maxd
        results.append([total_satis, ms_satis, ws_satis, diff_satis, max_satis])
        with cols[j]:
            st.markdown(f"**{roman_labels[i + j]} 満足度合計 {total_satis} (男性和 {ms_satis}, 女性和 {ws_satis})<br>差 {diff_satis}, 最小 {max_satis}**", unsafe_allow_html=True)
            st.markdown(f"**{', '.join([f'{m}→{w}' for m, w in mlist])}**", unsafe_allow_html=True)
            st.pyplot(draw_matching_with_images(mlist, st.session_state.men_prefs, st.session_state.women_prefs))

# 表表示
df = pd.DataFrame(results, columns=["満足度合計", "男性和", "女性和", "差", "最小"], index=roman_labels[:len(matchings)])
st.markdown("### 安定マッチング")
st.dataframe(df, use_container_width=True)
