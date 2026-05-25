import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import numpy as np

# ==========================================
# 1. 網頁基本與高階外觀設定 (究極琉璃 UI)
# ==========================================
st.set_page_config(page_title="手搖飲全知戰情室 (究極版)", page_icon="🧋", layout="wide")

st.markdown("""
    <style>
    /* 究極版專屬：毛玻璃 (Glassmorphism) 與高級漸層背景 */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(240, 246, 255) 0%, rgb(245, 247, 250) 90%);
    }
    h1, h2, h3, h4 {color: #1E293B; font-weight: 900; letter-spacing: -0.5px;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px; border-bottom: none; padding-bottom: 5px;}
    .stTabs [data-baseweb="tab"] {
        height: 45px; white-space: pre-wrap; background-color: rgba(255,255,255,0.6); 
        border-radius: 12px; padding: 0 18px; font-size: 15px; font-weight: 700; color: #64748B; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255,255,255,0.8);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); margin-right: 5px; backdrop-filter: blur(10px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: white !important; border: none; box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.9); padding: 20px; border-radius: 16px; 
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), inset 0 0 0 1px rgba(255,255,255,1); 
        transition: transform 0.3s, box-shadow 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
    .ai-insight-box {
        background: linear-gradient(145deg, #1E293B, #0F172A); color: #F8FAFC;
        padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border-left: 5px solid #38BDF8; margin-bottom: 20px;
    }
    .ai-insight-box h4 {color: #38BDF8; margin-top: 0;}
    </style>
""", unsafe_allow_html=True)

st.title("🧋 台灣手搖飲商業分析戰情室 (Ultimate 究極版)")
st.markdown("融合 3D 視覺化、AI 決策大腦、定價沙盤推演與消費者行為學的 **神級商業決策系統**。")

# ==========================================
# 2. 讀取與預處理資料
# ==========================================
@st.cache_data(show_spinner=False)
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
        st.error(f"❌ 讀取 Excel 失敗，請確認檔案是否存在且工作表名稱正確。錯誤訊息: {e}")
        return pd.DataFrame()

with st.spinner("🚀 系統啟動中... 正在載入全台手搖飲大數據..."):
    df = load_data()

if not df.empty:
    st.toast('戰情室啟動成功！資料已同步。', icon='✅')
    all_stores = df['店家'].dropna().unique().tolist()
    market_expectation = df.groupby(['標籤1', '加料狀態'])['價格(L)'].mean().reset_index()
    market_expectation.rename(columns={'價格(L)': '市場預期價'}, inplace=True)
    
    # ==========================================
    # 3. 側邊欄：全域過濾器
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3081/3081162.png", width=90)
        st.header("🎛️ 究極控制台")
        st.caption("連動全站 8 大模組與 AI 大腦")
        
        selected_stores = st.multiselect("🏪 選擇分析品牌", options=all_stores, default=all_stores[:7] if len(all_stores)>=7 else all_stores)
        all_bases = df['標籤1'].dropna().unique().tolist()
        selected_base = st.multiselect("🍃 選擇基底茶", options=all_bases, placeholder="預設為全茶種")
        topping_option = st.radio("🍬 加料狀態", ["全部", "有加料", "純茶/無加料"])
        
        st.divider()
        st.markdown(f"**📊 總體資料庫**\n- 總店家數: {len(all_stores)}\n- 總品項數: {len(df)}")
        st.caption("*(Powered by Streamlit Ultimate)*")

    filtered_df = df.copy()
    if selected_stores: filtered_df = filtered_df[filtered_df['店家'].isin(selected_stores)]
    if selected_base: filtered_df = filtered_df[filtered_df['標籤1'].isin(selected_base)]
    if topping_option != "全部": filtered_df = filtered_df[filtered_df['加料狀態'] == topping_option]

    def apply_common_layout(fig):
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=20, l=10, r=10),
            hoverlabel=dict(bgcolor="rgba(255,255,255,0.9)", font_size=14, font_family="Arial", bordercolor="#CBD5E1"),
            font=dict(color="#1E293B")
        )
        fig.update_xaxes(showgrid=False, linecolor='#E2E8F0')
        fig.update_yaxes(showgrid=True, gridcolor='#F1F5F9', linecolor='#E2E8F0')
        return fig

    if filtered_df.empty:
        st.warning("⚠️ 目前的篩選條件沒有相符的資料，請放寬側邊欄的篩選條件！")
        st.stop()

    # ==========================================
    # 建立 8 大究極功能頁籤
    # ==========================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 戰情總覽與洞察", "🌌 3D星系版圖", "⚔️ 品牌死鬥 PK", "📈 定價與加料", 
        "🔄 樞紐熱力圖", "🤖 AI預測模擬", "🧠 CP值分析", "📋 原始數據"
    ])

    # ------------------------------------------
    # 頁籤 1：營運總覽與 AI 洞察
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
        
        # AI 決策大腦動態生成洞察報告
        brand_stats = filtered_df.groupby('店家').agg(
            均價=('價格(L)', 'mean'), 品項數=('飲料品項', 'count'), 加料數=('加料', 'sum')
        ).reset_index()
        brand_stats['加料佔比'] = brand_stats['加料數'] / brand_stats['品項數']
        
        most_expensive = brand_stats.loc[brand_stats['均價'].idxmax()]
        cheapest = brand_stats.loc[brand_stats['均價'].idxmin()]
        most_items = brand_stats.loc[brand_stats['品項數'].idxmax()]
        most_toppings = brand_stats.loc[brand_stats['加料佔比'].idxmax()]
        
        insight_text = f"""
        <div class="ai-insight-box">
            <h4>🧠 AI 戰略分析大腦 (CEO Insight)</h4>
            <ul>
                <li><strong>定價天花板：</strong>目前選取範圍內，定價最高昂的品牌是 <b>{most_expensive['店家']}</b> (均價 ${most_expensive['均價']:.1f})，主打高客單價策略。</li>
                <li><strong>平價破壞者：</strong>定價最親民的品牌是 <b>{cheapest['店家']}</b> (均價 ${cheapest['均價']:.1f})，適合以量取勝的量販戰術。</li>
                <li><strong>菜單海王：</strong><b>{most_items['店家']}</b> 擁有高達 {most_items['品項數']} 個品項，產品線豐富，但需注意庫存管理成本。</li>
                <li><strong>咀嚼系霸主：</strong><b>{most_toppings['店家']}</b> 的加料品項佔比高達 {most_toppings['加料佔比']*100:.0f}%，是靠高毛利配料推升營收的典範。</li>
            </ul>
        </div>
        """
        st.markdown(insight_text, unsafe_allow_html=True)
            
        st.divider()
        
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
    # 頁籤 2：3D星系與市場版圖
    # ------------------------------------------
    with tab2:
        st.markdown("### 🌌 市場 3D 星系與結構解剖")
        st.markdown("#### 🔭 品牌 3D 競爭星系圖 (3D Market Galaxy)")
        st.caption("💡 滑鼠可自由旋轉縮放！透過 X(價格)、Y(品項數)、Z(加料佔比) 尋找市場真空藍海區塊。")
        
        quad_df = filtered_df.dropna(subset=['價格(L)']).groupby('店家').agg(
            品項數=('飲料品項', 'count'), 均價=('價格(L)', 'mean'), 加料數=('加料', 'sum')
        ).reset_index()
        
        if not quad_df.empty:
            quad_df['加料佔比(%)'] = (quad_df['加料數'] / quad_df['品項數'] * 100).round(1)
            fig_3d = px.scatter_3d(quad_df, x='均價', y='品項數', z='加料佔比(%)',
                                   color='店家', size='品項數', text='店家',
                                   color_discrete_sequence=px.colors.qualitative.Bold,
                                   hover_data={'店家': False, '均價': ':.1f', '品項數': True, '加料佔比(%)': True})
            fig_3d.update_traces(textposition='top center', marker=dict(line=dict(color='white', width=1), opacity=0.9))
            fig_3d.update_layout(scene=dict(
                xaxis_title='大杯均價 (X)', yaxis_title='品項豐富度 (Y)', zaxis_title='加料佔比% (Z)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=0.5))
            ), height=600, margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
            st.plotly_chart(fig_3d, use_container_width=True)

        st.divider()
        
        # 建立折疊面板收納次要圖表
        with st.expander("📂 展開查看：品牌戰略板塊矩陣與菜單宇宙", expanded=False):
            st.markdown("#### 🧱 品牌戰略定價板塊矩陣 (Treemap Matrix)")
            if not quad_df.empty:
                fig_tree = px.treemap(quad_df, path=[px.Constant("全市場版圖"), '店家'], values='品項數', color='均價', color_continuous_scale='RdYlBu_r', hover_data={'均價': ':.1f'})
                fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>品項數: %{value} 項<br>大杯均價: $ %{color:.1f}<extra></extra>', textinfo="label+value", textfont=dict(size=16, family="Arial Black"), root_color="lightgrey")
                fig_tree.update_layout(margin=dict(t=30, l=10, r=10, b=20), height=450)
                st.plotly_chart(fig_tree, use_container_width=True)
            
            st.divider()
            
            st.markdown("#### 🌞 專屬品牌菜單宇宙 (Sunburst Chart)")
            valid_sunburst_stores = filtered_df['店家'].unique().tolist()
            if valid_sunburst_stores:
                selected_sun_store = st.selectbox("🔍 選擇要放大解剖的品牌菜單", options=valid_sunburst_stores, index=0)
                sun_df = filtered_df[filtered_df['店家'] == selected_sun_store].dropna(subset=['價格(L)']).copy().fillna("無分類")
                fig_sun = px.sunburst(sun_df, path=['店家', '標籤1', '加料狀態', '飲料品項'], values='價格(L)', color='價格(L)', color_continuous_scale='RdYlBu_r')
                fig_sun.update_layout(margin=dict(t=20, l=10, r=10, b=20), height=600)
                fig_sun.update_traces(marker=dict(line=dict(color='#FFFFFF', width=1)), hovertemplate='<b>%{label}</b><br>大杯售價: $ %{color:.0f}<extra></extra>')
                st.plotly_chart(fig_sun, use_container_width=True)

    # ------------------------------------------
    # 頁籤 3：品牌雷達 PK
    # ------------------------------------------
    with tab3:
        st.markdown("### ⚔️ 品牌 DNA 死鬥對決")
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
                    if b_df.empty: return [0,0,0,0], [0,0,0,0]
                    s1 = (b_df['價格(L)'].mean() / max_price) * 100
                    s2 = (len(b_df) / max_items) * 100
                    s3 = (b_df['加料'] == 1.0).sum() / len(b_df) * 100 if len(b_df)>0 else 0
                    s4 = (b_df['標籤1'].nunique() / max_bases) * 100
                    v1 = f"${b_df['價格(L)'].mean():.1f}"
                    v2 = f"{len(b_df)} 項"
                    v3 = f"{(b_df['加料'] == 1.0).sum() / len(b_df) * 100:.1f}%"
                    v4 = f"{b_df['標籤1'].nunique()} 種"
                    return [s1, s2, s3, s4], [v1, v2, v3, v4]

                scores_a, vals_a = get_brand_metrics(brand_a)
                scores_b, vals_b = get_brand_metrics(brand_b)
                categories = ['價格水準 (高單價)', '品項豐富度', '加料專注度', '茶種多樣性']

                radar_c1, radar_c2 = st.columns([1.2, 1])
                with radar_c1:
                    st.markdown("#### 🕸️ 商業模式雷達圖")
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(r=scores_a, theta=categories, fill='toself', name=brand_a, line_color='#EF4444'))
                    fig_radar.add_trace(go.Scatterpolar(r=scores_b, theta=categories, fill='toself', name=brand_b, line_color='#3B82F6'))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, margin=dict(t=40, b=40, l=40, r=40))
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    with st.expander("📋 展開直接對比數據"):
                        pk_table = pd.DataFrame({
                            "評估維度": ["大杯平均單價", "總品項數量", "加料品項佔比", "涵蓋基底茶種類"],
                            f"🟥 {brand_a}": vals_a,
                            f"🟦 {brand_b}": vals_b
                        })
                        st.dataframe(pk_table, use_container_width=True, hide_index=True)

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
        
        with st.expander("📊 品牌均價與升杯策略統整表", expanded=True):
            summary_table = filtered_df.groupby('店家').agg(
                平均中杯價=('價格(M)', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                平均大杯價=('價格(L)', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                平均升杯價差=('升杯價差', lambda x: f"${x.mean().round(1)}" if pd.notna(x.mean()) else "-"),
                最常見升杯價差=('升杯價差', lambda x: f"{int(x.mode().iloc[0])} 元" if not x.mode().empty else "-"),
                有效品項數=('飲料品項', 'count')
            ).reset_index().sort_values(by='有效品項數', ascending=False).reset_index(drop=True)
            summary_table.index += 1
            st.dataframe(summary_table, use_container_width=True)
            
        st.divider()
        box_col, top_col = st.columns(2)
        
        with box_col:
            st.markdown("#### 📦 價格區間與極端值 (盒鬚圖)")
            fig_box = px.box(filtered_df, x='店家', y='價格(L)', color='店家', points="all", hover_data={'店家': False, '飲料品項': True, '加料狀態': True, '價格(L)': ':.0f'})
            fig_box.update_layout(xaxis={'categoryorder':'median descending'}, showlegend=False, yaxis_title="大杯價格 (元)", xaxis_title="")
            fig_box = apply_common_layout(fig_box)
            st.plotly_chart(fig_box, use_container_width=True)
            
        with top_col:
            st.markdown("#### 🍬 加料經濟學：加料平均溢價")
            top_pivot = filtered_df.pivot_table(index='店家', columns='加料狀態', values='價格(L)', aggfunc='mean').reset_index()
            if '有加料' in top_pivot.columns and '純茶/無加料' in top_pivot.columns:
                top_pivot['加料溢價'] = top_pivot['有加料'] - top_pivot['純茶/無加料']
                top_pivot = top_pivot.dropna(subset=['加料溢價']).sort_values(by='加料溢價', ascending=False)
                fig_top = px.bar(top_pivot, x='店家', y='加料溢價', text_auto='+.1f', color='加料溢價', color_continuous_scale='Purples')
                fig_top.update_layout(yaxis_title="平均加料溢價 (元)", xaxis_title="")
                fig_top = apply_common_layout(fig_top)
                st.plotly_chart(fig_top, use_container_width=True)
            else:
                st.info("💡 目前篩選的資料維度不足以計算加料溢價（需同時包含有加料與無加料的品項）。")

    # ------------------------------------------
    # 頁籤 5：動態樞紐分析
    # ------------------------------------------
    with tab5:
        st.markdown("### 🔄 自由維度樞紐與熱力分析")
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
            
            with st.expander("📋 展開查看樞紐分析明細表"):
                display_df = pivot_df.reset_index()
                if value_axis == '計算品項數量 (Count)': display_df = display_df.fillna(0).astype(int, errors='ignore')
                else: display_df = display_df.fillna("-")
                st.dataframe(display_df, use_container_width=True)
        else:
            st.error("⚠️ X 軸與 Y 軸不能選擇相同的維度，請重新選擇。")

    # ------------------------------------------
    # 頁籤 6：AI 預測引擎 & 定價模擬
    # ------------------------------------------
    with tab6:
        st.markdown("### 🤖 AI 價格預測與新品牌定價模擬器")
        
        reg_df = filtered_df.dropna(subset=['價格(M)', '價格(L)']).copy()
        reg_df = reg_df[(reg_df['價格(M)'] > 0) & (reg_df['價格(L)'] > 0)]
        
        if len(reg_df) > 5:
            slope, intercept, r_value, p_value, std_err = stats.linregress(reg_df['價格(M)'], reg_df['價格(L)'])
            
            st.markdown("#### 🎛️ 新品牌定價模擬器 (AI 沙盤推演)")
            st.info("💡 想像您準備開一家新的手搖飲店。請拉動下方的「中杯售價」，AI 模型將依據目前全市場的大數據，建議您大杯應該賣多少錢才符合市場公定預期。")
            
            sim_col1, sim_col2, sim_col3 = st.columns([1.5, 1, 1])
            with sim_col1:
                user_m_price = st.slider("👇 設定您的中杯預計售價 (元)", min_value=20, max_value=120, value=40, step=5)
            
            predicted_l_price = user_m_price * slope + intercept
            
            with sim_col2:
                st.metric("🤖 AI 建議大杯定價", f"${predicted_l_price:.0f} 元", delta="符合市場行情", delta_color="off")
            with sim_col3:
                st.metric("📈 預期升杯價差", f"${(predicted_l_price - user_m_price):.0f} 元")

            st.divider()
            
            st.markdown("#### 📊 中杯升大杯「性價比」散佈圖")
            reg_df['AI預測大杯價'] = reg_df['價格(M)'] * slope + intercept
            reg_df['升杯落差'] = reg_df['價格(L)'] - reg_df['AI預測大杯價']
            
            def categorize_upgrade(gap):
                if gap > 3: return "⚠️ 升杯溢價 (偏貴)"
                elif gap < -3: return "🔥 超值升杯 (划算)"
                else: return "✅ 合理升杯 (符行情)"
            reg_df['AI升杯判定'] = reg_df['升杯落差'].apply(categorize_upgrade)
            
            metric_c1, metric_c2, metric_c3 = st.columns(3)
            metric_c1.metric("📐 市場升級斜率", f"{slope:.2f}")
            sign = "+" if intercept >= 0 else "-"
            metric_c2.metric("🎯 預測公定價公式", f"大杯 = 中杯 × {slope:.2f} {sign} {abs(intercept):.1f}")
            metric_c3.metric("📈 模型信賴度 (R²)", f"{r_value**2:.2f}")

            fig_reg = px.scatter(
                reg_df, x='價格(M)', y='價格(L)', color='AI升杯判定',
                hover_data={'店家': True, '飲料品項': True, '價格(M)': ':.0f', '價格(L)': ':.0f', '升杯落差': ':.1f'},
                color_discrete_map={"⚠️ 升杯溢價 (偏貴)": "#EF4444", "✅ 合理升杯 (符行情)": "#94A3B8", "🔥 超值升杯 (划算)": "#10B981"},
                trendline="ols", trendline_scope="overall", opacity=0.8, size_max=12
            )
            fig_reg.update_traces(marker=dict(size=9, line=dict(width=1, color='white')), line=dict(color='red', dash='dash') if 'line' in str(fig_reg.data) else None)
            fig_reg.update_layout(xaxis_title="中杯實際價格 (自變數 X)", yaxis_title="大杯實際價格 (應變數 Y)", hovermode="closest")
            fig_reg = apply_common_layout(fig_reg)
            st.plotly_chart(fig_reg, use_container_width=True)
            
            with st.expander("📋 展開查看 AI 升杯性價比明細表"):
                table_display = reg_df[['店家', '飲料品項', '標籤1', '價格(M)', '價格(L)', 'AI預測大杯價', '升杯落差', 'AI升杯判定']].copy()
                table_display['AI預測大杯價'] = table_display['AI預測大杯價'].round(1).astype(str) + " 元"
                table_display['升杯落差'] = table_display['升杯落差'].round(1).apply(lambda x: f"{x:+.1f} 元")
                table_display = table_display.sort_values(by='升杯落差', ascending=False).reset_index(drop=True)
                table_display.index += 1
                st.dataframe(table_display, use_container_width=True, height=350)
        else:
            st.warning("⚠️ 此篩選條件下的中/大杯雙重數據不足，無法啟動 AI 預測引擎。")

    # ------------------------------------------
    # 頁籤 7：預期心理分析
    # ------------------------------------------
    with tab7:
        st.markdown("### 🧠 消費者預期心理預測分析 (CP值指數)")
        
        psych_df = pd.merge(filtered_df, market_expectation, on=['標籤1', '加料狀態'], how='left').dropna(subset=['價格(L)', '市場預期價'])
        if not psych_df.empty:
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
            
            st.divider()
            
            with st.expander("📋 品牌預期心理與綜合 CP 值總表", expanded=True):
                st.caption("ℹ️ **CP 值指數** 計算方式：基礎分數 50 分，平均價格每低於市場行情 1 元加 2 分。分數越高代表在該維度下越超值。")
                psych_summary = psych_df.groupby('店家').agg(
                    溢價品項數=('消費者體感', lambda x: (x == "💸 品牌溢價 (超出預期)").sum()),
                    符合預期數=('消費者體感', lambda x: (x == "😐 符合預期 (市場行情)").sum()),
                    超值品項數=('消費者體感', lambda x: (x == "🤑 體感超值 (低於預期)").sum()),
                    落差數值=('價格落差', 'mean')
                ).reset_index()
                
                psych_summary['總品項數'] = psych_summary['溢價品項數'] + psych_summary['符合預期數'] + psych_summary['超值品項數']
                psych_summary['綜合 CP 值指數'] = (50 - (psych_summary['落差數值'] * 2)).clip(0, 100).round(1)
                psych_summary['平均價格落差'] = psych_summary['落差數值'].apply(lambda x: f"{x:+.1f} 元")
                psych_summary = psych_summary.sort_values(by='綜合 CP 值指數', ascending=False).reset_index(drop=True)
                psych_summary.index += 1
                st.dataframe(psych_summary[['店家', '總品項數', '溢價品項數', '符合預期數', '超值品項數', '平均價格落差', '綜合 CP 值指數']], use_container_width=True)
            
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
        else:
             st.warning("⚠️ 數據無法進行心理預期計算，請調整篩選條件。")

    # ------------------------------------------
    # 頁籤 8：原始資料
    # ------------------------------------------
    with tab8:
        st.markdown("### 📋 篩選結果明細與匯出")
        st.dataframe(filtered_df, use_container_width=True, height=500)
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 匯出當前視角資料 (CSV)", data=csv, file_name='beverages_ultimate.csv', mime='text/csv')

else:
    # 全域資料抓取失敗或為空時
    st.stop()
