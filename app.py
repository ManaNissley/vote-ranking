import streamlit as st
import pandas as pd

st.set_page_config(page_title="小選挙区 10年合算 有権者無責任度ランキング", layout="wide")

st.title("🗳️ 全国289小選挙区 10年合算 有権者無責任度（バカ度）ランキング")
st.markdown("""
**【このランキングについて】**
過去10年間（直近3回の衆院選）のデータに基づき、「有権者がどれほどチェック機能を放棄してきたか」を数値化しました。特定の政治家を批判するものではありません。
* **初期値100点（各回）の3回平均スコア**です。点数が低いほど、有権者のチェック機能が働いていないことを示します。
* **減点基準:** 重大不祥事（-50点/-30点 ※投票日時点で公的処分が下っていたもの）、世襲（-5点）、低投票率（60%を基準に1%につき-1点）。

⚠️ **【区割り変更に関する注釈】**
2022年の「10増10減」等により、多くの選挙区で区割りが変更されています。本ランキングは「現在の289選挙区」を基準にしているため、過去（2017・2021年）のデータは変更前の区域での結果が紐づいている場合があります。
---
""")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("japan_voter_ranking_master.csv")
    df = df.drop_duplicates(subset=["選挙区"], keep="last")
    df = df[df["選挙区"] != "広島県 7区"]
    
    def check_new_district(row):
        if "新設前" in str(row["2021年当選者"]):
            return "🆕2024年新設区"
        return "-"
    df.insert(3, "備考", df.apply(check_new_district, axis=1))

    df = df.sort_values("10年総合スコア").reset_index(drop=True)
    df.index = df.index + 1
    df = df.reset_index().rename(columns={"index": "ワースト順位"})
    df = df.fillna("-")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("データの読み込みに失敗しました。")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 総合ランキング", "🔍 地元を検索", "⚠ 次回要注意リスト"])

display_cols = [
    "ワースト順位", "選挙区", "10年総合スコア", "備考",
    "2024年当選者", "2024年政党", "2024年投票率",
    "2021年当選者", "2021年投票率",
    "2017年当選者", "2017年投票率",
    "世襲減点", "不祥事減点", "当選後発覚"
]

# 【修正箇所】「備考」と「当選後発覚」をちょうど良いサイズ（medium）に設定
column_config_settings = {
    "当選後発覚": st.column_config.TextColumn(width="medium"),
    "備考": st.column_config.TextColumn(width="small"),
    "選挙区": st.column_config.TextColumn(width="small")
}

with tab1:
    st.subheader(f"10年合算 総合スコア（全{len(df)}選挙区 ワースト順）")
    st.markdown("※表は横にスクロールできます。列名をクリックすると並び替えが可能です。")
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True, column_config=column_config_settings)

with tab2:
    st.subheader("🔍 あなたの選挙区を検索")
    search_query = st.text_input("市区町村名、候補者名、政党名を入力してください")
    if search_query:
        mask = (
            df["選挙区"].astype(str).str.contains(search_query) | 
            df["市区町村"].astype(str).str.contains(search_query) | 
            df["2024年当選者"].astype(str).str.contains(search_query) |
            df["2024年政党"].astype(str).str.contains(search_query) |
            df["2021年当選者"].astype(str).str.contains(search_query) |
            df["2017年当選者"].astype(str).str.contains(search_query)
        )
        filtered_df = df[mask]
        
        if len(filtered_df) > 0:
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True, column_config=column_config_settings)
        else:
            st.warning("該当するデータが見つかりません。")
    else:
        st.info("👆 上のボックスに市区町村名や過去の候補者名を入力すると表示されます。")

with tab3:
    st.subheader("⚠ 公的処分歴があるにもかかわらず通してしまったリスト")
    warning_df = df[df["次回要注意"] != "-"]
    if len(warning_df) > 0:
        st.table(warning_df[["ワースト順位", "選挙区", "次回要注意", "2024年政党", "10年総合スコア"]])
    else:
        st.write("現在、該当するデータはありません。")
