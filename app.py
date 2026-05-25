import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import numpy as np

# ==========================================
# 1. 網頁基本與高階外觀設定 (全知戰情室 UI)
# ==========================================
st.set_page_config(page_title="手搖飲全知分析戰情室", page_icon="🧋", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #F8FAFC;}
    h1, h2, h3, h4 {color: #0F172A; font-weight: 800; letter-spacing: -0.5px;}
    .stTabs [data-baseweb="tab-list"] {gap: 6px; border-bottom: 2px solid #E2E8F0; flex-wrap: wrap;}
    .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: #F1F5F9; border-radius: 8px 8px 0 0; padding: 0 16px; font-size: 15px; font-weight: 700; color: #64748B; transition: all 0.3s;}
    .stTabs [aria-selected="true"] {background-color: #FFFFFF; border-bottom: 3px solid #6366F1; color: #4F46E5; box-shadow: 0 -4px 6px -1px rgba(0,0,0,0.05);}
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #ffffff, #f0f4f8); border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; 
        box-shadow: 4px 4px 10px rgba(0,0,0,0.03), -4px -4px 10px rgba(255,255,255,0.8); transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {transform: translateY(-3px);}
    </style>
""", unsafe_allow_html=True)

st.title("🧋 台灣手搖飲商業分析戰情室 (全知版)")
st.markdown("融合大數據視覺化、板塊矩陣分析、AI 預測與消費者行為學的終極商業決策系統。")

# ==========================================
# 2. 讀取與預處理資料
# ==========================================
@st.cache_data
def load_data():
    excel_file = "飲料清單.xlsx"
    sheet = "飲料清單"
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df['價格(M)'] = pd.to_numeric(df['價格(M)'], errors='coerce')
        df['價格(L)'] = pd.to_numeric(df['價格(L)'], errors='coerce')
        df['加料'] = pd.to_numeric(df['加料'], errors='coerce')
        df['加料狀態'] = df['加料'].map({1.0: '有加料', 0.0: '純茶/無加料'})
        df['標籤1'] = df['標籤1'].fillna('未分類')
        df['升杯價差'] = df['價格(L)'] - df['價格(M)']
        return df
    except Exception as e:
        st.error(f"❌ 讀取 Excel 失敗，請確認檔案。錯誤: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    all_stores = df['店家'].dropna().unique().tolist()
    market_expectation = df.groupby(['標籤1', '加料狀態'])['價格(L)'].mean().reset_index()
    market_expectation.rename(columns={'價格(L)': '市場預期價'}, inplace=True)
    
    # ==========================================
    # 3. 側邊欄：全域過濾器
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3081/3081162.png", width=80)
        st.header("🎛️ 戰情室控制台")
        st.caption("連動全站 8 大分析模組")
        
        selected_stores = st.multiselect("🏪 選擇分析品牌", options=all_stores, default=all_stores[:7] if len(all_stores)>=7 else all_stores)
        all_bases = df['標籤1'].dropna().unique().tolist()
        selected_base = st.multiselect("🍃 選擇基底茶", options=all_bases)
        topping_option = st.radio("🍬 加料狀態", ["全部", "有加料", "純茶/無加料"])
        
        st.markdown("---")
        st.markdown(f"**資料庫總覽**\n- 總店家數: {len(all_stores)}\n- 總品項數: {len(df)}")

    filtered_df = df.copy()
    if selected_stores: filtered_df = filtered_df[filtered_df['店家'].isin(selected_stores)]
    if selected_base: filtered_df = filtered_df[filtered_df['標籤1'].isin(selected_base)]
    if topping_option != "全部": filtered_df = filtered_df[filtered_df['加料狀態'] == topping_option]

    def apply_common_layout(fig):
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=20, l=10, r=10),
            hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial", bordercolor="#CBD5E1"),
            font=dict(color="#334155")
        )
        fig.update_xaxes(showgrid=False, linecolor='#E2E8F0')
        fig.update_yaxes(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0')
        return fig

    # ==========================================
    # 建立 8 大究極功能頁籤
    # ==========================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 營運總覽", "🗺️ 市場版圖結構", "⚔️ 品牌雷達 PK", "📈 定價與加料", 
        "🔄 動態樞紐", "🤖 AI 預測引擎", "🧠 預期心理", "📋 原始資料"
    ])

    # ------------------------------------------
    # 頁籤 1：營運總覽
    # ------------------------------------------
    with tab1:
        st.markdown("### 🚀 關鍵營運指標 (KPI)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 有效品項總數", f"{len(filtered_df)} 項")
        avg_l_price = filtered_df['價格(L)'].mean()
        col2.metric("💰 均價水位 (大杯)", f"${avg_l_price:.1f}" if pd.notna(avg_l_price) else "N/A")
        topping_pct = (filtered_df['加料'] == 1.0).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        col3.metric("🧋 加料品項佔比", f"{topping_pct:.1f}%")
        col4.metric("🏪 涵蓋品牌數", f"{filtered_df['店家'].nunique()} 家")
        st.markdown("---")
        
        if not filtered_df.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📊 品牌均價排行榜")
                avg_price_df = filtered_df.groupby(['店家', '加料狀態'])['價格(L)'].mean().reset_index()
                fig1 = px.bar(avg_price_df, x='店家', y='價格(L)', color='加料狀態', barmode='group', text_auto='.0f', 
                              color_discrete_map={'有加料': '#F59E0B', '純茶/無加料': '#10B981'})
                fig1.update_layout(xaxis={'categoryorder':'total descending'}, yaxis_title="平均價格 (元)", xaxis_title="")
                fig1 = apply_common_layout(fig1)
                st.plotly_chart(fig1, use_container_width=True)

            with c2:
                st.markdown("#### 🍩 全域基底茶生態圈")
                fig2 = px.pie(filtered_df, names='標籤1', hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism)
                fig2.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05 if i==0 else 0 for i in range(10)])
                fig2.update_layout(margin=dict(t=20, b=10, l=10, r=10), showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

    # ------------------------------------------
    # 頁籤 2：市場定位與結構
    # ------------------------------------------
    with tab2:
        st.markdown("### 🗺️ 市場品牌定位與菜單結構解剖")
        
        if not filtered_df.empty:
            st.markdown("#### 🧱 品牌戰略定價板塊矩陣 (Treemap Matrix)")
            st.caption("完美替代傳統四象限！**板塊面積**代表「品項數量」，**顏色**代表「平均定價」。紅色系代表高單價，藍綠色系代表親民平價。")
            
            quad_df = filtered_df.dropna(subset=['價格(L)']).groupby('店家').agg(品項數=('飲料品項', 'count'), 均價=('價格(L)', 'mean')).reset_index()
            
            if not quad_df.empty:
                fig_tree = px.treemap(quad_df, path=[px.Constant("全市場版圖"), '店家'], values='品項數', color='均價', color_continuous_scale='RdYlBu_r', hover_data={'均價': ':.1f', '品項數': True})
                fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>品項數: %{value} 項<br>大杯均價: $ %{color:.1f}<extra></extra>', textinfo="label+value", textfont=dict(size=16, family="Arial Black"), root_color="lightgrey")
                fig_tree.update_layout(margin=dict(t=30, l=10, r=10, b=20), height=500)
                st.plotly_chart(fig_tree, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 🌌 競爭紅海密集度分析 (Marginal Density Heatmap)")
            st.caption("透過熱力圖與邊際分佈，直接透視「哪個茶種」與「哪個價格帶」是各家品牌交火最密集的『紅海戰區』！")
            
            fig_density = px.density_heatmap(filtered_df.dropna(subset=['價格(L)']), x='標籤1', y='價格(L)', marginal_x="histogram", marginal_y="histogram", text_auto=True)
            fig_density.update_traces(colorscale='Purples', selector=dict(type='histogram2d'))
            fig_density.update_layout(xaxis_title="基底茶種分類", yaxis_title="大杯價格 (元)", height=550, xaxis=dict(tickangle=-45), yaxis=dict(dtick=5))
            fig_density = apply_common_layout(fig_density)
            st.plotly_chart(fig_density, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🌞 專屬品牌菜單宇宙 (Sunburst Chart)")
            st.caption("由內而外展開：品牌 ➔ 基底茶 ➔ 加料狀態 ➔ 單一飲品。區塊大小代表價格貢獻度，顏色深淺代表單價高低。")
            
            valid_sunburst_stores = filtered_df['店家'].unique().tolist()
            if valid_sunburst_stores:
                selected_sun_store = st.selectbox("🔍 選擇要放大解剖的品牌菜單", options=valid_sunburst_stores, index=0)
                sun_df = filtered_df[filtered_df['店家'] == selected_sun_store].dropna(subset=['價格(L)']).copy()
                sun_df = sun_df.fillna("無分類")
                
                fig_sun = px.sunburst(sun_df, path=['店家', '標籤1', '加料狀態', '飲料品項'], values='價格(L)', color='價格(L)', color_continuous_scale='RdYlBu_r')
                fig_sun.update_layout(margin=dict(t=20, l=10, r=10, b=20), height=700)
                fig_sun.update_traces(marker=dict(line=dict(color='#FFFFFF', width=1)), hovertemplate='<b>%{label}</b><br>大杯售價: $ %{color:.0f}<extra></extra>')
                st.plotly_chart(fig_sun, use_container_width=True)
            else:
                st.info("目前條件下無可用品牌資料。")

    # ------------------------------------------
    # 頁籤 3：品牌雷達 PK
    # ------------------------------------------
    with tab3:
        st.markdown("### ⚔️ 品牌 DNA 一對一對決")
        if len(all_stores) >= 2:
            pk_c1, pk_c2 = st.columns(2)
            brand_a = pk_c1.selectbox("🟥 選擇紅方品牌", all_stores, index=0)
            brand_b = pk_c2.selectbox("🟦 選擇藍方品牌", all_stores, index=1 if len(all_stores)>1 else 0)
            if brand_a and brand_b and brand_a != brand_b:
                max_price = df.groupby('店家')['價格(L)'].mean().max()
                max_items = df.groupby('店家').size().max()
                max_bases = df.groupby('店家')['標籤1'].nunique().max()
                
                def get_brand_metrics(brand_name):
                    b_df = df[df['店家'] == brand_name]
                    if b_df.empty: return [0,0,0,0]
                    return [(b_df['價格(L)'].mean() / max_price) * 100, (len(b_df) / max_items) * 100,
                            (b_df['加料'] == 1.0).sum() / len(b_df) * 100 if len(b_df)>0 else 0,
                            (b_df['標籤1'].nunique() / max_bases) * 100]

                metrics_a, metrics_b = get_brand_metrics(brand_a), get_brand_metrics(brand_b)
                categories = ['價格水準 (高單價)', '品項豐富度', '加料專注度', '茶種多樣性']

                radar_c1, radar_c2 = st.columns([1, 1.2])
                with radar_c1:
                    st.markdown("#### 🕸️ 品牌商業模式雷達圖")
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=metrics_a, theta=categories, fill='toself', name=brand_a, line_color='#EF4444'))
                    fig_radar.add_trace(go.Scatterpolar(r=metrics_b, theta=categories, fill='toself', name=brand_b, line_color='#3B82F6'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, margin=dict(t=40, b=40, l=40, r=40))
                    st.plotly_chart(fig_radar, use_container_width=True)

                with radar_c2:
                    st.markdown("#### 📊 價格分佈疊加圖 (Histogram)")
                    pk_df = df[df['店家'].isin([brand_a, brand_b])]
                    fig_pk1 = px.histogram(pk_df, x="價格(L)", color="店家", barmode="overlay", nbins=15, color_discrete_sequence=['#EF4444', '#3B82F6'], opacity=0.7)
                    fig_pk1 = apply_common_layout(fig_pk1)
                    st.plotly_chart(fig_pk1, use_container_width=True)
            else:
                st.warning("⚠️ 請選擇兩個不同的品牌進行 PK！")

    # ------------------------------------------
    # 頁籤 4：定價與加料經濟
    # ------------------------------------------
    with tab4:
        st.markdown("### 📈 定價區間、升杯策略與加料經濟學")
        st.markdown("#### 📋 各品牌定價與升杯策略明細表")
        if not filtered_df.empty:
            summary_table = filtered_df.groupby('店家').agg(
                平均中杯價=('價格(M)', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                平均大杯價=('價格(L)', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                平均升杯價差=('升杯價差', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                最常見升杯價差=('升杯價差', lambda x: f"{int(x.mode().iloc[0])} 元" if not x.mode().empty else "-"),
                有效品項數=('飲料品項', 'count')
            ).reset_index().sort_values(by='有效品項數', ascending=False).reset_index(drop=True)
            summary_table.index += 1
            st.dataframe(summary_table, use_container_width=True)
            
        st.markdown("---")
        box_col, top_col = st.columns(2)
        
        with box_col:
            st.markdown("#### 📦 價格區間與極端值 (盒鬚圖)")
            fig_box = px.box(filtered_df, x='店家', y='價格(L)', color='店家', points="all", hover_data={'店家': False, '飲料品項': True, '加料狀態': True, '價格(L)': ':.0f'})
            fig_box.update_layout(xaxis={'categoryorder':'median descending'}, showlegend=False, yaxis_title="大杯價格 (元)", xaxis_title="")
            fig_box = apply_common_layout(fig_box)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with top_col:
            st.markdown("#### 🍬 加料經濟學：加料平均溢價分析")
            top_pivot = filtered_df.pivot_table(index='店家', columns='加料狀態', values='價格(L)', aggfunc='mean').reset_index()
            if '有加料' in top_pivot.columns and '純茶/無加料' in top_pivot.columns:
                top_pivot['加料溢價'] = top_pivot['有加料'] - top_pivot['純茶/無加料']
                top_pivot = top_pivot.dropna(subset=['加料溢價']).sort_values(by='加料溢價', ascending=False)
                fig_top = px.bar(top_pivot, x='店家', y='加料溢價', text_auto='+.1f', color='加料溢價', color_continuous_scale='Purples')
                fig_top.update_layout(yaxis_title="平均加料溢價 (元)", xaxis_title="")
                fig_top = apply_common_layout(fig_top)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("目前的資料維度不足以計算加料溢價。")

    # ------------------------------------------
    # 頁籤 5：動態樞紐分析
    # ------------------------------------------
    with tab5:
        st.markdown("### 🔄 自由維度樞紐分析")
        st.markdown("自訂 X 軸與 Y 軸，系統將即時運算產生**熱力圖**與**交叉分析數據表**，幫助您快速比對市場資料。")
        p_col1, p_col2, p_col3 = st.columns([1, 1, 2])
        y_axis = p_col1.selectbox("選擇 Y 軸 (列)", ['店家', '標籤1', '加料狀態'], index=0)
        x_axis = p_col2.selectbox("選擇 X 軸 (欄)", ['標籤1', '店家', '加料狀態'], index=1)
        value_axis = p_col3.selectbox("分析數值 (填入儲存格)", ['計算品項數量 (Count)', '平均大杯價格 (Average)'])
            
        if y_axis != x_axis:
            if value_axis == '計算品項數量 (Count)':
                pivot_df = pd.crosstab(filtered_df[y_axis], filtered_df[x_axis])
                color_scale = 'Blues'
            else:
                pivot_df = filtered_df.pivot_table(index=y_axis, columns=x_axis, values='價格(L)', aggfunc='mean').round(1)
                color_scale = 'YlOrRd'

            st.markdown("#### 📊 樞紐分析熱力圖")
            fig_heatmap = px.imshow(pivot_df, text_auto=True, color_continuous_scale=color_scale, aspect="auto")
            fig_heatmap.update_layout(margin=dict(t=20, b=20, l=0, r=0))
            fig_heatmap.update_xaxes(side="top")
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 📋 樞紐分析數據明細表")
            display_df = pivot_df.reset_index()
            if value_axis == '計算品項數量 (Count)':
                display_df = display_df.fillna(0).astype(int, errors='ignore')
            else:
                display_df = display_df.fillna("-")
            st.dataframe(display_df, use_container_width=True)
            
        else:
            st.warning("⚠️ X 軸與 Y 軸不能選擇相同的維度。")

    # ------------------------------------------
    # 頁籤 6：AI 預測引擎 (🔥 本次升級：升杯性價比模型 + 明細表 🔥)
    # ------------------------------------------
    with tab6:
        st.markdown("### 🤖 價格預測與 AI 趨勢線 (升杯性價比模型)")
        st.markdown("利用線性迴歸 AI 模型，找出「中杯升級大杯」的隱藏市場公定價公式。進一步比對實際售價，揪出哪些品項升級大杯是**「薛盤價 (不划算)」**，哪些是**「佛心價 (超值)」**！")
        
        reg_df = filtered_df.dropna(subset=['價格(M)', '價格(L)']).copy()
        reg_df = reg_df[(reg_df['價格(M)'] > 0) & (reg_df['價格(L)'] > 0)]
        
        if len(reg_df) > 5:
            slope, intercept, r_value, p_value, std_err = stats.linregress(reg_df['價格(M)'], reg_df['價格(L)'])
            
            # 1. 執行預測與落差計算
            reg_df['AI預測大杯價'] = reg_df['價格(M)'] * slope + intercept
            reg_df['升杯落差'] = reg_df['價格(L)'] - reg_df['AI預測大杯價']
            
            # 2. 定義判定條件 (大於預測 3 元算貴，小於 3 元算划算)
            def categorize_upgrade(gap):
                if gap > 3: return "⚠️ 升杯溢價 (偏貴)"
                elif gap < -3: return "🔥 超值升杯 (划算)"
                else: return "✅ 合理升杯 (符行情)"
                
            reg_df['AI升杯判定'] = reg_df['升杯落差'].apply(categorize_upgrade)
            
            # 3. 顯示 KPI
            metric_c1, metric_c2, metric_c3 = st.columns(3)
            metric_c1.metric("📐 市場升級斜率", f"{slope:.2f}", help="中杯每增加 1 元，大杯理論上增加的金額。")
            sign = "+" if intercept >= 0 else "-"
            metric_c2.metric("🎯 預測公定價公式", f"大杯 = 中杯 × {slope:.2f} {sign} {abs(intercept):.1f}")
            metric_c3.metric("📈 模型信賴度 (R²)", f"{r_value**2:.2f}")

            # 4. 繪製三色散佈圖
            st.markdown("---")
            st.markdown("#### 📊 中杯升大杯「性價比」散佈圖")
            st.caption("位在趨勢線(紅線)上方紅點代表升級大杯偏貴；位在趨勢線下方綠點代表買大杯相對划算！")
            
            fig_reg = px.scatter(
                reg_df, x='價格(M)', y='價格(L)', color='AI升杯判定',
                hover_data={
                    '店家': True, '飲料品項': True, 
                    '價格(M)': ':.0f', '價格(L)': ':.0f', 
                    'AI預測大杯價': ':.1f', '升杯落差': ':.1f'
                },
                color_discrete_map={
                    "⚠️ 升杯溢價 (偏貴)": "#EF4444", 
                    "✅ 合理升杯 (符行情)": "#94A3B8", 
                    "🔥 超值升杯 (划算)": "#10B981"
                },
                trendline="ols", trendline_scope="overall", opacity=0.8, size_max=12
            )
            # 將趨勢線改為明顯的紅色虛線
            fig_reg.update_traces(
                marker=dict(size=9, line=dict(width=1, color='white')),
                line=dict(color='red', dash='dash') if 'line' in str(fig_reg.data) else None
            )
            
            fig_reg.update_layout(xaxis_title="中杯實際價格 (自變數 X)", yaxis_title="大杯實際價格 (應變數 Y)", hovermode="closest")
            fig_reg = apply_common_layout(fig_reg)
            st.plotly_chart(fig_reg, use_container_width=True)
            
            # 5. 繪製數據表格
            st.markdown("---")
            st.markdown("#### 📋 AI 升杯性價比明細表")
            st.caption("下方表格預設以「升杯落差」遞減排序。正數(+)代表該飲料升級大杯被收取了較高溢價，負數(-)代表升級大杯物超所值。")
            
            # 整理並美化表格欄位
            table_display = reg_df[['店家', '飲料品項', '標籤1', '價格(M)', '價格(L)', 'AI預測大杯價', '升杯落差', 'AI升杯判定']].copy()
            table_display['AI預測大杯價'] = table_display['AI預測大杯價'].round(1).astype(str) + " 元"
            table_display['升杯落差'] = table_display['升杯落差'].round(1).apply(lambda x: f"{x:+.1f} 元")
            
            table_display = table_display.sort_values(by='升杯落差', ascending=False).reset_index(drop=True)
            table_display.index += 1
            
            st.dataframe(table_display, use_container_width=True, height=400)
            
        else:
            st.warning("⚠️ 數據不足，無法啟動 AI 預測引擎。")

    # ------------------------------------------
    # 頁籤 7：預期心理分析
    # ------------------------------------------
    with tab7:
        st.markdown("### 🧠 消費者預期心理預測分析")
        
        if not filtered_df.empty:
            psych_df = pd.merge(filtered_df, market_expectation, on=['標籤1', '加料狀態'], how='left').dropna(subset=['價格(L)', '市場預期價'])
            psych_df['價格落差'] = psych_df['價格(L)'] - psych_df['市場預期價']
            
            def categorize_psych(gap):
                if gap >= 5: return "💸 品牌溢價 (超出預期)"
                elif gap <= -5: return "🤑 體感超值 (低於預期)"
                else: return "😐 符合預期 (市場行情)"
                
            psych_df['消費者體感'] = psych_df['價格落差'].apply(categorize_psych)
            
            total_items = len(psych_df)
            premium_pct = (psych_df['消費者體感'] == "💸 品牌溢價 (超出預期)").sum() / total_items * 100 if total_items > 0 else 0
            value_pct = (psych_df['消費者體感'] == "🤑 體感超值 (低於預期)").sum() / total_items * 100 if total_items > 0 else 0
            normal_pct = 100 - premium_pct - value_pct
            
            p_c1, p_c2, p_c3 = st.columns(3)
            p_c1.metric("💸 考驗信仰 (品牌溢價佔比)", f"{premium_pct:.1f}%", delta_color="inverse")
            p_c2.metric("😐 舒適區 (符合預期佔比)", f"{normal_pct:.1f}%", delta_color="off")
            p_c3.metric("🤑 容易爆單 (體感超值佔比)", f"{value_pct:.1f}%", delta_color="normal")
            
            st.markdown("---")
            st.markdown("#### 📋 品牌預期心理統整表")
            
            psych_summary = psych_df.groupby('店家').agg(
                溢價品項數=('消費者體感', lambda x: (x == "💸 品牌溢價 (超出預期)").sum()),
                符合預期數=('消費者體感', lambda x: (x == "😐 符合預期 (市場行情)").sum()),
                超值品項數=('消費者體感', lambda x: (x == "🤑 體感超值 (低於預期)").sum()),
                平均價格落差=('價格落差', lambda x: f"{x.mean():+.1f} 元")
            ).reset_index()
            psych_summary['總品項數'] = psych_summary['溢價品項數'] + psych_summary['符合預期數'] + psych_summary['超值品項數']
            psych_summary = psych_summary.sort_values(by=['溢價品項數', '總品項數'], ascending=[False, False]).reset_index(drop=True)
            psych_summary.index += 1
            st.dataframe(psych_summary[['店家', '總品項數', '溢價品項數', '符合預期數', '超值品項數', '平均價格落差']], use_container_width=True)
            
            st.markdown("---")
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                psych_count = psych_df.groupby(['店家', '消費者體感']).size().reset_index(name='數量')
                fig_psych_bar = px.bar(psych_count, y="店家", x="數量", color="消費者體感", orientation='h', barmode="relative", text_auto=True,
                                   color_discrete_map={"💸 品牌溢價 (超出預期)": "#EF4444", "😐 符合預期 (市場行情)": "#94A3B8", "🤑 體感超值 (低於預期)": "#10B981"})
                fig_psych_bar.update_layout(xaxis_title="品項數量", yaxis_title="", yaxis={'categoryorder':'total ascending'})
                fig_psych_bar = apply_common_layout(fig_psych_bar)
                st.plotly_chart(fig_psych_bar, use_container_width=True)

            with chart_col2:
                fig_psych_scatter = px.scatter(psych_df, x="市場預期價", y="價格(L)", color="消費者體感",
                                         hover_data={'店家': True, '飲料品項': True, '標籤1': True, '價格落差': ':.1f'},
                                         color_discrete_map={"💸 品牌溢價 (超出預期)": "#EF4444", "😐 符合預期 (市場行情)": "#94A3B8", "🤑 體感超值 (低於預期)": "#10B981"}, opacity=0.8, size_max=10)
                fig_psych_scatter.update_traces(marker=dict(size=8, line=dict(width=1, color='white')))
                min_val = min(psych_df["市場預期價"].min(), psych_df["價格(L)"].min()) if not psych_df.empty else 0
                max_val = max(psych_df["市場預期價"].max(), psych_df["價格(L)"].max()) if not psych_df.empty else 100
                fig_psych_scatter.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="rgba(0,0,0,0.3)", dash="dash"))
                fig_psych_scatter.update_layout(xaxis_title="市場公定行情價 (元)", yaxis_title="實際大杯售價 (元)")
                fig_psych_scatter = apply_common_layout(fig_psych_scatter)
                st.plotly_chart(fig_psych_scatter, use_container_width=True)

    # ------------------------------------------
    # 頁籤 8：原始資料
    # ------------------------------------------
    with tab8:
        st.markdown("### 📋 篩選結果明細與匯出")
        st.dataframe(filtered_df, use_container_width=True, height=500)
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 匯出當前視角資料 (CSV)", data=csv, file_name='beverages_omniscient.csv', mime='text/csv')

else:
    st.info("📂 請確認資料夾內包含 `飲料清單.xlsx` 且具備正確的工作表 `飲料_全品項(整理)`。")