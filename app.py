import streamlit as st
import pandas as pd

st.set_page_config(page_title="小選挙区 10年合算 有権者無責任度ランキング", layout="wide")

st.title("🗳️ 全国289小選挙区 10年合算 有権者無責任度（バカ度）ランキング")
st.markdown("""
**【このランキングについて】**
過去10年間（直近3回の衆院選）のデータに基づき、「有権者がどれほどチェック機能を放棄してきたか」を数値化しました。特定の政治家を批判するものではありません。
* **初期値100点（各回）の3回平均スコア**です。点数が低いほど、有権者のチェック機能が働いていないことを示します。
* **減点基準:** 重大不祥事（-50点/-30点 ※投票日時点で公的処分が下っていたもの）、世襲（-5点）、低投票率（60%を基準に1%につき-1点）。
---
""")

@st.cache_data
def load_data():
    # GitHubに保存したマスターデータを読み込む
    df = pd.read_csv("japan_voter_ranking_master.csv")
    
    # スコアが低い順（ワースト順）に並び替え
    df = df.sort_values("10年総合スコア").reset_index(drop=True)
    
    # ワースト順位を付ける (1からスタート)
    df.index = df.index + 1
    df = df.reset_index().rename(columns={"index": "ワースト順位"})
    
    # 空欄（欠損値）をハイフンに変換（エラー防止）
    df = df.fillna("-")
    return df

try:
    df = load_data()
except Exception as e:
    st.error("データの読み込みに失敗しました。ファイルが正しく保存されているか確認してください。")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔍 地元を検索 (市区町村・候補者名)", "📊 総合ランキング", "⚠ 次回要注意リスト"])

with tab1:
    st.subheader("🔍 あなたの選挙区を検索")
    search_query = st.text_input("市区町村名、または候補者名、政党名を入力してください（例：八王子市、世耕、千葉県）")
    if search_query:
        # 複数の列からキーワードを検索
        mask = (
            df["選挙区"].astype(str).str.contains(search_query) | 
            df["市区町村"].astype(str).str.contains(search_query) | 
            df["2024年当選者"].astype(str).str.contains(search_query) |
            df["2024年政党"].astype(str).str.contains(search_query)
        )
        filtered_df = df[mask]
        
        if len(filtered_df) > 0:
            display_cols = ["ワースト順位", "選挙区", "市区町村", "10年総合スコア", "2024年当選者", "2024年政党", "世襲減点", "不祥事減点", "当選後発覚"]
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("該当するデータが見つかりません。別のキーワードを試してください。")
    else:
        st.info("👆 上のボックスに市区町村名を入力すると、あなたの地元の「バカ度」が表示されます。")

with tab2:
    st.subheader("10年合算 総合スコア（ワースト順）")
    st.markdown("※列名をクリックすると並び替えができます。横にスクロールして全項目を確認できます。")
    display_df = df[["ワースト順位", "選挙区", "10年総合スコア", "2024年当選者", "2024年政党", "世襲減点", "不祥事減点", "当選後発覚"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("⚠ 公的処分歴があるにもかかわらず通してしまったリスト")
    st.markdown("今回の選挙において、重大な不祥事の減点があったにも関わらず当選した議員です。")
    warning_df = df[df["次回要注意"] != "-"]
    if len(warning_df) > 0:
        st.table(warning_df[["ワースト順位", "選挙区", "次回要注意", "2024年政党", "10年総合スコア"]])
    else:
        st.write("現在、該当するデータはありません。")
