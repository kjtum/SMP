
import streamlit as st
import random
import itertools
import matplotlib.pyplot as plt
from PIL import Image
import os
import pandas as pd
from best20_prefs import BEST_PREFS

# -------------------- 基本設定 -------------------- #
MEN = ["A", "B", "C", "D"]
WOMEN = ["X", "Y", "Z", "W"]
IMAGE_DIR = "img"

st.set_option("deprecation.showPyplotGlobalUse", False)  # グローバル pyplot 使用の警告抑止
st.title("安定マッチング問題")

st.markdown("""
<div style='font-size: small; margin-bottom: 10px;'>
    <a href="explain.html" target="_blank">▶ 安定結婚問題の説明</a><br>
    <a href="https://jht72mtp85txu9zih7gn5m.streamlit.app/" target="_blank">▶ 安定マッチング使用方法</a><br>
    <a href="https://ja.wikipedia.org/wiki/安定結婚問題" target="_blank">▶ Wikipedia（安定結婚問題）</a>
</div>
""", unsafe_allow_html=True)

# -------------------- 初期化 -------------------- #
preset_keys = sorted(BEST_PREFS.keys())
choice = st.sidebar.selectbox("好みパターン番号を選択", preset_keys)

def generate_random_prefs():
    men = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
    women = {w: random.sample(MEN, len(MEN)) for w in WOMEN}
    return men, women

if st.sidebar.button("このパターンで初期化"):
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[choice]

if st.sidebar.button("好みをランダム初期化"):
    st.session_state.men_prefs, st.session_state.women_prefs = generate_random_prefs()

if 'men_prefs' not in st.session_state:
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[preset_keys[0]]

# -------------------- 安定性判定 -------------------- #
def is_stable(matching, men_prefs, women_prefs):
    man2woman = {m: w for m, w in matching}
    woman2man = {w: m for m, w in matching}
    # 男性主導のブロッキングペア確認
    for m, w in matching:
        for w2 in men_prefs[m][:men_prefs[m].index(w)]:
            if women_prefs[w2].index(m) < women_prefs[w2].index(woman2man[w2]):
                return False
    # 女性主導のブロッキングペア確認
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

# -------------------- 満足度計算 -------------------- #
def calculate_dissatisfaction(matching, men_prefs, women_prefs):
    man_score = sum(men_prefs[m].index(w) for m, w in matching)
    woman_score = sum(women_prefs[w].index(m) for m, w in matching)
    total = man_score + woman_score
    diff = abs(man_score - woman_score)
    max_score = max(max(men_prefs[m].index(w), women_prefs[w].index(m)) for m, w in matching)
    return total, man_score, woman_score, diff, max_score

# -------------------- マッチング図描画 -------------------- #
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
    ax.set_xlim(0, 1)
    ax.set_ylim(- (len(MEN) - 1) * spacing - 0.3, 0.3)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0)
    return fig

# -------------------- 現在の好み表示 -------------------- #
st.subheader("現在の好み")
col1, col2 = st.columns(2)

# --- 男性の好み --- #
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

# --- 女性の好み --- #
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

# -------------------- マッチングと図の表示 -------------------- #
st.markdown("---")
st.subheader("安定マッチング一覧")
matchings = all_stable_matchings(st.session_state.men_prefs, st.session_state.women_prefs)
results = []
roman_labels = ['(i)', '(ii)', '(iii)', '(iv)', '(v)', '(vi)', '(vii)', '(viii)', '(ix)', '(x)']

for i in range(0, len(matchings), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j >= len(matchings):
            break
        mlist = matchings[i + j]

        # ----- 満足度計算 ----- #
        total, ms, ws, diff, maxd = calculate_dissatisfaction(mlist, st.session_state.men_prefs, st.session_state.women_prefs)
        total_satis = 3 * 2 * len(mlist) - total
        ms_satis = 3 * len(mlist) - ms
        ws_satis = 3 * len(mlist) - ws
        diff_satis = abs(ms_satis - ws_satis)
        max_satis = 3 - maxd
        results.append([total_satis, ms_satis, ws_satis, diff_satis, max_satis])

        # ----- 表示 ----- #
        with cols[j]:
            st.markdown(
                f"**{roman_labels[i + j]} 満足度合計 {total_satis} (男性和 {ms_satis}, 女性和 {ws_satis})<br>差 {diff_satis}, 最小 {max_satis}**",
                unsafe_allow_html=True)
            st.markdown(
                f"**{', '.join([f'{m}→{w}' for m, w in mlist])}**",
                unsafe_allow_html=True)
            st.pyplot(draw_matching_with_images(mlist, st.session_state.men_prefs, st.session_state.women_prefs))

# -------------------- 結果表作成 -------------------- #
df = pd.DataFrame(results, columns=["満足度合計", "男性和", "女性和", "差", "最小"], index=roman_labels[:len(matchings)])

# --- スタイリング関数 --- #

def highlight_special(dataframe: pd.DataFrame):
    """
    表の列番号は **行ラベルを 1 列目** と数えたときの指定。

    2 列目 (満足度合計) : 最大値を赤太字

    4 列目 (女性和)     : 最小値を赤太字

    5 列目 (差)         : 最大値を赤太字
    """
    styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)

    # 2列目: 満足度合計 (max)
    max_total = dataframe["満足度合計"].max()
    styles.loc[dataframe["満足度合計"] == max_total, "満足度合計"] = "color: red; font-weight: bold;"

    # 4列目: 女性和 (min)
    min_women_sum = dataframe["女性和"].min()
    styles.loc[dataframe["女性和"] == min_women_sum, "女性和"] = "color: red; font-weight: bold;"

    # 5列目: 差 (max)
    max_diff = dataframe["差"].max()
    styles.loc[dataframe["差"] == max_diff, "差"] = "color: red; font-weight: bold;"

    return styles

st.markdown("### 安定マッチング")
styled_df = df.style.apply(highlight_special, axis=None)
st.dataframe(styled_df, use_container_width=True)

# -------------------- ソースダウンロード -------------------- #
# 実行ファイル自身を読み取り専用モードで開き、ダウンロードボタンを提供
try:
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    st.download_button(label="Python ソースをダウンロード", data=source_code, file_name="4uSMPT3_modified.py",
                       mime="text/x-python")
except Exception as e:
    st.warning(f"ソースの読み込みに失敗しました: {e}")
