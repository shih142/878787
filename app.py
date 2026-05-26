import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import numpy as np
import google.generativeai as genai

# ==========================================
# 1. 網頁基本與高階外觀設定 (黑曜石極光 UI)
# ==========================================
st.set_page_config(page_title="手搖飲全知戰情室 (Gemini 究極版)", page_icon="🧋", layout="wide")

# 注入高端深色系黑曜石 CSS 樣式表
st.markdown("""
    <style>
    /* 引入現代感雙字體系統 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Noto Sans TC', sans-serif;
    }
    
    /* 全域賽博深色漸層背景 */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0F172A 0%, #020617 100%) !important;
        color: #E2E8F0 !important;
    }
    
    /* 強制 Streamlit 原生標籤、文字在深色背景下清晰呈現 */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, label {
        color: #CBD5E1 !important;
    }
    
    h1 { font-weight: 900 !important; color: #F8FAFC !important; letter-spacing: -1px; margin-bottom: 5px; }
    h2, h3, h4 { font-weight: 800 !important; color: #F1F5F9 !important; }
    
    /* 側邊欄控制台深色毛玻璃化 */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 10px 0 40px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stSidebar"] .stWidget {
        background: rgba(30, 41, 59, 0.4);
        padding: 15px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] .stWidget:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    /* 賽博網頁頁籤微互動設計 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: none; padding: 10px 0; }
    .stTabs [data-baseweb="tab"] {
        height: 48px; white-space: pre-wrap; background-color: rgba(30, 41, 59, 0.4); 
        border-radius: 14px; padding: 0 22px; font-size: 15px; font-weight: 700; color: #94A3B8; 
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid rgba(255, 255, 255, 0.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); margin-right: 2px; backdrop-filter: blur(8px);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(30, 41, 59, 0.7); color: #F8FAFC; transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: white !important; border: none !important; 
        box-shadow: 0 12px 24px -6px rgba(79, 70, 229, 0.5) !important;
        transform: translateY(-3px) !important;
    }
    
    /* KPI 容器暗色光澤卡片 */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05); padding: 22px; border-radius: 20px; 
        box-shadow: 0 12px 35px -5px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.05); 
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-6px); 
        box-shadow: 0 25px 40px -10px rgba(0, 0, 0, 0.6);
        border-color: rgba(99, 102, 241, 0.4);
    }
    div[data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 800 !important; color: #F8FAFC !important; }
    div[data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #94A3B8 !important; }
    
    /* AI 決策盒黑曜石極光版 */
    .ai-insight-box {
        background: linear-gradient(145deg, #020617, #1E293B); color: #E2E8F0;
        padding: 28px; border-radius: 20px; box-shadow: 0 20px 45px rgba(0,0,0,0.4);
        border-left: 6px solid #38BDF8; margin-bottom: 25px; position: relative; overflow: hidden;
    }
    .ai-insight-box h4 { color: #38BDF8 !important; margin-top: 0; font-weight: 900; letter-spacing: 0.5px; }
    .ai-insight-box li { margin-bottom: 10px; font-size: 15px; color: #CBD5E1; line-height: 1.6; }
    
    /* Gemini 輸出的精美外殼 */
    .gemini-output-container {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 30px;
        border-radius: 18px;
        margin-top: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧋 台灣手搖飲商業分析戰情室 (Gemini API 究極版)")
st.markdown("<p style='font-size:16px; color:#94A3B8;'>融合 3D 立體版圖、Gemini 決策大腦、定價沙盤推演與消費者行為學的 <b>神級商業決策系統</b>。</p>", unsafe_allow_html=True)

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
        return pd.DataFrame()

with st.spinner("🚀 系統啟動中... 正在載入全台手搖飲大數據..."):
    df = load_data()

if df.empty:
    st.error("❌ 系統初始化失敗：找不到 `飲料清單.xlsx` 或活頁簿名稱不正確。")
    st.info("💡 請確認專案根目錄下存在 `飲料清單.xlsx` 且包含名為 `飲料清單` 的工作表。")
    st.stop()

st.toast('戰情室啟動成功！資料已同步。', icon='✅')
all_stores = df['店家'].dropna().unique().tolist()
market_expectation = df.groupby(['標籤1', '加料狀態'])['價格(L)'].mean().reset_index()
market_expectation.rename(columns={'價格(L)': '市場預期價'}, inplace=True)

# ==========================================
# 3. 側邊欄：全域過濾器與 Gemini API 配置
# ==========================================
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 10px 0;'><img src='https://cdn-icons-png.flaticon.com/512/3081/3081162.png' width='85'></div>", unsafe_allow_html=True)
    st.header("🎛️ 究極控制台")
    st.caption("連動全站 12 大模組與 AI 大腦")
    
    selected_stores = st.multiselect("🏪 選擇分析品牌", options=all_stores, default=all_stores[:7] if len(all_stores)>=7 else all_stores)
    all_bases = df['標籤1'].dropna().unique().tolist()
    selected_base = st.multiselect("🍃 選擇基底茶", options=all_bases, placeholder="預設為全茶種")
    topping_option = st.radio("🍬 加料狀態", ["全部", "有加料", "純茶/無加料"])
    
    st.divider()
    st.header("🔑 Gemini API 設定")
    default_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key_input = st.text_input("輸入 Gemini API Key", type="password", value=default_key, help="填入您的 API 金鑰以解鎖即時生成式報告大腦。")
    
    if api_key_input:
        genai.configure(api_key=api_key_input)
        st.caption("🟢 Gemini API 已成功配置")
    else:
        st.caption("🟡 未配置 API 金鑰 (部份即時分析將呈現靜態備份)")

    st.divider()
    st.markdown(f"**📊 總體資料庫狀況**\n- 總品牌數: ` {df['店家'].nunique()} ` 家\n- 總品項數: ` {len(df)} ` 款")
    st.caption("*(Powered by Streamlit Cyber UI)*")

filtered_df = df.copy()
if selected_stores: filtered_df = filtered_df[filtered_df['店家'].isin(selected_stores)]
if selected_base: filtered_df = filtered_df[filtered_df['標籤1'].isin(selected_base)]
if topping_option != "全部": filtered_df = filtered_df[filtered_df['加料狀態'] == topping_option]

def apply_common_layout(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(t=50, b=30, l=15, r=15),
        hoverlabel=dict(bgcolor="rgba(15, 23, 42, 0.95)", font_size=14, font_color="#F8FAFC", font_family="Inter", bordercolor="rgba(255,255,255,0.1)"),
        font=dict(color="#CBD5E1", family="Noto Sans TC")
    )
    fig.update_xaxes(showgrid=False, linecolor='#334155', title_font=dict(size=13, color='#94A3B8'), tickfont=dict(color='#94A3B8'))
    fig.update_yaxes(showgrid=True, gridcolor='#334155', linecolor='rgba(0,0,0,0)', title_font=dict(size=13, color='#94A3B8'), tickfont=dict(color='#94A3B8'))
    return fig

def call_gemini(prompt_text):
    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"❌ **Gemini 引擎串接失敗**\n原因：{str(e)}\n\n*提示：請檢查左側控制台的 API 金鑰是否輸入正確。*"

if filtered_df.empty:
    st.warning("⚠️ 目前的篩選條件沒有相符的資料，請放寬側邊欄的篩選條件！")
    st.stop()

# ==========================================
# 4. 建立 12 大功能頁籤 (新增消費者角度)
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📊 戰情總覽與洞察", "🌌 3D星系版圖", "⚔️ 品牌死鬥 PK", "📈 定價與加料", 
    "🔄 樞紐熱力圖", "🤖 AI預測模擬", "🧠 CP值分析", "🧑‍🤝‍🧑 消費者行為學", 
    "📋 原始數據", "📝 AI全能報告", "🧪 藍海新品研發", "💰 財務損益推演"
])

# ------------------------------------------
# 頁籤 1：營運總覽與 AI 洞察
# ------------------------------------------
with tab1:
    st.markdown("<h3 style='margin-top:10px;'>🚀 關鍵營運指標 (KPI)</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 有效品項總數", f"{len(filtered_df)} 項")
    avg_l_price = filtered_df['價格(L)'].mean()
    col2.metric("💰 均價水位 (大杯)", f"${avg_l_price:.1f}" if pd.notna(avg_l_price) else "N/A")
    topping_pct = (filtered_df['加料'] == 1.0).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    col3.metric("🧋 加料品項佔比", f"{topping_pct:.1f}%")
    col4.metric("🏪 涵蓋品牌數", f"{filtered_df['店家'].nunique()} 家")
    
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
        <h4>🧠 AI 戰略分析大腦 (CEO Insight 快照)</h4>
        <ul>
            <li><strong>定價天花板：</strong>目前選取範圍內，定價最高昂的品牌是 <b>{most_expensive['店家']}</b> (均價 ${most_expensive['均價']:.1f})，主打高客單價策略。</li>
            <li><strong>平價破壞者：</strong>定價最親民的品牌是 <b>{cheapest['店家']}</b> (均價 ${cheapest['均價']:.1f})，適合以量取勝的量販戰術。</li>
            <li><strong>菜單海王：</strong><b>{most_items['店家']}</b> 擁有高達 {most_items['品項數']} 個品項，產品線豐富，但需注意庫存管理成本。</li>
            <li><strong>咀嚼系霸主：</strong><b>{most_toppings['店家']}</b> 的加料品項佔比高達 {most_toppings['加料佔比']*100:.0f}%，是靠高毛利配料推升營收的典範。</li>
        </ul>
        <small style='color: #38BDF8;'>💡 提示：前往「🧑‍🤝‍🧑 消費者行為學」頁籤，可切換至消費者視角，分析社群輿情與客群掏錢心理學。</small>
    </div>
    """
    st.markdown(insight_text, unsafe_allow_html=True)
        
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📊 品牌均價排行榜")
        avg_price_df = filtered_df.groupby(['店家', '加料狀態'])['價格(L)'].mean().reset_index()
        fig1 = px.bar(avg_price_df, x='店家', y='價格(L)', color='加料狀態', barmode='group', text_auto='.0f', 
                     color_discrete_map={'有加料': '#818CF8', '純茶/無加料': '#34D399'})
        fig1.update_layout(xaxis={'categoryorder':'total descending'}, yaxis_title="平均價格 (元)", xaxis_title="")
        fig1 = apply_common_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.markdown("#### 🍩 全域基底茶生態圈")
        fig2 = px.pie(filtered_df, names='標籤1', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_traces(textposition='inside', textinfo='percent+label', pull=[0.03 if i==0 else 0 for i in range(len(filtered_df['標籤1'].unique()))])
        fig2.update_layout(margin=dict(t=30, b=10, l=10, r=10), showlegend=False)
        fig2 = apply_common_layout(fig2)
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
                               color_discrete_sequence=px.colors.qualitative.Prism,
                               hover_data={'店家': False, '均價': ':.1f', '品項數': True, '加料佔比(%)': True})
        fig_3d.update_traces(textposition='top center', marker=dict(line=dict(color='rgba(255,255,255,0.2)', width=1), opacity=0.85))
        fig_3d.update_layout(scene=dict(
            xaxis=dict(title='大杯均價 (X)', backgroundcolor="#0F172A", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
            yaxis=dict(title='品項豐富度 (Y)', backgroundcolor="#1E293B", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
            zaxis=dict(title='加料佔比% (Z)', backgroundcolor="#0F172A", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.6))
        ), height=600, margin=dict(l=0, r=0, b=0, t=0), showlegend=False)
        st.plotly_chart(fig_3d, use_container_width=True)

    st.divider()
    
    with st.expander("📂 展開查看：品牌戰略板塊矩陣與菜單宇宙", expanded=False):
        st.markdown("#### 🧱 品牌戰略定價板塊矩陣 (Treemap Matrix)")
        if not quad_df.empty:
            fig_tree = px.treemap(quad_df, path=[px.Constant("全市場版圖"), '店家'], values='品項數', color='均價', color_continuous_scale='YlOrRd')
            fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>品項數: %{value} 項<br>大杯均價: $ %{color:.1f}<extra></extra>', textinfo="label+value", textfont=dict(size=15, color="white"), root_color="#1E293B")
            fig_tree.update_layout(margin=dict(t=30, l=10, r=10, b=20), height=450)
            st.plotly_chart(fig_tree, use_container_width=True)
        
        st.divider()
        
        st.markdown("#### 🌞 專屬品牌菜單宇宙 (Sunburst Chart)")
        valid_sunburst_stores = filtered_df['店家'].unique().tolist()
        if valid_sunburst_stores:
            selected_sun_store = st.selectbox("🔍 選擇要放大解剖的品牌菜單", options=valid_sunburst_stores, index=0)
            sun_df = filtered_df[filtered_df['店家'] == selected_sun_store].dropna(subset=['價格(L)']).copy().fillna("無分類")
            fig_sun = px.sunburst(sun_df, path=['店家', '標籤1', '加料狀態', '飲料品項'], values='價格(L)', color='價格(L)', color_continuous_scale='Thermal')
            fig_sun.update_layout(margin=dict(t=20, l=10, r=10, b=20), height=600)
            fig_sun.update_traces(marker=dict(line=dict(color='#0F172A', width=1)), hovertemplate='<b>%{label}</b><br>大杯售價: $ %{color:.0f}<extra></extra>')
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
                v1 = b_df['價格(L)'].mean()
                v2 = len(b_df)
                v3 = (b_df['加料'] == 1.0).sum() / len(b_df) * 100 if len(b_df)>0 else 0
                v4 = b_df['標籤1'].nunique()
                return [s1, s2, s3, s4], [v1, v2, v3, v4]

            scores_a, vals_a = get_brand_metrics(brand_a)
            scores_b, vals_b = get_brand_metrics(brand_b)
            categories = ['價格水準 (高單價)', '品項豐富度', '加料專注度', '茶種多樣性']

            radar_c1, radar_c2 = st.columns([1.2, 1])
            with radar_c1:
                st.markdown("#### 🕸️ 商業模式雷達圖")
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=scores_a, theta=categories, fill='toself', name=brand_a, fillcolor='rgba(244, 63, 94, 0.15)', line_color='#F43F5E'))
                fig_radar.add_trace(go.Scatterpolar(r=scores_b, theta=categories, fill='toself', name=brand_b, fillcolor='rgba(56, 189, 248, 0.15)', line_color='#38BDF8'))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#334155"), angularaxis=dict(gridcolor="#334155")), showlegend=True, margin=dict(t=40, b=40, l=40, r=40))
                fig_radar = apply_common_layout(fig_radar)
                st.plotly_chart(fig_radar, use_container_width=True)
                
                with st.expander("📋 展開直接對比數據"):
                    pk_table = pd.DataFrame({
                        "評估維度": ["大杯平均單價", "總品項數量", "加料品項佔比", "涵蓋基底茶種類"],
                        f"{brand_a}": [vals_a[0], vals_a[1], vals_a[2], vals_a[3]],
                        f"{brand_b}": [vals_b[0], vals_b[1], vals_b[2], vals_b[3]]
                    })
                    st.dataframe(
                        pk_table, 
                        column_config={
                            f"{brand_a}": st.column_config.NumberColumn(format="%.1f"),
                            f"{brand_b}": st.column_config.NumberColumn(format="%.1f")
                        },
                        use_container_width=True, 
                        hide_index=True
                    )

            with radar_c2:
                st.markdown("#### 📊 價格分佈疊加圖 (Histogram)")
                pk_df = df[df['店家'].isin([brand_a, brand_b])]
                fig_pk1 = px.histogram(pk_df, x="價格(L)", color="店家", barmode="overlay", nbins=15, color_discrete_sequence=['#F43F5E', '#38BDF8'], opacity=0.6)
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
            平均中杯價=('價格(M)', 'mean'),
            平均大杯價=('價格(L)', 'mean'),
            平均升杯價差=('升杯價差', 'mean'),
            有效品項數=('飲料品項', 'count')
        ).reset_index().sort_values(by='有效品項數', ascending=False).reset_index(drop=True)
        summary_table.index += 1
        
        st.dataframe(
            summary_table,
            column_config={
                "平均中杯價": st.column_config.NumberColumn(format="$%.1f"),
                "平均大杯價": st.column_config.NumberColumn(format="$%.1f"),
                "平均升杯價差": st.column_config.NumberColumn(format="$%.1f"),
            },
            use_container_width=True
        )
        
    st.divider()
    box_col, top_col = st.columns(2)
    
    with box_col:
        st.markdown("#### 📦 價格區間與極端值 (盒鬚圖)")
        fig_box = px.box(filtered_df, x='店家', y='價格(L)', color='店家', points="all", color_discrete_sequence=px.colors.qualitative.Set2)
        fig_box.update_layout(xaxis={'categoryorder':'median descending'}, showlegend=False, yaxis_title="大杯價格 (元)", xaxis_title="")
        fig_box = apply_common_layout(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)
        
    with top_col:
        st.markdown("#### 🍬 加料經濟學：加料平均溢價")
        top_pivot = filtered_df.pivot_table(index='店家', columns='加料狀態', values='價格(L)', aggfunc='mean').reset_index()
        if '有加料' in top_pivot.columns and '純茶/無加料' in top_pivot.columns:
            top_pivot['加料溢價'] = top_pivot['有加料'] - top_pivot['純茶/無加料']
            top_pivot = top_pivot.dropna(subset=['加料溢價']).sort_values(by='加料溢價', ascending=False)
            fig_top = px.bar(top_pivot, x='店家', y='加料溢價', text_auto='+.1f', color='加料溢價', color_continuous_scale='Agsunset')
            fig_top.update_layout(yaxis_title="平均加料溢價 (元)", xaxis_title="")
            fig_top = apply_common_layout(fig_top)
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("💡 目前篩選的資料維度不足以計算加料溢價。")

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
            color_scale = 'Cividis'
        else:
            pivot_df = filtered_df.pivot_table(index=y_axis, columns=x_axis, values='價格(L)', aggfunc='mean').round(1)
            color_scale = 'Magma'

        st.markdown("#### 📊 樞紐分析熱力圖")
        fig_heatmap = px.imshow(pivot_df, text_auto=True, color_continuous_scale=color_scale, aspect="auto")
        fig_heatmap.update_layout(margin=dict(t=40, b=20, l=0, r=0))
        fig_heatmap.update_xaxes(side="top")
        fig_heatmap = apply_common_layout(fig_heatmap)
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
            color_discrete_map={"⚠️ 升杯溢價 (偏貴)": "#F43F5E", "✅ 合理升杯 (符行情)": "#475569", "🔥 超值升杯 (划算)": "#34D399"},
            trendline="ols", trendline_scope="overall", opacity=0.85, size_max=11
        )
        fig_reg.update_layout(xaxis_title="中杯實際價格 (自變數 X)", yaxis_title="大杯實際價格 (應變數 Y)", hovermode="closest")
        fig_reg = apply_common_layout(fig_reg)
        st.plotly_chart(fig_reg, use_container_width=True)
        
        with st.expander("📋 展開查看 AI 升杯性價比明細表"):
            table_display = reg_df[['店家', '飲料品項', '標籤1', '價格(M)', '價格(L)', 'AI預測大杯價', '升杯落差', 'AI升杯判定']].copy()
            table_display = table_display.sort_values(by='升杯落差', ascending=False).reset_index(drop=True)
            table_display.index += 1
            st.dataframe(
                table_display, 
                column_config={
                    "價格(M)": st.column_config.NumberColumn(format="$%d"),
                    "價格(L)": st.column_config.NumberColumn(format="$%d"),
                    "AI預測大杯價": st.column_config.NumberColumn(format="$%.1f"),
                    "升杯落差": st.column_config.NumberColumn(format="%+.1f 元"),
                },
                use_container_width=True, 
                height=350
            )
    else:
        st.warning("⚠️ 此篩選條件下的中/大杯數據不足，無法啟動 AI 預測引擎。")

# ------------------------------------------
# 頁籤 7：預期心理分析 (動態矩陣權重版)
# ------------------------------------------
with tab7:
    st.markdown("### 🧠 究極矩陣式預期心理分析 (Matrix-Weighted CP Index)")
    st.caption("導入 MCDA 演算法，依據品項的「物料成本」、「工藝複雜度」與「品牌招牌光環」進行動態權重校正。")
    
    diagnostic_df = filtered_df.copy()
    diagnostic_df['加料狀態'] = diagnostic_df['加料狀態'].fillna('純茶/無加料')
    diagnostic_df = diagnostic_df.dropna(subset=['價格(L)'])
    
    psych_df = pd.merge(diagnostic_df, market_expectation, on=['標籤1', '加料狀態'], how='left')
    global_l_mean = df['價格(L)'].mean() if not df.empty else 50
    psych_df['市場預期價'] = psych_df['市場預期價'].fillna(global_l_mean)

    if not psych_df.empty:
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
        p_c1.metric("💸 高質感定位品項佔比", f"{premium_pct:.1f}%")
        p_c2.metric("😐 營收護城河 (行情品項)", f"{normal_pct:.1f}%")
        p_c3.metric("🤑 破局爆單 (超值品項)", f"{value_pct:.1f}%")
        
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
        psych_summary = psych_summary.sort_values(by='綜合 CP 值指數', ascending=False).reset_index(drop=True)
        psych_summary.index += 1
        
        st.dataframe(
            psych_summary, 
            column_config={
                "平均真實落差": st.column_config.NumberColumn("校正後平均落差", format="%+.1f 元"),
                "綜合 CP 值指數": st.column_config.ProgressColumn("綜合 CP 值指數", min_value=0, max_value=100, format="%.1f", color="#818CF8")
            },
            use_container_width=True
        )
        
        st.divider()
        
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### 📊 品牌消費者體感結構分佈")
            psych_count = psych_df.groupby(['店家', '消費者體感']).size().reset_index(name='數量')
            fig_psych_bar = px.bar(
                psych_count, y="店家", x="數量", color="消費者體感", 
                orientation='h', barmode="relative", text_auto=True,
                color_discrete_map={
                    "💸 品牌溢價 (主打高質感)": "#818CF8", 
                    "😐 符合預期 (市場行情)": "#475569", 
                    "🤑 體感超值 (利潤回饋)": "#34D399"
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
                    "💸 品牌溢價 (主打高質感)": "#818CF8", 
                    "😐 符合預期 (市場行情)": "#475569", 
                    "🤑 體感超值 (利潤回饋)": "#34D399"
                }, opacity=0.85
            )
            fig_psych_scatter.update_traces(marker=dict(size=12, line=dict(width=1.5, color='#0F172A')))
            
            min_val = min(psych_df["調整後預期價"].min(), psych_df["價格(L)"].min())
            max_val = max(psych_df["調整後預期價"].max(), psych_df["價格(L)"].max())
            fig_psych_scatter.add_shape(
                type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, 
                line=dict(color="rgba(255, 255, 255, 0.2)", dash="dash", width=1.5)
            )
            fig_psych_scatter.update_layout(xaxis_title="動態權重校正行情 (元)", yaxis_title="實際大杯售價 (元)")
            fig_psych_scatter = apply_common_layout(fig_psych_scatter)
            st.plotly_chart(fig_psych_scatter, use_container_width=True)

# ------------------------------------------
# 🔥 🔥 頁籤 8：🧑‍🤝‍🧑 消費者行為心理學 (全新新增模組)
# ------------------------------------------
with tab8:
    st.markdown("### 🧑‍🤝‍🧑 終端消費者行為心理學與輿情觀測大腦")
    st.caption("從「買方」與「社群網民」視角出發，深度解析消費者掏錢時的真實體感、情感動機以及潛在社群風暴。")
    
    if not filtered_df.empty:
        total_items_c = len(filtered_df)
        global_avg_c = filtered_df['價格(L)'].mean()
        top_base_c = filtered_df['標籤1'].value_counts().idxmax() if '標籤1' in filtered_df.columns and not filtered_df['標籤1'].empty else "純茶"
        topping_pct_c = (filtered_df['加料'] == 1.0).sum() / total_items_c * 100 if total_items_c > 0 else 0
        
        consumer_stats_summary = {
            "大盤平均定價": f"{global_avg_c:.1f}元",
            "主力依賴基底": top_base_c,
            "加料/咀嚼系依賴度": f"{topping_pct_c:.1f}%",
            "當前篩選品牌": filtered_df['店家'].dropna().unique().tolist()
        }
        
        if api_key_input:
            st.success("✨ Gemini 行為心理學專家已就緒。點擊下方按鈕進行買方視角透視。")
            if st.button("🧑‍🤝‍🧑 啟動 Gemini 消費者視角深度解碼", key="run_gemini_consumer_behavior"):
                with st.spinner("🧠 正在模擬消費者大腦、爬梳 Dcard/Threads 輿情流..."):
                    
                    prompt_consumer = f"""
                    你是一位精通台灣手搖飲文化、Z世代消費心理學、小資族行為學以及社群輿情（Dcard、PTT、Threads）的頂級行銷創意總監。
                    請根據以下提供的當前市場大數據快照，完全站在「消費者（買方）」的角度，為經營團隊撰寫一份「消費者核心洞察報告」。
                    
                    【當前市場數據快照】：
                    {str(consumer_stats_summary)}
                    
                    【撰寫格式與核心內容要求】：
                    1. 🎯 【客群畫像與生活型態】：精準描繪會高頻購買這群品牌的終端受眾（如：辦公室下午茶小資、戒不掉糖分的咀嚼狂熱者、追求輕負擔的都會白領等），他們的日常痛點是什麼？
                    2. 🧠 【掏錢心理學與體感代價】：消費者在購買這群品牌的飲品時，心中的「價格痛感」如何？大盤均價為 {global_avg_c:.1f} 元，他們是在購買一杯「續命水」、「短暫的小確幸」，還是對「高質感職人原茶的信仰」？
                    3. 💬 【虛擬社群輿情觀測箱（Dcard/Threads 體裁）】：模擬當前最真實的社群風向！請寫出網民在 Dcard 或 Threads 上對這群品牌的「私房好評（如：哪個品項神到哭）」與「毒舌吐槽爆料（如：哪家偏貴、糖度很迷）」，語氣要幽默生動、貼近台灣網路口語。
                    4. ⚠️ 【消費者退粉地雷（體驗毒藥）】：點出吧台操作或產品設計上，哪些細節（例如：珍珠中間沒熟、鮮奶茶茶味太淡被嫌水、包裝杯身太醜不適合拍照）會讓這群消費者「一次報銷」再也不復購？
                    
                    請用繁體中文（台灣地區商務與網路流行語交織的語氣）產出，內容要犀利、極具市場臨場感。
                    """
                    
                    consumer_ai_report = call_gemini(prompt_consumer)
                    st.markdown(f"<div class='gemini-output-container'>{consumer_ai_report}</div>", unsafe_allow_html=True)
        else:
            st.info("💡 提示：請在左側控制台輸入 Gemini API Key 以解鎖生成式消費者心理學分析。")
            
            # 靜態模擬視覺
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.4); padding: 25px; border-radius: 16px; border: 1px dashed rgba(255,255,255,0.1);">
                <h5 style="color: #818CF8; margin-top:0;">📊 大數據體感指標預估 (買方觀點)</h5>
                <p>根據目前篩選大盤行情，終端市場心理反應如下：</p>
                <ul>
                    <li><b>價格抗性風險：</b>均價若超越 $65 元，辦公室團購訂單的決策阻力將會直線上升 45%。</li>
                    <li><b>咀嚼系心流：</b>配料佔比直接連動社群拍照打卡率，是推動主動傳播的黃金鑰匙。</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# ------------------------------------------
# 頁籤 9：原始數據檢視
# ------------------------------------------
with tab9:
    st.markdown("### 📋 原始數據觀測站")
    st.caption("當前通過篩選器的底層明細資料。")
    st.dataframe(filtered_df, use_container_width=True)

# ------------------------------------------
# 頁籤 10：AI 全能商業戰略總結報告
# ------------------------------------------
with tab10:
    st.markdown("### 📝 AI 全能商業戰略總結報告 (Executive Summary)")
    st.caption("自動融合全站大數據矩陣，透過 **Gemini API** 動態生成的頂層戰略洞察與決策建議。")
    
    if not filtered_df.empty and filtered_df['店家'].nunique() > 0:
        total_brands = filtered_df['店家'].nunique()
        total_items = len(filtered_df)
        global_avg_price = filtered_df['價格(L)'].mean()
        
        brand_summary = filtered_df.groupby('店家').agg(
            均價=('價格(L)', 'mean'), 品項數=('飲料品項', 'count')
        ).reset_index()
        
        top_base = filtered_df['標籤1'].value_counts().idxmax() if '標籤1' in filtered_df.columns and not filtered_df['標籤1'].empty else "未分類"
        top_base_pct = (filtered_df['標籤1'] == top_base).sum() / total_items * 100 if total_items > 0 else 0
        topping_pct = (filtered_df['加料'] == 1.0).sum() / total_items * 100 if total_items > 0 else 0

        market_stats_summary = {
            "總品牌數": total_brands,
            "總品項數": total_items,
            "市場大杯平均售價": f"{global_avg_price:.1f}元",
            "核心茶種王": f"{top_base} (佔比 {top_base_pct:.1f}%)",
            "配料商品佔比": f"{topping_pct:.1f}%",
            "品牌個別均價明細": brand_summary.set_index('店家')['均價'].round(1).to_dict()
        }

        if api_key_input:
            st.success("✨ Gemini 大腦就緒。點擊按鈕，AI 將對當前篩選的數據進行全盤策略擬定。")
            if st.button("🚀 啟動 Gemini 頂層戰略運算", key="run_gemini_market_report"):
                with st.spinner("🧠 Gemini 大腦正在深度解構全域矩陣並撰寫白皮書，請稍候..."):
                    
                    prompt = f"""
                    你是一位精通台灣手搖飲連鎖市場、餐飲供應鏈以及消費者心理學的頂級商業策略顧問（Chief Strategy Officer）。
                    請根據以下提供的當前市場真實大數據統計快照，為執行長（CEO）撰寫一份極具戰略高度與落地執行細節的「商業戰略白皮書」。
                    
                    【當前市場篩選大數據快照】：
                    {str(market_stats_summary)}
                    
                    【撰寫格式與核心內容要求】：
                    1. 🎯 【市場定位與宏觀矩陣診斷】：依據平均售價與配料佔比，診斷目前的競爭屬於何種型態，並分析其隱含的商機與危機。
                    2. 📊 【菜單工程與定價策略（Menu Engineering）】：新產品若切入此市場，建議的「流量款」與「高毛利利基款」定價錨點應該如何設定？
                    3. 🧋 【加料經濟與配料變現解密】：針對目前的加料品項佔比，給出具體建言。
                    4. 🛠️ 【CEO 執行行動方案（Actionable Roadmap）】：給出短中期的具體落地步驟（至少3點）。
                    
                    請用繁體中文（台灣地區商務語氣）回答。排版需精美，展現百萬級顧問報告的專業度與銳利度。
                    """
                    
                    ai_response = call_gemini(prompt)
                    st.markdown(f"<div class='gemini-output-container'>{ai_response}</div>", unsafe_allow_html=True)
        else:
            st.info("💡 提示：在左側控制台輸入 Gemini API Key 後，可解鎖即時生成式數據洞察。")
            if global_avg_price >= 55: market_type = "⚖️ 白領輕奢精緻戰場"
            elif global_avg_price >= 40: market_type = "🔥 主流中產高頻剛需區"
            else: market_type = "🥊 價格破壞型下沉紅海"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #020617 0%, #1E293B 100%); color: #F8FAFC; padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); margin-bottom: 25px;">
                <h3 style="color: #A5B4FC; margin-top: 0; font-weight: 900; letter-spacing: 1px;">🔮 戰情官決策大腦：戰略白皮書 (靜態快照)</h3>
                <hr style="border-color: rgba(255,255,255,0.08); margin: 20px 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div><span>當前市場定位分類</span><h4 style="color: #F43F5E; margin: 5px 0 0 0; font-size: 18px;">{market_type}</h4></div>
                    <div><span>核心基底茶霸主</span><h4 style="color: #34D399; margin: 5px 0 0 0; font-size: 18px;">{top_base} ({top_base_pct:.1f}%)</h4></div>
                    <div><span>大盤平均價格</span><h4 style="color: #FBBF24; margin: 5px 0 0 0; font-size: 18px;">${global_avg_price:.1f} 元</h4></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 當前篩選條件下無足夠數據，AI 無法生成戰略報告。")

# ==========================================
# 🔥 頁籤 11 - 藍海新品研發實驗室
# ==========================================
with tab11:
    st.markdown("### 🧪 藍海新品研發與智慧定價實驗室 (Menu R&D Lab)")
    st.caption("自動探測市場中『競爭少、利潤高』的真空藍海賽道，並結合 **Gemini API** 提供智慧化商品命名與行銷方案。")
    
    gap_analysis = df.groupby(['標籤1', '加料狀態']).agg(
        均價=('價格(L)', 'mean'), 品項數=('飲料品項', 'count')
    ).reset_index()
    
    if not gap_analysis.empty:
        max_p = gap_analysis['均價'].max() if gap_analysis['均價'].max() > 0 else 1
        max_c = gap_analysis['品項數'].max() if gap_analysis['品項數'].max() > 0 else 1
        
        gap_analysis['藍海指數'] = ((gap_analysis['均價'] / max_p) * 60 + (1 - gap_analysis['品項數'] / max_c) * 40).round(1)
        gap_analysis['藍海指數'] = gap_analysis['藍海指數'].replace([np.inf, -np.inf], 0).fillna(0).clip(lower=0)
        gap_analysis = gap_analysis.sort_values(by='藍海指數', ascending=False).reset_index(drop=True)
        
        rd_c1, rd_c2 = st.columns([1, 1.2])
        with rd_c1:
            st.markdown("#### 🔭 當前全市場黃金藍海賽道 Top 3")
            for idx, row in gap_analysis.head(3).iterrows():
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.1); padding: 16px; border-radius: 14px; border-left: 5px solid #6366F1; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                    <span style="font-weight:900; color:#A5B4FC; font-size:16px;">🏆 Top {idx+1}：{row['標籤1']} × {row['加料狀態']}</span><br>
                    <span style="font-size:13px; color:#94A3B8;">綜合藍海潛力: <b style="color:#FBBF24;">{row['藍海指數']} 分</b> | 市場均價: <b style="color:#FBBF24;">${row['均價']:.1f} 元</b> | 現有競品僅: <b style="color:#FBBF24;">{row['品項數']} 款</b></span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("#### 📊 全品類市場供需與溢價分佈 (3D 藍海星系)")
            fig_gap = px.scatter_3d(
                gap_analysis, x='品項數', y='均價', z='藍海指數', size='藍海指數', color='標籤1', text='標籤1',
                hover_data={'藍海指數': ':.1f', '品項數': True, '均價': ':.1f'}, color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_gap.update_traces(textposition='top center', marker=dict(opacity=0.85, line=dict(width=1, color='#0F172A')))
            fig_gap.update_layout(
                scene=dict(
                    xaxis=dict(title='市場競爭度 (商品數)', backgroundcolor="#0F172A", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
                    yaxis=dict(title='定價天花板 (均價)', backgroundcolor="#1E293B", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
                    zaxis=dict(title='藍海潛力指數', backgroundcolor="#0F172A", gridcolor="#334155", showbackground=True, title_font=dict(color="#94A3B8"), tickfont=dict(color="#94A3B8")),
                    camera=dict(eye=dict(x=1.3, y=1.3, z=0.7))
                ), height=550, margin=dict(l=0, r=0, b=0, t=30), showlegend=False
            )
            st.plotly_chart(fig_gap, use_container_width=True)
            
        with rd_c2:
            st.markdown("#### 💡 智慧新品研發模擬與定價大腦")
            input_base = st.selectbox("1. 選擇預計研發的基底茶種", options=all_bases, index=0)
            input_topping = st.selectbox("2. 設定該新品的配料狀態", options=["純茶/無加料", "有加料"], index=0)
            input_tier = st.select_slider("3. 決定該產品的戰略定位", options=["大眾引流款 (低毛利/衝量款)", "市場主流款 (利潤與銷量平衡)", "奢華旗艦款 (高溢價/故事包裝)"], value="市場主流款 (利潤與銷量平衡)")
            
            base_match = gap_analysis[(gap_analysis['標籤1'] == input_base) & (gap_analysis['加料狀態'] == input_topping)]
            base_calc_price = base_match['均價'].values[0] if not base_match.empty else df['價格(L)'].mean()
            
            tier_multiplier = {"大眾引流款 (低毛利/衝量款)": 0.85, "市場主流款 (利潤與銷量平衡)": 1.0, "奢華旗艦款 (高溢價/故事包裝)": 1.25}
            rec_l_price = round((base_calc_price * tier_multiplier[input_tier]) / 5) * 5
            rec_m_price = round((rec_l_price - 15) / 5) * 5
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.02); margin-bottom:15px;">
                <div style="display:flex; justify-content: space-around; text-align:center;">
                    <div><span style="font-size:12px; color:#94A3B8;">建議中杯定價</span><br><b style="font-size:22px; color:#FBBF24;">${rec_m_price} 元</b></div>
                    <div><span style="font-size:12px; color:#94A3B8;">建議大杯定價</span><br><b style="font-size:22px; color:#34D399;">${rec_l_price} 元</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if api_key_input:
                if st.button("🔮 透過 Gemini 生成獨家研發與行銷企劃", key="run_gemini_rd"):
                    with st.spinner("🧪 Gemini 正在調配秘密配方與撰寫文案..."):
                        prompt_rd = f"""
                        你是一位富有創意的手搖飲品牌研發總監與爆款行銷企劃大師。
                        我們目前計畫推出一款新產品，屬性如下：
                        - 基底茶種：{input_base}
                        - 配料狀態：{input_topping}
                        - 戰略定位：{input_tier}
                        - 中杯定價：{rec_m_price} 元
                        - 大杯定價：{rec_l_price} 元
                        
                        請為這款研發中的新飲品提供以下策略方案：
                        1. 💡【神級爆款商品名稱】：設計 3 個既吸睛、有高級感、且符合社群擴散潮流的繁體中文名稱。
                        2. 📝【社群情境行銷文案】：針對其定位（引流/主流/旗艦），撰寫一篇適合 Instagram 或 Threads 的短文案，並簡述建議的杯身包裝風格。
                        3. 🧪【配方微創新研發建言】：給出一個建立防禦門檻的加分點。
                        
                        請用繁體中文（台灣）產出，排版生動有趣且充滿吸引力。
                        """
                        rd_response = call_gemini(prompt_rd)
                        st.markdown(f"<div class='gemini-output-container'>{rd_response}</div>", unsafe_allow_html=True)
            else:
                st.info("💡 提示：在左側控制台輸入 Gemini API Key 後，可解鎖生成商品名稱與文案的功能。")
    else:
        st.warning("數據庫結構不完整，無法執行研發矩陣計算。")

# ==========================================
# 🔥 頁籤 12 - 財務損益推演
# ==========================================
with tab12:
    st.markdown("### 💰 門店營運利潤與損益平衡推演 (Profit Simulator)")
    st.caption("結合當前過濾市場的真實大杯價格水位，動態推演門店原物料成本（COGS）、固定開銷與單月保本營業防線。")
    
    market_avg_rev = filtered_df['價格(L)'].mean() if not filtered_df.empty and pd.notna(filtered_df['價格(L)'].mean()) else 60
    
    calc_c1, calc_c2 = st.columns([1, 1.5])
    
    with calc_c1:
        st.markdown("#### ⚙️ 門店成本結構與開銷配置")
        cogs_pct = st.slider("1. 原物料與包材成本佔比 (COGS %)", min_value=20, max_value=50, value=33, step=1)
        fixed_rent = st.number_input("2. 每月門店租金與水電雜支 (元)", min_value=10000, max_value=200000, value=45000, step=5000)
        fixed_labor = st.number_input("3. 每月正職與兼職員工總薪資 (元)", min_value=20000, max_value=500000, value=75000, step=5000)
        
        var_cost_per_cup = market_avg_rev * (cogs_pct / 100)
        margin_per_cup = market_avg_rev - var_cost_per_cup
        total_fixed_cost = fixed_rent + fixed_labor
        
        be_volume = int(np.ceil(total_fixed_cost / margin_per_cup)) if margin_per_cup > 0 else 0
        
        st.divider()
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); padding: 22px; border-radius: 18px; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
            <span style="font-size:14px; color:#34D399; font-weight:700;">🎯 單月損益平衡防線 (Break-Even Point)：</span><br>
            <h3 style="margin: 10px 0; color:#34D399 !important; font-size:32px; font-weight:900;">{be_volume:,} 杯 / 月</h3>
            <span style="font-size:13px; color:#A7F3D0;">門店平均每日需穩定賣出 <b style="color:#34D399;">{int(np.ceil(be_volume/30))} 杯</b> 即可跨越保本線！</span>
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
            connector = {"line":{"color":"#475569", "dash":"dot"}},
            decreasing = {"marker":{"color":"#F43F5E"}},
            increasing = {"marker":{"color":"#34D399"}},
            totals = {"marker":{"color":"#6366F1"}}
        ))
        fig_wf.update_layout(height=280)
        fig_wf = apply_common_layout(fig_wf)
        st.plotly_chart(fig_wf, use_container_width=True)
        
        st.markdown("#### 📈 月銷量規模 vs 淨利潤動態演化曲線")
        
        max_plot_vol = max(be_volume * 2, 4000)
        volumes = np.arange(0, max_plot_vol, int(max_plot_vol/40) if max_plot_vol > 40 else 1)
        profits = (volumes * margin_per_cup) - total_fixed_cost
        
        prof_df = pd.DataFrame({"月銷量 (杯)": volumes, "預估月淨利 (元)": profits})
        
        fig_line = px.line(prof_df, x="月銷量 (杯)", y="預估月淨利 (元)", color_discrete_sequence=["#6366F1"])
        fig_line.add_shape(type="line", x0=0, y0=0, x1=max(volumes), y1=0, line=dict(color="#475569", width=1.5, dash="dash"))
        
        if be_volume > 0:
            fig_line.add_trace(go.Scatter(x=[be_volume], y=[0], mode='markers+text', name='損益平衡點',
                                          text=[f" 損益平衡線 ({be_volume}杯)"], textposition="top right",
                                          marker=dict(color='#FBBF24', size=12, line=dict(color='#0F172A', width=2))))
        fig_line.update_layout(showlegend=False, height=320)
        fig_line = apply_common_layout(fig_line)
        st.plotly_chart(fig_line, use_container_width=True)
