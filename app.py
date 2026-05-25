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
        st.caption("連動全站 11 大模組與 AI 大腦")
        
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
    # 4. 建立 11 大究極功能頁籤
    # ==========================================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📊 戰情總覽與洞察", "🌌 3D星系版圖", "⚔️ 品牌死鬥 PK", "📈 定價與加料", 
        "🔄 樞紐熱力圖", "🤖 AI預測模擬", "🧠 CP值分析", "📋 原始數據", "📝 AI全能報告",
        "🧪 藍海新品研發", "💰 財務損益推演"
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
            fig2.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05 if i==0 else 0 for i in range(len(filtered_df['標籤1'].unique()))])
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
                max_price = df['價格(L)'].mean() if pd.notna(df['價格(L)'].mean()) else 100
                max_items = df.groupby('店家').size().max()
                max_bases = df.groupby('店家')['標籤1'].nunique().max()
                
                def get_brand_metrics(brand_name):
                    b_df = df[df['店家'] == brand_name]
                    if b_df.empty: return [0,0,0,0], [0,0,0,0]
                    s1 = (b_df['價格(L)'].mean() / max_price) * 100 if pd.notna(b_df['價格(L)'].mean()) else 0
                    s2 = (len(b_df) / max_items) * 100
                    s3 = (b_df['加料'] == 1.0).sum() / len(b_df) * 100 if len(b_df)>0 else 0
                    s4 = (b_df['標籤1'].nunique() / max_bases) * 100
                    v1 = f"${b_df['價格(L)'].mean():.1f}" if pd.notna(b_df['價格(L)'].mean()) else "N/A"
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
            metric_c2.metric("🎯 預測公定價公式", f"$$大杯 = 中杯 \\times {slope:.2f} {sign} {abs(intercept):.1f}$$")
            metric_c3.metric("📈 模型信賴度 ($R^2$)", f"{r_value**2:.2f}")

            fig_reg = px.scatter(
                reg_df, x='價格(M)', y='價格(L)', color='AI升杯判定',
                hover_data={'店家': True, '飲料品項': True, '價格(M)': ':.0f', '價格(L)': ':.0f', '升杯落差': ':.1f'},
                color_discrete_map={"⚠️ 升杯溢價 (偏貴)": "#EF4444", "✅ 合理升杯 (符行情)": "#94A3B8", "🔥 超值升杯 (划算)": "#10B981"},
                trendline="ols", trendline_scope="overall", opacity=0.8, size_max=12
            )
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
    # 頁籤 7：預期心理分析 (究極動態矩陣權重版)
    # ------------------------------------------
    with tab7:
        st.markdown("### 🧠 究極矩陣式預期心理分析 (Matrix-Weighted CP Index)")
        st.caption("導入 MCDA 演算法，依據品項的「物料成本」、「工藝複雜度」與「品牌招牌光環」進行動態權重校正。")
        
        diagnostic_df = filtered_df.copy()
        if '加料狀態' in diagnostic_df.columns:
            diagnostic_df['加料狀態'] = diagnostic_df['加料狀態'].fillna('純茶/無加料')
        else:
            diagnostic_df['加料狀態'] = '純茶/無加料'
            
        diagnostic_df = diagnostic_df.dropna(subset=['價格(L)'])
        
        psych_df = pd.merge(
            diagnostic_df, 
            market_expectation, 
            on=['標籤1', '加料狀態'], 
            how='left'
        )
        
        global_l_mean = df['價格(L)'].mean() if not df.empty else 50
        psych_df['市場預期價'] = psych_df['市場預期價'].fillna(global_l_mean)

        with st.expander("🔍 數據庫健康狀態診斷報告 (排錯專用)", expanded=False):
            st.markdown("##### 🩺 資料流失節點追蹤：")
            st.write(f"1. 經側邊欄篩選後，有效大杯商品數：`{len(diagnostic_df)}` 項")
            st.write(f"2. 成功與市場大盤行情配對商品數：`{len(psych_df)}` 項")
            
            nan_market_count = psych_df['市場預期價'].isna().sum()
            if nan_market_count > 0:
                st.error(f"⚠️ 警告：有 {nan_market_count} 個品項的『標籤1』在全大盤中找不到對應的平均價！")
            else:
                st.success("✅ 欄位配對檢查：所有品項皆已成功取得市場基準價。")
                
            st.markdown("##### 📋 當前傳入模型的前 3 筆檢視數據：")
            st.dataframe(psych_df[['店家', '飲料品項', '標籤1', '加料狀態', '價格(L)', '市場預期價']].head(3), use_container_width=True)

        if not psych_df.empty and len(psych_df) > 0:
            def calculate_matrix_weighted_cp(row):
                item_name = str(row['飲料品項'])
                base_expectation = row['市場預期價']
                W_m, W_b, W_c = 0.0, 0.0, 0.0
                
                if any(k in item_name for k in ['鮮奶', '拿鐵', '歐蕾', '芝士', '奶蓋', '厚乳', '重乳']):
                    W_m = 0.18
                elif any(k in item_name for k in ['鮮果', '葡萄', '草莓', '芒果', '蘋果', '檸檬', '百香', '雷夢']):
                    W_m = 0.15
                    
                if any(k in item_name for k in ['冰沙', '特調', '現打', '雙Q', '三兄弟', '多肉', '白玉']):
                    W_c = 0.08
                    
                if any(k in item_name for k in ['招牌', '經典', '得獎', '極品', '首創', '特選', '莊園', '丘森']):
                    W_b = 0.05
                    
                total_factor = 1.0 + W_m + W_b + W_c
                return base_expectation * total_factor

            psych_df['調整後預期價'] = psych_df.apply(calculate_matrix_weighted_cp, axis=1)
            psych_df['真實價格落差'] = psych_df['價格(L)'] - psych_df['調整後預期價']
            
            std_gap = psych_df['真實價格落差'].std()
            threshold = max(std_gap * 0.8, 3.5) if pd.notna(std_gap) else 4.0 
            
            def categorize_psych_matrix(gap):
                if gap >= threshold: return "💸 品牌溢價 (主打高質感)"
                elif gap <= -threshold: return "🤑 體感超值 (利潤回饋)"
                else: return "😐 符合預期 (市場行情)"
                
            psych_df['消費者體感'] = psych_df['真實價格落差'].apply(categorize_psych_matrix)
            
            total_items_p = len(psych_df)
            premium_pct = (psych_df['消費者體感'] == "💸 品牌溢價 (主打高質感)").sum() / total_items_p * 100
            value_pct = (psych_df['消費者體感'] == "🤑 體感超值 (利潤回饋)").sum() / total_items_p * 100
            normal_pct = 100 - premium_pct - value_pct
            
            p_c1, p_c2, p_c3 = st.columns(3)
            p_c1.metric("💸 高質感定位品項佔比", f"{premium_pct:.1f}%", delta="考驗品牌信仰", delta_color="inverse")
            p_c2.metric("😐 營收護城河 (行情品項)", f"{normal_pct:.1f}%", delta="流速主力")
            p_c3.metric("🤑 破局爆單 (超值品項)", f"{value_pct:.1f}%", delta="帶路雞商品", delta_color="normal")
            
            st.divider()
            
            st.markdown("#### 📋 品牌動態加權 CP 值轉換總表")
            psych_summary = psych_df.groupby('店家').agg(
                高質感品項數=('消費者體感', lambda x: (x == "💸 品牌溢價 (主打高質感)").sum()),
                符合預期數=('消費者體感', lambda x: (x == "😐 符合預期 (市場行情)").sum()),
                超值品項數=('消費者體感', lambda x: (x == "🤑 體感超值 (利潤回饋)").sum()),
                平均真實落差=('真實價格落差', 'mean')
            ).reset_index()
            
            psych_summary['總品項數'] = psych_summary['高質感品項數'] + psych_summary['符合預期數'] + psych_summary['超值品項數']
            psych_summary['綜合 CP 值指數'] = (60 - (psych_summary['平均真實落差'] * 3.5)).clip(0, 100).round(1)
            psych_summary['校正後平均落差'] = psych_summary['平均真實落差'].apply(lambda x: f"{x:+.1f} 元")
            
            psych_summary = psych_summary.sort_values(by='綜合 CP 值指數', ascending=False).reset_index(drop=True)
            psych_summary.index += 1
            st.dataframe(psych_summary[['店家', '總品項數', '高質感品項數', '符合預期數', '超值品項數', '校正後平均落差', '綜合 CP 值指數']], use_container_width=True)
            
            st.divider()
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("#### 📊 品牌消費者體感結構分佈")
                psych_count = psych_df.groupby(['店家', '消費者體感']).size().reset_index(name='數量')
                fig_psych_bar = px.bar(
                    psych_count, y="店家", x="數量", color="消費者體感", 
                    orientation='h', barmode="relative", text_auto=True,
                    color_discrete_map={
                        "💸 品牌溢價 (主打高質感)": "#6366F1", 
                        "😐 符合預期 (市場行情)": "#94A3B8", 
                        "🤑 體感超值 (利潤回饋)": "#10B981"
                    }
                )
                fig_psych_bar.update_layout(xaxis_title="品項數量", yaxis_title="", yaxis={'categoryorder':'total ascending'})
                fig_psych_bar = apply_common_layout(fig_psych_bar)
                st.plotly_chart(fig_psych_bar, use_container_width=True)

            with chart_col2:
                st.markdown("#### 🎯 實際售價 vs 矩陣校正行情價")
                fig_psych_scatter = px.scatter(
                    psych_df, x="調整後預期價", y="價格(L)", color="消費者體感",
                    hover_data={'店家': True, '飲料品項': True, '標籤1': True, '真實價格落差': ':.1f'},
                    color_discrete_map={
                        "💸 品牌溢價 (主打高質感)": "#6366F1", 
                        "😐 符合預期 (市場行情)": "#94A3B8", 
                        "🤑 體感超值 (利潤回饋)": "#10B981"
                    }, opacity=0.85
                )
                fig_psych_scatter.update_traces(marker=dict(size=12, line=dict(width=1.5, color='white')))
                
                min_val = min(psych_df["調整後預期價"].min(), psych_df["價格(L)"].min())
                max_val = max(psych_df["調整後預期價"].max(), psych_df["價格(L)"].max())
                fig_psych_scatter.add_shape(
                    type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, 
                    line=dict(color="rgba(15, 23, 42, 0.5)", dash="dash", width=1.5)
                )
                fig_psych_scatter.update_layout(xaxis_title="動態權重校正行情 (元)", yaxis_title="實際大杯售價 (元)")
                fig_psych_scatter = apply_common_layout(fig_psych_scatter)
                st.plotly_chart(fig_psych_scatter, use_container_width=True)
                
            with st.expander("📋 展開查看 AI 權重判定與落差明細表"):
                detail_df = psych_df[['店家', '飲料品項', '標籤1', '市場預期價', '調整後預期價', '價格(L)', '真實價格落差', '消費者體感']].copy()
                detail_df['市場預期價'] = detail_df['市場預期價'].round(1)
                detail_df['調整後預期價'] = detail_df['調整後預期價'].round(1)
                detail_df['真實價格落差'] = detail_df['真實價格落差'].round(1).apply(lambda x: f"{x:+.1f}")
                detail_df = detail_df.sort_values(by='價格(L)', ascending=False).reset_index(drop=True)
                st.dataframe(detail_df, use_container_width=True)
        else:
            st.error("🚨 嚴重錯誤：經過防呆清洗後依然無法產生資料，請檢查 Excel 中的『價格(L)』欄位是否全部為空值或非數字。")

    # ------------------------------------------
    # 頁籤 8：原始數據檢視
    # ------------------------------------------
    with tab8:
        st.markdown("### 📋 原始數據觀測站")
        st.caption("當前通過篩選器的底層明細資料。")
        st.dataframe(filtered_df, use_container_width=True)

    # ------------------------------------------
    # 頁籤 9：AI 全能商業戰略總結報告 (優化重製究極版)
    # ------------------------------------------
    with tab9:
        st.markdown("### 📝 AI 全能商業戰略總結報告 (Executive Summary)")
        st.caption("自動融合全站大數據矩陣，動態生成的頂層戰略洞察與決策建議。")
        
        if not filtered_df.empty and filtered_df['店家'].nunique() > 0:
            with st.spinner("🧠 AI 大腦正在深度運算全域矩陣..."):
                # 1. 基礎指標提取
                total_brands = filtered_df['店家'].nunique()
                total_items = len(filtered_df)
                global_avg_price = filtered_df['價格(L)'].mean()
                
                brand_summary = filtered_df.groupby('店家').agg(
                    均價=('價格(L)', 'mean'),
                    品項數=('飲料品項', 'count'),
                    加料數=('加料', 'sum')
                ).reset_index()
                
                # 2. 進階矩陣計算
                top_base = filtered_df['標籤1'].value_counts().idxmax() if '標籤1' in filtered_df.columns and not filtered_df['標籤1'].empty else "未分類"
                top_base_pct = (filtered_df['標籤1'] == top_base).sum() / total_items * 100 if total_items > 0 else 0
                topping_pct = (filtered_df['加料'] == 1.0).sum() / total_items * 100 if total_items > 0 else 0
                
                # ==========================================
                # 🔥 升級版 AI 分析引擎：雙維度戰略矩陣 (價格水位 x 產品結構)
                # ==========================================
                # 判斷維度 1：市場定價水位 (Price Level)
                if global_avg_price >= 70:
                    price_tier = "premium"
                    market_type = "💎 頂尖客單奢華型藍海"
                elif global_avg_price >= 55:
                    price_tier = "mid-high"
                    market_type = "⚖️ 白領輕奢精緻戰場"
                elif global_avg_price >= 40:
                    price_tier = "mass"
                    market_type = "🔥 主流中產高頻剛需區"
                else:
                    price_tier = "budget"
                    market_type = "🥊 價格破壞型下沉紅海"

                # 判斷維度 2：加料變現依賴度 (Topping Dependency)
                if topping_pct >= 45:
                    product_strategy = "高度甜品化，極度依賴咀嚼系配料（如白玉、奶蓋、寒天）來拉高客單價與飽足感。"
                    topping_type = "heavy"
                elif topping_pct >= 25:
                    product_strategy = "黃金配料比例，純茶與加料雙引擎並重，菜單結構均衡。"
                    topping_type = "balanced"
                else:
                    product_strategy = "極致純淨，主打茶湯底蘊與原物料本質，刻意降低吧台出杯工序。"
                    topping_type = "light"

                # 綜合生成 Strategic Focus (戰略方針)
                if price_tier == "premium":
                    if topping_type == "heavy":
                        strategic_focus = f"【奢華甜品化】{product_strategy} 建議強化配料的『稀缺性』（如法式慕斯、季節限定鮮果），透過高顏值視覺包裝創造 IG 傳播效應，此客群對價格極不敏感，賣的是犒賞感。"
                    else:
                        strategic_focus = f"【職人工藝茶】{product_strategy} 行銷應極致放大『單一產區、契作茶園、職人手沖』等故事性。捨棄花俏配料，以純粹的品茶文化建立堅不可摧的品牌信仰。"
                
                elif price_tier == "mid-high":
                    if topping_type == "heavy" or topping_type == "balanced":
                        strategic_focus = f"【微創新突圍】此區間為兵家必爭之地。{product_strategy} 建議透過研發『特色帶路雞』（如獨家口味茶凍、新創基底茶）打破定價僵局，創造競品無法輕易複製的記憶點。"
                    else:
                        strategic_focus = f"【輕負擔精緻飲】{product_strategy} 鎖定注重健康的都會白領，建議行銷主打『低卡、無糖也順口、小農契作』，拉開與大眾市場的質感差距。"
                
                elif price_tier == "mass":
                    strategic_focus = f"【規模化防禦】{product_strategy} 核心重點在於『高轉化率與出杯流速』。必須嚴控供應鏈成本，透過數位化點單、會員寄杯點數機制，死死綁定區域型消費者的日常復購習慣。"
                
                else:
                    strategic_focus = f"【極致效率戰】{product_strategy} 生存法則唯有『規模經濟與極致成本控制』。應大刀闊斧刪減低周轉品項，菜單聚焦於爆款純茶與少數暢銷配料，以連鎖量販模式搶佔市佔率。"
                    
                # 3. 頂層視覺看板渲染
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%); color: #F8FAFC; padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px;">
                    <h3 style="color: #A5B4FC; margin-top: 0; font-weight: 900; letter-spacing: 1px;">🔮 戰情官決策大腦：戰略白皮書</h3>
                    <p style="font-size: 14px; color: #CBD5E1; line-height: 1.6;">本報告由戰情室動態矩陣演算法生成。基於當前篩選的 <b>{total_brands}</b> 個品牌、<b>{total_items}</b> 款品項進行全盤解構，旨在提供 CEO 級別的頂層商業佈局思維。</p>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 20px 0;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div>
                            <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">當前市場定位分類</span>
                            <h4 style="color: #F43F5E; margin: 5px 0 0 0; font-size: 18px;">{market_type}</h4>
                        </div>
                        <div>
                            <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">核心基底茶霸主</span>
                            <h4 style="color: #34D399; margin: 5px 0 0 0; font-size: 18px;">{top_base} ({top_base_pct:.1f}%)</h4>
                        </div>
                        <div>
                            <span style="font-size: 12px; color: #94A3B8; text-transform: uppercase;">篩選大盤平均價格</span>
                            <h4 style="color: #FBBF24; margin: 5px 0 0 0; font-size: 18px;">${global_avg_price:.1f} 元</h4>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 4. 戰略三大支柱剖析
                col_strat1, col_strat2 = st.columns(2)
                with col_strat1:
                    st.markdown("#### 🎯 支柱一：定價與菜單工程 (Menu Engineering)")
                    st.markdown(f"""
                    * **定價錨點策略**：目前大盤大杯均價落在 `${global_avg_price:.1f}` 元。新研發品項切入時，若定位為流量款，定價應落於均價減 10-15 元；若定位為高毛利利基款（如鮮奶茶、鮮果茶），應大膽定價在均價加 15-20 元以鎖定獲利區間。
                    * **市場聚焦戰術**：當前市場以 `{top_base}` 為絕對核心（佔比達 `{top_base_pct:.1f}%`）。這意味著該基底茶的消費者教育成本最低，品牌切入時，應優先優化此基底茶的風味結構與品質穩定度，建立品牌基本盤。
                    """)
                    
                with col_strat2:
                    st.markdown("#### 🧋 支柱二：加料變現與毛利解密 (Topping Economics)")
                    if topping_pct > 30:
                        st.markdown(f"""
                        * **咀嚼經濟火熱**：當前篩選範圍內，加料品項佔比高達 `{topping_pct:.1f}%`，市場表現出高度的「咀嚼依賴性」。
                        * **變現建言**：加料是推升客單價與毛利淨值的核心武器。強烈建議研發「品牌獨家限定配料」（如特殊茶凍、海鹽黑糖奶蓋），並採取不開放單點、僅隨明星限定飲品出杯的策略，以拉高產品防禦門檻。
                        """)
                    else:
                        st.markdown(f"""
                        * **純茶/輕負擔主力**：加料品項佔比僅 `{topping_pct:.1f}%`，顯示該市場消費者更偏向「原茶品茗」或「清爽系健康飲品」。
                        * **變現建言**：此時盲目疊加珍珠、波霸無法帶來業績增量。策略應轉向「茶湯工藝升級」，例如標榜產地莊園茶、小農契作、低溫冷泡工藝，利用茶湯本質的溢價來取代傳統配料的堆疊。
                        """)
                        
                st.markdown("---")
                st.markdown("#### 🛠️ CEO 戰術執行行動方案 (Actionable Roadmap)")
                
                if not brand_summary.empty:
                    leader_brand = brand_summary.loc[brand_summary['均價'].idxmax()]['店家']
                    volume_brand = brand_summary.loc[brand_summary['品項數'].idxmax()]['店家']
                    
                    st.success(f"""
                    🚀 **短中期戰術佈局建議：**
                    1.  **市場定位診斷**：目前市場定位屬於 **{market_type}**，核心戰略為：*{strategic_focus}*。
                    2.  **向標竿看齊 (高價溢價)**：參考當前均價最高昂的品牌 **{leader_brand}** 的定價與視覺呈現，檢視自身的產品故事包裝，是否具備支撐高客單價的「情感溢價價值」。
                    3.  **菜單工程斷捨離 (降低內耗)**：目前品項數最多的品牌為 **{volume_brand}**。對於中小型新創品牌，品項過多將導致供應鏈臃腫與原料耗損。強烈建議實施『菜單精簡化』，將品項限縮在 30 款核心爆款內，聚焦出杯效率。
                    4.  **定價動態回測**：在每一次新品研發或配方調整前，請隨時切換至 **「🤖 AI預測模擬」** 頁籤，利用動態迴歸斜率，確保新品定價踩在「消費者預期性價比」的黃金交叉點。
                    """)
        else:
            st.warning("⚠️ 當前篩選條件下無足夠數據，AI 無法生成戰略報告。")

    # ==========================================
    # 🔥 全新擴充：頁籤 10 - 藍海新品研發實驗室 (含繪圖防呆修復)
    # ==========================================
    with tab10:
        st.markdown("### 🧪 藍海新品研發與智慧定價實驗室 (Menu R&D Lab)")
        st.caption("自動探測市場中『競爭少、利潤高』的真空藍海賽道，並提供智慧化新品定價與 AI 行銷包裝指南。")
        
        # 1. 藍海真空矩陣算法
        gap_analysis = df.groupby(['標籤1', '加料狀態']).agg(
            均價=('價格(L)', 'mean'),
            品項數=('飲料品項', 'count')
        ).reset_index()
        
        if not gap_analysis.empty:
            max_p = gap_analysis['均價'].max() if gap_analysis['均價'].max() > 0 else 1
            max_c = gap_analysis['品項數'].max() if gap_analysis['品項數'].max() > 0 else 1
            
            # 藍海指數公式：均價越高分數越高(佔60%) + 現有競品越少分數越高(佔40%)
            gap_analysis['藍海指數'] = ((gap_analysis['均價'] / max_p) * 60 + (1 - gap_analysis['品項數'] / max_c) * 40).round(1)
            
            # === 核心防呆修復：安全清洗「藍海指數」欄位，防止 Plotly 畫圖崩潰 ===
            gap_analysis['藍海指數'] = gap_analysis['藍海指數'].replace([np.inf, -np.inf], 0) # 清除無限大
            gap_analysis['藍海指數'] = gap_analysis['藍海指數'].fillna(0) # 清除空值
            gap_analysis['藍海指數'] = gap_analysis['藍海指數'].clip(lower=0) # 強制最小為 0
            
            gap_analysis = gap_analysis.sort_values(by='藍海指數', ascending=False).reset_index(drop=True)
            
            rd_c1, rd_c2 = st.columns([1, 1.2])
            with rd_c1:
                st.markdown("#### 🔭 當前全市場黃金藍海賽道 Top 3")
                for idx, row in gap_analysis.head(3).iterrows():
                    st.markdown(f"""
                    <div style="background: rgba(99, 102, 241, 0.05); padding: 15px; border-radius: 12px; border-left: 5px solid #6366F1; margin-bottom: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                        <span style="font-weight:900; color:#4F46E5; font-size:16px;">🏆 Top {idx+1}：{row['標籤1']} × {row['加料狀態']}</span><br>
                        <span style="font-size:14px; color:#475569;">綜合藍海潛力: <b>{row['藍海指數']} 分</b> | 市場均價: <b>${row['均價']:.1f} 元</b> | 現有競品僅: <b>{row['品項數']} 款</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### 📊 全品類市場供需與溢價分佈")
                fig_gap = px.scatter(gap_analysis, x='品項數', y='均價', size='藍海指數', color='標籤1', text='標籤1',
                                     hover_data={'藍海指數': True, '品項數': True, '均價': ':.1f'}, color_discrete_sequence=px.colors.qualitative.Dark24)
                fig_gap.update_traces(textposition='top center', marker=dict(opacity=0.85, line=dict(width=1, color='white')))
                fig_gap.update_layout(xaxis_title="市場競爭度 (現有商品總數)", yaxis_title="定價天花板 (大杯平均價格)")
                st.plotly_chart(apply_common_layout(fig_gap), use_container_width=True)
                
            with rd_c2:
                st.markdown("#### 💡 智慧新品研發模擬與定價大腦")
                st.info("💡 選擇您研發中的新品屬性，AI 將根據大盤實體行情，給出精準的定價建議與情感價值包裝方案。")
                
                input_base = st.selectbox("1. 選擇預計研發的基底茶種", options=all_bases, index=0)
                input_topping = st.selectbox("2. 設定該新品的配料狀態", options=["純茶/無加料", "有加料"], index=0)
                input_tier = st.select_slider("3. 決定該產品的戰略定位", options=["大眾引流款 (低毛利/衝量款)", "市場主流款 (利潤與銷量平衡)", "奢華旗艦款 (高溢價/故事包裝)"], value="市場主流款 (利潤與銷量平衡)")
                
                # 智慧定價算法
                base_match = gap_analysis[(gap_analysis['標籤1'] == input_base) & (gap_analysis['加料狀態'] == input_topping)]
                base_calc_price = base_match['均價'].values[0] if not base_match.empty else df['價格(L)'].mean()
                
                tier_multiplier = {"大眾引流款 (低毛利/衝量款)": 0.85, "市場主流款 (利潤與銷量平衡)": 1.0, "奢華旗艦款 (高溢價/故事包裝)": 1.25}
                rec_l_price = round((base_calc_price * tier_multiplier[input_tier]) / 5) * 5
                rec_m_price = round((rec_l_price - 15) / 5) * 5
                
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #1E293B, #0F172A); color: #F8FAFC; padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border-top: 4px solid #38BDF8;">
                    <h5 style="color: #38BDF8; margin-top:0; font-weight:800; font-size:16px;">🤖 AI 新品定價與變現指南</h5>
                    <div style="display:flex; justify-content: space-around; margin: 20px 0; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;">
                        <div style="text-align:center;"><span style="font-size:12px; color:#94A3B8;">建議中杯定價</span><br><b style="font-size:26px; color:#FBBF24;">${rec_m_price} 元</b></div>
                        <div style="text-align:center;"><span style="font-size:12px; color:#94A3B8;">建議大杯定價</span><br><b style="font-size:26px; color:#34D399;">${rec_l_price} 元</b></div>
                        <div style="text-align:center;"><span style="font-size:12px; color:#94A3B8;">爆款毛利潛力</span><br><b style="font-size:26px; color:#38BDF8;">{"極致高爆發" if input_tier=="奢華旗艦款 (高溢價/故事包裝)" else "穩健護城河" if input_tier=="市場主流款 (利潤與銷量平衡)" else "薄利多銷型"}</b></div>
                    </div>
                    <p style="font-size:14px; color:#CBD5E1; margin-bottom:6px;"><b>✨ AI 專屬行銷文案包裝指南：</b></p>
                    <p style="font-size:13px; color:#94A3B8; line-height:1.7; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px;">
                    {"【職人奢華流】契作產地直送頂級 " + input_base + " 悉心淬鍊，融合黃金比例，完美封存最純粹的極致風韻。包裝建議採用高質感霧面冷調杯身，文案主打職人工藝與稀缺性，鎖定注重生活儀式感的都會輕奢客群，輕鬆打破價格防線。" if input_tier=="奢華旗艦款 (高溢價/故事包裝)" else "【每日必喝款】完美揉合大盤精髓，入口滑順、回甘悠長，是菜單上無可取代的靈魂支柱。建議配合辦公室下午茶進行促銷，建立高頻次、高復購率的日常品牌粘性。" if input_tier=="市場主流款 (利潤與銷量平衡)" else "【破局引流彈】以最具市場破壞力的極致價格切入，主打超高性價比與閃電出杯速度。作為門店『帶路雞』，可迅速吸引大批團購新客，並透過引導加點高毛利配料完成獲利二次轉化。"}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("數據庫結構不完整，無法執行研發矩陣計算。")

    # ==========================================
    # 🔥 全新擴充：頁籤 11 - 財務損益推演
    # ==========================================
    with tab11:
        st.markdown("### 💰 門店營運利潤與損益平衡推演 (Profit Simulator)")
        st.caption("結合當前過濾市場的真實大杯價格水位，動態推演門店原物料成本（COGS）、固定開銷與單月保本營業防線。")
        
        # 提取當前篩選數據的大杯均價作為營收基準
        market_avg_rev = filtered_df['價格(L)'].mean() if not filtered_df.empty and pd.notna(filtered_df['價格(L)'].mean()) else 60
        
        calc_c1, calc_c2 = st.columns([1, 1.5])
        
        with calc_c1:
            st.markdown("#### ⚙️ 門店成本結構與開銷配置")
            cogs_pct = st.slider("1. 原物料與包材成本佔比 (COGS %)", min_value=20, max_value=50, value=33, step=1, help="包含茶葉、鮮奶、配料、杯材、吸管與提袋損耗總和。")
            fixed_rent = st.number_input("2. 每月門店租金與水電雜支 (元)", min_value=10000, max_value=200000, value=45000, step=5000)
            fixed_labor = st.number_input("3. 每月正職與兼職員工總薪資 (元)", min_value=20000, max_value=500000, value=75000, step=5000)
            
            # 財務核心計算
            var_cost_per_cup = market_avg_rev * (cogs_pct / 100)
            margin_per_cup = market_avg_rev - var_cost_per_cup
            total_fixed_cost = fixed_rent + fixed_labor
            
            # 防止分母為零
            be_volume = int(np.ceil(total_fixed_cost / margin_per_cup)) if margin_per_cup > 0 else 0
            
            st.divider()
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.08); padding: 22px; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
                <span style="font-size:14px; color:#065F46; font-weight:700;">🎯 單月損益平衡防線 (Break-Even Point)：</span><br>
                <h3 style="margin: 10px 0; color:#047857; font-size:32px; font-weight:900;">{be_volume:,} 杯 / 月</h3>
                <span style="font-size:13px; color:#065F46;">門店平均每日需穩定賣出 <b>{int(np.ceil(be_volume/30))} 杯</b> 即可跨越保本線，往後的每一杯都是純淨利！</span>
            </div>
            """, unsafe_allow_html=True)
            
        with calc_c2:
            st.markdown("#### 📊 單杯手搖飲財務瀑布拆解 (Waterfall Chart)")
            
            fig_wf = go.Figure(go.Waterfall(
                orientation = "v",
                measure = ["relative", "relative", "total"],
                x = ["大杯真實均價營收", "原物料/包材成本 (COGS)", "單杯貢獻毛利 (Margin)"],
                textposition = "outside",
                text = [f"${market_avg_rev:.1f}", f"-${var_cost_per_cup:.1f}", f"${margin_per_cup:.1f}"],
                y = [market_avg_rev, -var_cost_per_cup, 0],
                connector = {"line":{"color":"#CBD5E1", "dash":"dot"}},
                decreasing = {"marker":{"color":"#EF4444"}},
                increasing = {"marker":{"color":"#10B981"}},
                totals = {"marker":{"color":"#6366F1"}}
            ))
            fig_wf.update_layout(height=280)
            st.plotly_chart(apply_common_layout(fig_wf), use_container_width=True)
            
            st.markdown("#### 📈 月銷量規模 vs 淨利潤動態演化曲線")
            
            # 動態生成銷量級數
            max_plot_vol = max(be_volume * 2, 4000)
            volumes = np.arange(0, max_plot_vol, int(max_plot_vol/40) if max_plot_vol > 40 else 1)
            profits = (volumes * margin_per_cup) - total_fixed_cost
            
            prof_df = pd.DataFrame({"月銷量 (杯)": volumes, "預估月淨利 (元)": profits})
            
            fig_line = px.line(prof_df, x="月銷量 (杯)", y="預估月淨利 (元)", color_discrete_sequence=["#4F46E5"])
            # 繪製 0 元損益水平線
            fig_line.add_shape(type="line", x0=0, y0=0, x1=max(volumes), y1=0, line=dict(color="#94A3B8", width=1.5, dash="dash"))
            
            if be_volume > 0:
                fig_line.add_trace(go.Scatter(x=[be_volume], y=[0], mode='markers+text', name='損益平衡點',
                                              text=[f" 損益平衡線 ({be_volume}杯)"], textposition="top right",
                                              marker=dict(color='#F59E0B', size=12, line=dict(color='white', width=2))))
            fig_line.update_layout(showlegend=False, height=320)
            st.plotly_chart(apply_common_layout(fig_line), use_container_width=True)
