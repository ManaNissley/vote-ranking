import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="10年合算 有権者無責任度ランキング", layout="wide")

# ==========================================
# 1. サイドバーで「衆議院 / 参議院」を切り替え
# ==========================================
st.sidebar.title("🏛️ 選挙の種類を選択")
election_type = st.sidebar.radio(
    "",
    ("衆議院（小選挙区）", "参議院（都道府県選挙区）")
)

st.sidebar.markdown("---")
st.sidebar.markdown("**【評価の仕組み】**")
st.sidebar.write("初期値100点から、低投票率・世襲・重大不祥事などの「有権者のチェック機能の欠如」を減点方式でスコア化しています。")

# ==========================================
# 2. データの読み込み関数
# ==========================================
@st.cache_data(ttl=60)
def load_data(election_type):
    if election_type == "衆議院（小選挙区）":
        file_path = "japan_voter_ranking_master.csv"
    else:
        file_path = "japan_voter_ranking_sangiin.csv"

    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df = df.drop_duplicates(subset=["選挙区"], keep="last")
    
    if election_type == "衆議院（小選挙区）":
        df = df[df["選挙区"] != "広島県 7区"]
        def check_new_district(row):
            if "新設前" in str(row.get("2021年当選者", "")):
                return "🆕2024年新設区"
            return "-"
        if "備考" not in df.columns:
            df.insert(3, "備考", df.apply(check_new_district, axis=1))

    df = df.sort_values("10年総合スコア").reset_index(drop=True)
    df.index = df.index + 1
    df = df.reset_index().rename(columns={"index": "ワースト順位"})
    df = df.fillna("-")
    return df

# ==========================================
# 3. メイン画面の描画
# ==========================================
st.title(f"🗳️ {election_type} 10年合算 有権者無責任度（バカ度）ランキング")
st.markdown("""
**【このランキングについて】**
過去10年間のデータに基づき、「有権者がどれほどチェック機能を放棄してきたか」を数値化しました。特定の政治家を批判するものではありません。
* **減点基準:** 重大不祥事、世襲、低投票率（60%を基準）。
* 参議院等の複数人区は「定数における平均減点」を採用しています。
---
""")

df = load_data(election_type)

if df is None:
    st.info(f"🚧 現在、**{election_type}** のデータは集計中（準備中）です。もうしばらくお待ちください！")
    st.stop()

if election_type == "衆議院（小選挙区）":
    display_cols = [
        "ワースト順位", "選挙区", "10年総合スコア", "備考",
        "2024年当選者", "2024年政党", "2024年投票率",
        "2021年当選者", "2021年投票率",
        "2017年当選者", "2017年投票率",
        "世襲減点", "不祥事減点", "当選後発覚"
    ]
else:
    display_cols = [
        "ワースト順位", "選挙区", "10年総合スコア", "備考",
        "2025年当選者", "2025年政党", "2025年投票率",
        "2022年当選者", "2022年投票率",
        "2019年当選者", "2019年投票率",
        "2016年当選者", "2016年投票率",
        "世襲減点", "不祥事減点", "当選後発覚"
    ]

column_config_settings = {
    "当選後発覚": st.column_config.TextColumn(width="medium"),
    "備考": st.column_config.TextColumn(width="medium")
}

tab1, tab2, tab3, tab4 = st.tabs(["📊 総合ランキング", "🔍 地元を検索", "📈 データ分析・グラフ", "⚠ 次回要注意リスト"])

with tab1:
    st.subheader(f"10年合算 総合スコア（全{len(df)}選挙区 ワースト順）")
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True, column_config=column_config_settings)

with tab2:
    st.subheader("🔍 あなたの選挙区を検索")
    search_query = st.text_input("市区町村名、候補者名、政党名を入力してください")
    
    if search_query:
        # === 修正箇所：安全な検索フィルター処理 ===
        mask = df["選挙区"].astype(str).str.contains(search_query, na=False)
        
        if "市区町村" in df.columns:
            mask = mask | df["市区町村"].astype(str).str.contains(search_query, na=False)
            
        if election_type == "衆議院（小選挙区）":
            search_cols = ["2024年当選者", "2024年政党", "2021年当選者", "2017年当選者"]
        else:
            search_cols = ["2025年当選者", "2025年政党", "2022年当選者", "2019年当選者", "2016年当選者"]
            
        for col in search_cols:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.contains(search_query, na=False)
                
        filtered_df = df[mask]
        # =====================================

        if len(filtered_df) > 0:
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True, column_config=column_config_settings)
            
            if len(filtered_df) == 1:
                st.markdown("---")
                st.subheader(f"📊 {filtered_df.iloc[0]['選挙区']} の詳細分析")
                row = filtered_df.iloc[0]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📉 過去の投票率推移**")
                    if election_type == "衆議院（小選挙区）":
                        turnout_data = pd.DataFrame({
                            "年": ["2017年", "2021年", "2024年"],
                            "投票率(%)": [row["2017年投票率"], row["2021年投票率"], row["2024年投票率"]]
                        })
                    else:
                        turnout_data = pd.DataFrame({
                            "年": ["2016年", "2019年", "2022年", "2025年"],
                            "投票率(%)": [row["2016年投票率"], row["2019年投票率"], row["2022年投票率"], row["2025年投票率"]]
                        })
                        
                    turnout_data["投票率(%)"] = pd.to_numeric(turnout_data["投票率(%)"], errors="coerce")
                    
                    turnout_chart = alt.Chart(turnout_data).mark_line(point=True).encode(
                        x=alt.X("年:N", sort=None, title="", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("投票率(%):Q", title=["投", "票", "率", "(%)"], scale=alt.Scale(zero=False), axis=alt.Axis(titleAngle=0, titleY=-10, titleX=-60, titleAlign='center'))
                    ).properties(height=300)
                    st.altair_chart(turnout_chart, use_container_width=True)
                
                with col2:
                    st.markdown("**💥 減点要因の内訳**")
                    turnout_penalty = 100 - (pd.to_numeric(row["10年総合スコア"], errors='coerce') - pd.to_numeric(row.get("世襲減点", 0), errors='coerce') - pd.to_numeric(row.get("不祥事減点", 0), errors='coerce'))
                    penalties = pd.DataFrame({
                        "減点理由": ["①投票率の低さ", "②世襲", "③不祥事"],
                        "引かれた点数": [round(turnout_penalty, 1), abs(pd.to_numeric(row.get("世襲減点", 0), errors='coerce')), abs(pd.to_numeric(row.get("不祥事減点", 0), errors='coerce'))]
                    })
                    
                    base_pen = alt.Chart(penalties).encode(
                        x=alt.X("減点理由:N", sort=["①投票率の低さ", "②世襲", "③不祥事"], title="", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("引かれた点数:Q", title=list("引かれた点数"), axis=alt.Axis(titleAngle=0, titleY=20, titleX=-60, titleAlign='center'))
                    )
                    bar_pen = base_pen.mark_bar().encode(color=alt.Color("減点理由:N", legend=None))
                    text_pen = base_pen.mark_text(dy=-10).encode(text=alt.Text("引かれた点数:Q", format=".1f"))
                    
                    st.altair_chart((bar_pen + text_pen).properties(height=300), use_container_width=True)
            else:
                st.info("💡 もう少しキーワードを足して【1つの選挙区に絞り込む】と、詳細なグラフが表示されます！")
        else:
            st.warning("該当するデータが見つかりません。")
    else:
        st.info("👆 上のボックスに市区町村名や過去の候補者名を入力すると表示されます。")

with tab3:
    st.subheader("📈 データ分析（全国傾向）")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**全国のスコア分布**")
        # ヒストグラム用に数値型に変換
        df["10年総合スコア_num"] = pd.to_numeric(df["10年総合スコア"], errors="coerce")
        chart1 = alt.Chart(df).mark_bar(color='#4C72B0').encode(
            alt.X("10年総合スコア_num:Q", bin=alt.Bin(maxbins=20), title="10年総合スコア（点）"),
            alt.Y("count():Q", title=list("選挙区の数"), axis=alt.Axis(titleAngle=0, titleY=20, titleX=-60, titleAlign='center')),
            tooltip=["count()"]
        ).properties(height=350)
        st.altair_chart(chart1, use_container_width=True)
        st.caption("※右にいくほどスコアが高い（チェックが機能している）ことを示します。")

    with col2:
        party_col = "2024年政党" if election_type == "衆議院（小選挙区）" else "2025年政党"
        st.markdown(f"**{party_col}別の平均スコア**")
        df[party_col] = df[party_col].astype(str)
        party_scores = df.groupby(party_col)["10年総合スコア_num"].mean().reset_index()
        party_scores = party_scores.sort_values("10年総合スコア_num", ascending=False)
        
        base_chart2 = alt.Chart(party_scores).encode(
            x=alt.X(f"{party_col}:N", sort="-y", title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("10年総合スコア_num:Q", title=list("平均スコア"), axis=alt.Axis(titleAngle=0, titleY=20, titleX=-60, titleAlign='center')),
            tooltip=[party_col, "10年総合スコア_num"]
        )
        bar2 = base_chart2.mark_bar().encode(
            color=alt.Color(f"{party_col}:N", legend=None)
        )
        text2 = base_chart2.mark_text(dy=-10).encode(
            text=alt.Text("10年総合スコア_num:Q", format=".1f")
        )
        st.altair_chart((bar2 + text2).properties(height=350), use_container_width=True)
        st.caption("※直近の選挙で勝利した政党ごとに、その選挙区の過去10年スコア平均を出したものです。")

with tab4:
    st.subheader("⚠ 公的処分歴があるにもかかわらず通してしまったリスト")
    if "次回要注意" in df.columns:
        warning_df = df[df["次回要注意"] != "-"]
        if len(warning_df) > 0:
            st.table(warning_df[["ワースト順位", "選挙区", "次回要注意", "10年総合スコア"]])
        else:
            st.write("現在、該当するデータはありません。")
    else:
        st.write("データがありません。")
