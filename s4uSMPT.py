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

try:
    st.set_option("deprecation.showPyplotGlobalUse", False)
except Exception:
    pass

st.title("安定マッチング問題")
st.markdown("---")
st.markdown("""
<div style='font-size: small; margin-bottom: 10px;'>
リンク：
<a href="https://kjtum.github.io/labpage/poster.pdf" target="_blank">▶ 安定結婚問題の説明</a>　
　<a href="https://eoghzzfgagjzk9e8pucwam.streamlit.app/" target="_blank">▶ 安定マッチング探索GS法</a>　
  <a href="https://kjtum.github.io/labpage/stproofness.pdf" target="_blank">▶ 耐戦略性の説明</a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='font-size: small; margin-bottom: 10px;'>
ページ内リンク：　
<a href="#allM">▶ 求まった安定マッチング</a>　
　<a href="#idx">▶ 各指標での安定マッチング比較</a>
</div>
""", unsafe_allow_html=True)

# -------------------- 初期化UI（メイン画面に表示） -------------------- #
preset_keys = sorted(BEST_PREFS.keys())

st.markdown("---")
st.markdown("### 好みの初期化")
col_init1, col_init2, col_init3 = st.columns([2, 1, 1])

with col_init1:
    choice = st.selectbox("好みパターン番号を選択", preset_keys)

with col_init2:
    if st.button("このパターンで初期化"):
        st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[choice]

with col_init3:
    if st.button("好みをランダム初期化"):
        def generate_random_prefs():
            men = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
            women = {w: random.sample(MEN, len(MEN)) for w in WOMEN}
            return men, women
        st.session_state.men_prefs, st.session_state.women_prefs = generate_random_prefs()

if 'men_prefs' not in st.session_state:
    st.session_state.men_prefs, st.session_state.women_prefs = BEST_PREFS[preset_keys[0]]

# -------------------- 安定性判定 -------------------- #
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

st.markdown("---")
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

# -------------------- マッチング表示 -------------------- #
st.markdown('<a name="allM"></a>', unsafe_allow_html=True)
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

# -------------------- 結果表 -------------------- #
df = pd.DataFrame(results, columns=["満足度合計", "男性和", "女性和", "差", "最小"], index=roman_labels[:len(matchings)])

def highlight_special(df: pd.DataFrame):
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    styles.loc[df["満足度合計"] == df["満足度合計"].max(), "満足度合計"] = "color:red; font-weight:bold;"
    styles.loc[df["男性和"] == df["男性和"].max(), "男性和"] = "color:red; font-weight:bold;"
    styles.loc[df["女性和"] == df["女性和"].max(), "女性和"] = "color:red; font-weight:bold;"
    styles.loc[df["差"] == df["差"].min(), "差"] = "color:red; font-weight:bold;"
    styles.loc[df["最小"] == df["最小"].max(), "最小"] = "color:red; font-weight:bold;"
    return styles

st.markdown("---")
st.markdown('<a name="idx"></a>', unsafe_allow_html=True)
st.markdown("### 5つの指標での安定マッチングの比較")
st.dataframe(df.style.apply(highlight_special, axis=None), use_container_width=True)

# -------------------- ソースダウンロード -------------------- #
try:
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    st.download_button(label="Python ソースをダウンロード", data=source_code, file_name="4uSMPT4_ui_fixed.py", mime="text/x-python")
except Exception as e:
    st.warning(f"ソースの読み込みに失敗しました: {e}")
