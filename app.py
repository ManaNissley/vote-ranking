import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="小選挙区 10年合算 有権者無責任度ランキング", layout="wide")

# タイトルと免責事項
st.title("🗳️ 小選挙区 10年合算 有権者無責任度（バカ度）ランキング")
st.markdown("""
**【このランキングについて】**
本データは、過去10年間（直近3回の衆院選）の客観的データに基づき、「私たち有権者がどれほどチェック機能を放棄してきたか」を数値化したものです。特定の地域や政治家を批判するものではありません。
*   **初期値100点（各回）の3回平均スコア**です。点数が低いほど、有権者のチェック機能が働いていないことを示します。
*   **減点基準:** 重大不祥事（-50点/-30点 ※投票日時点で公的処分が下っていたものに限る）、世襲（-5点）、低投票率（60%を基準に1%につき-1点）。
*   ※表の見出しをクリックすると、自由に並び替えができます。
---
""")

# CSVデータの読み込み（完全版データ）
@st.cache_data
def load_data():
    # GitHub上に一緒にアップロードするCSVファイルを読み込みます
    df = pd.read_csv("japan_voter_irresponsibility_ranking_289.csv")
    return df

df = load_data()

# タブの作成
tab1, tab2, tab3 = st.tabs(["📊 総合ランキング", "⚠️ 次回要注意リスト", "🔍 データ検索"])

with tab1:
    st.subheader("10年合算 総合スコア（ワースト順）")
    st.markdown("※列名（世襲減点など）をクリックすると、その項目で並び替えができます。")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("⚠️️ 2024年選挙での「思考停止」リスト")
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
