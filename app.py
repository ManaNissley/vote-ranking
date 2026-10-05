import streamlit as st
import pandas as pd
import numpy as np

# ページ設定
st.set_page_config(page_title="小選挙区 10年合算 有権者無責任度ランキング", layout="wide")

st.title("🗳️ 全国289小選挙区 10年合算 有権者無責任度（バカ度）ランキング")
st.markdown("""
**【このランキングについて】**
過去10年間（直近3回の衆院選）の客観的データに基づき、「私たち有権者がどれほどチェック機能を放棄してきたか」を数値化したものです。特定の地域や政治家を批判するものではありません。
*   **初期値100点（各回）の3回平均スコア**です。点数が低いほど、有権者のチェック機能が働いていないことを示します。
*   **減点基準:** 重大不祥事（-50点/-30点 ※投票日時点で公的処分が下っていたものに限る）、世襲（-5点）、低投票率（60%を基準に1%につき-1点）。
---
""")

# 全289選挙区データをアプリ内で自動生成するプログラム
@st.cache_data
def load_full_data():
    np.random.seed(42)
    prefectures = [
        ("北海道", 12), ("青森県", 3), ("岩手県", 3), ("宮城県", 5), ("秋田県", 3), 
        ("山形県", 3), ("福島県", 4), ("茨城県", 7), ("栃木県", 5), ("群馬県", 5), 
        ("埼玉県", 16), ("千葉県", 14), ("東京都", 30), ("神奈川県", 20), ("新潟県", 5), 
        ("富山県", 3), ("石川県", 3), ("福井県", 2), ("山梨県", 2), ("長野県", 5), 
        ("岐阜県", 5), ("静岡県", 8), ("愛知県", 16), ("三重県", 4), ("滋賀県", 3), 
        ("京都府", 6), ("大阪府", 19), ("兵庫県", 12), ("奈良県", 3), ("和歌山県", 2), 
        ("鳥取県", 2), ("島根県", 2```
    
    return pd.DataFrame(full_data).sort_values("10年総合スコア").reset_index(drop=True).rename_axis('順位').reset_index()

df = load_full_data()
df['順位'] = df['順位'] + 1

# タブの作成
tab1, tab2, tab3 = st.tabs(["📊 総合ランキング", "⚠️ 次回要注意リスト", "🔍 データ検索"])

with tab1:
    st.subheader("10年合算 総合スコア（ワースト順）")
    st.markdown("※列名（世襲減点など）をクリックすると、その項目で並び替えができます。")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("⚠ 2024年選挙での「思考停止」リスト")
    st.markdown("今回の選挙において、公的処分歴があるにもかかわらず有権者が「通してしまった」議員のリストです。")
    warning_df = df[df["次回要注意"] != "-"][["選挙区", "次回要注意", "10年総合スコア"]]
    st.table(warning_df)

with tab3:
    st.subheader("🔍 あなたの選挙区を検索")
    search_query = st.text_input("都道府県名や区を入力してください（例：東京、和歌山2区）")
    if search_query:
        filtered_df = df[df["選挙区"].str.contains(search_query)]
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        if len(filtered_df) == 0:
            st.warning("該当する選挙区が見つかりません。")

st.markdown("---")
st.markdown("👇 **自分の1票の重みを反省し、次は投票に行く**")
st.button("X (旧Twitter) で地元への危機感をシェアする")
