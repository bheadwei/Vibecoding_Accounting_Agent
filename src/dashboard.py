"""
記帳儀表板 - Streamlit 互動式應用程式
功能：
1. 上傳 Excel 記帳檔案
2. 自動顯示消費統計
3. 互動式圖表（可選擇月份）
4. 簡潔美觀的介面
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# 設定頁面配置
st.set_page_config(
    page_title="記帳儀表板",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    
    /* 統計摘要卡片樣式 - 適配深色和淺色模式 */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* 為每個指標設定不同的漸層色 */
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    /* 深色模式下的標題顏色調整 */
    @media (prefers-color-scheme: dark) {
        h1 {
            color: #4fc3f7;
        }
        h2 {
            color: #e0e0e0;
        }
    }
    </style>
""", unsafe_allow_html=True)


def load_data(uploaded_file):
    """載入並處理 Excel 檔案"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # 確保必要欄位存在
        required_columns = ['日期', '項目', '金額', '類別']
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Excel 檔案必須包含以下欄位：{', '.join(required_columns)}")
            return None
        
        # 轉換日期格式
        df['日期'] = pd.to_datetime(df['日期'])
        df['年月'] = df['日期'].dt.to_period('M').astype(str)
        df['月份'] = df['日期'].dt.month
        df['年份'] = df['日期'].dt.year
        
        return df
    except Exception as e:
        st.error(f"❌ 讀取檔案時發生錯誤：{str(e)}")
        return None


def create_summary_metrics(df):
    """建立統計摘要指標"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_expense = df['金額'].sum()
        st.metric(
            label="💵 總花費",
            value=f"${total_expense:,.0f}",
            delta=None
        )
    
    with col2:
        avg_expense = df['金額'].mean()
        st.metric(
            label="📊 平均花費",
            value=f"${avg_expense:,.0f}",
            delta=None
        )
    
    with col3:
        total_records = len(df)
        st.metric(
            label="📝 總筆數",
            value=f"{total_records}",
            delta=None
        )
    
    with col4:
        category_count = df['類別'].nunique()
        st.metric(
            label="🏷️ 類別數",
            value=f"{category_count}",
            delta=None
        )


def create_category_pie_chart(df):
    """建立類別圓餅圖"""
    category_summary = df.groupby('類別')['金額'].sum().reset_index()
    category_summary = category_summary.sort_values('金額', ascending=False)
    
    fig = px.pie(
        category_summary,
        values='金額',
        names='類別',
        title='各類別花費佔比',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4  # 甜甜圈圖
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>金額: $%{value:,.0f}<br>佔比: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=14),
        showlegend=True,
        height=500
    )
    
    return fig


def create_monthly_trend_chart(df, selected_categories=None):
    """建立每月趨勢圖"""
    if selected_categories:
        df_filtered = df[df['類別'].isin(selected_categories)]
    else:
        df_filtered = df
    
    monthly_summary = df_filtered.groupby('年月')['金額'].sum().reset_index()
    monthly_summary = monthly_summary.sort_values('年月')
    
    fig = px.bar(
        monthly_summary,
        x='年月',
        y='金額',
        title='每月花費趨勢',
        color_discrete_sequence=['#4ECDC4'],
        text='金額'
    )
    
    fig.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>金額: $%{y:,.0f}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title='月份',
        yaxis_title='花費金額 (元)',
        font=dict(size=14),
        height=500,
        showlegend=False
    )
    
    return fig


def create_category_monthly_stacked_chart(df):
    """建立類別月度堆疊圖"""
    pivot_data = df.pivot_table(
        values='金額',
        index='年月',
        columns='類別',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # 轉換為長格式
    df_long = pivot_data.melt(
        id_vars='年月',
        var_name='類別',
        value_name='金額'
    )
    
    fig = px.bar(
        df_long,
        x='年月',
        y='金額',
        color='類別',
        title='各類別每月花費分布',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        barmode='stack'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>類別: %{fullData.name}<br>金額: $%{y:,.0f}<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title='月份',
        yaxis_title='花費金額 (元)',
        font=dict(size=14),
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_top_expenses_table(df, n=10):
    """建立最高花費項目表格"""
    top_expenses = df.nlargest(n, '金額')[['日期', '項目', '類別', '金額']]
    top_expenses['日期'] = top_expenses['日期'].dt.strftime('%Y-%m-%d')
    top_expenses['金額'] = top_expenses['金額'].apply(lambda x: f'${x:,.0f}')
    top_expenses = top_expenses.reset_index(drop=True)
    top_expenses.index = top_expenses.index + 1
    
    return top_expenses


def main():
    """主程式"""
    
    # 標題
    st.title("💰 記帳儀表板")
    st.markdown("---")
    
    # 側邊欄
    with st.sidebar:
        st.header("📂 檔案上傳")
        uploaded_file = st.file_uploader(
            "上傳 Excel 記帳檔案",
            type=['xlsx', 'xls'],
            help="請上傳包含「日期」、「項目」、「金額」、「類別」欄位的 Excel 檔案"
        )
        
        st.markdown("---")
        st.header("ℹ️ 使用說明")
        st.markdown("""
        1. 上傳您的 Excel 記帳檔案
        2. 系統會自動分析並顯示統計資料
        3. 使用篩選器查看特定類別或月份
        4. 所有圖表都可以互動操作
        """)
        
        st.markdown("---")
        st.markdown("**📊 資料格式範例**")
        st.code("""
日期       | 項目 | 金額 | 類別
2024-01-01 | 午餐 | 150  | 餐飲
2024-01-02 | 捷運 | 30   | 交通
        """)
    
    # 主要內容區
    if uploaded_file is not None:
        # 載入資料
        df = load_data(uploaded_file)
        
        if df is not None:
            # 顯示資料概覽
            st.success(f"✅ 成功載入 {len(df)} 筆記帳資料")
            
            # 統計摘要
            st.header("📊 統計摘要")
            create_summary_metrics(df)
            
            st.markdown("---")
            
            # 篩選器
            st.header("🔍 資料篩選")
            col1, col2 = st.columns(2)
            
            with col1:
                # 類別篩選
                all_categories = df['類別'].unique().tolist()
                selected_categories = st.multiselect(
                    "選擇類別",
                    options=all_categories,
                    default=all_categories,
                    help="選擇要顯示的類別"
                )
            
            with col2:
                # 月份篩選
                all_months = sorted(df['年月'].unique().tolist())
                selected_months = st.multiselect(
                    "選擇月份",
                    options=all_months,
                    default=all_months,
                    help="選擇要顯示的月份"
                )
            
            # 根據篩選條件過濾資料
            if selected_categories and selected_months:
                df_filtered = df[
                    (df['類別'].isin(selected_categories)) &
                    (df['年月'].isin(selected_months))
                ]
            else:
                df_filtered = df
            
            if len(df_filtered) == 0:
                st.warning("⚠️ 沒有符合篩選條件的資料")
            else:
                st.info(f"📋 顯示 {len(df_filtered)} 筆資料（共 {len(df)} 筆）")
                
                st.markdown("---")
                
                # 圖表區域
                st.header("📈 視覺化分析")
                
                # 第一排：圓餅圖和趨勢圖
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(
                        create_category_pie_chart(df_filtered),
                        use_container_width=True
                    )
                
                with col2:
                    st.plotly_chart(
                        create_monthly_trend_chart(df_filtered, selected_categories),
                        use_container_width=True
                    )
                
                # 第二排：堆疊圖
                st.plotly_chart(
                    create_category_monthly_stacked_chart(df_filtered),
                    use_container_width=True
                )
                
                st.markdown("---")
                
                # 最高花費項目
                st.header("🔝 最高花費項目 (Top 10)")
                top_expenses = create_top_expenses_table(df_filtered, n=10)
                st.dataframe(
                    top_expenses,
                    use_container_width=True,
                    hide_index=False
                )
                
                st.markdown("---")
                
                # 原始資料預覽
                with st.expander("📋 查看原始資料"):
                    st.dataframe(
                        df_filtered[['日期', '項目', '金額', '類別']].sort_values('日期', ascending=False),
                        use_container_width=True
                    )
                
                # 下載篩選後的資料
                st.markdown("---")
                st.header("💾 下載資料")
                
                # 準備下載資料
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_filtered.to_excel(writer, index=False, sheet_name='篩選資料')
                output.seek(0)
                
                st.download_button(
                    label="📥 下載篩選後的資料 (Excel)",
                    data=output,
                    file_name=f"filtered_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    else:
        # 歡迎畫面
        st.info("👈 請從左側上傳 Excel 記帳檔案開始使用")
        
        # 顯示範例
        st.header("📝 範例資料格式")
        example_data = pd.DataFrame({
            '日期': ['2024-01-01', '2024-01-02', '2024-01-03'],
            '項目': ['午餐', '捷運', '電影'],
            '金額': [150, 30, 280],
            '類別': ['餐飲', '交通', '娛樂']
        })
        st.dataframe(example_data, use_container_width=True)


if __name__ == "__main__":
    main()
