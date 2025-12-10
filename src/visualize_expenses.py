"""
記帳資料視覺化程式
功能：
1. 讀取分析結果 Excel 檔案
2. 繪製圓餅圖顯示各類別佔比
3. 繪製長條圖顯示每月花費趨勢
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.font_manager as fm

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題


def create_category_pie_chart(df, output_path):
    """
    建立類別花費圓餅圖
    
    參數:
        df (DataFrame): 原始記帳資料
        output_path (Path): 輸出圖片路徑
    """
    # 計算各類別總花費
    category_summary = df.groupby('類別')['金額'].sum().sort_values(ascending=False)
    
    # 設定美觀的配色方案（使用柔和的現代色彩）
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', 
              '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
    
    # 建立圓餅圖
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(
        category_summary.values,
        labels=category_summary.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(category_summary)],
        textprops={'fontsize': 12, 'weight': 'bold'},
        explode=[0.05] * len(category_summary)  # 讓每個扇形稍微分開
    )
    
    # 設定百分比文字顏色為白色，更清晰
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
    
    plt.title('各類別花費佔比分析', fontsize=18, weight='bold', pad=20)
    
    # 加入圖例，顯示實際金額
    legend_labels = [f'{cat}: ${amount:,.0f}' for cat, amount in category_summary.items()]
    plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 圓餅圖已儲存至: {output_path}")
    plt.close()


def create_monthly_trend_chart(df, output_path):
    """
    建立每月花費趨勢長條圖
    
    參數:
        df (DataFrame): 原始記帳資料
        output_path (Path): 輸出圖片路徑
    """
    # 確保日期欄位是 datetime 格式
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 提取年月
    df['年月'] = df['日期'].dt.to_period('M')
    
    # 計算每月總花費
    monthly_summary = df.groupby('年月')['金額'].sum().sort_index()
    
    # 轉換為字串格式以便顯示
    monthly_labels = [str(period) for period in monthly_summary.index]
    
    # 建立長條圖
    plt.figure(figsize=(14, 7))
    bars = plt.bar(
        range(len(monthly_summary)),
        monthly_summary.values,
        color='#4ECDC4',
        edgecolor='#2C3E50',
        linewidth=1.5,
        alpha=0.85
    )
    
    # 在每個長條上方顯示金額
    for i, (bar, value) in enumerate(zip(bars, monthly_summary.values)):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'${value:,.0f}',
            ha='center',
            va='bottom',
            fontsize=9,
            weight='bold'
        )
    
    plt.xlabel('月份', fontsize=14, weight='bold')
    plt.ylabel('花費金額 (元)', fontsize=14, weight='bold')
    plt.title('每月花費趨勢分析', fontsize=18, weight='bold', pad=20)
    
    # 設定 x 軸標籤
    plt.xticks(range(len(monthly_labels)), monthly_labels, rotation=45, ha='right')
    
    # 加入網格線
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 設定 y 軸格式
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 長條圖已儲存至: {output_path}")
    plt.close()


def create_category_monthly_trend_chart(df, output_path):
    """
    建立各類別每月花費堆疊長條圖（額外圖表）
    
    參數:
        df (DataFrame): 原始記帳資料
        output_path (Path): 輸出圖片路徑
    """
    # 確保日期欄位是 datetime 格式
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M')
    
    # 建立透視表：月份 x 類別
    pivot_data = df.pivot_table(
        values='金額',
        index='年月',
        columns='類別',
        aggfunc='sum',
        fill_value=0
    )
    
    # 排序
    pivot_data = pivot_data.sort_index()
    
    # 設定配色
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
    
    # 建立堆疊長條圖
    plt.figure(figsize=(14, 7))
    pivot_data.plot(
        kind='bar',
        stacked=True,
        color=colors[:len(pivot_data.columns)],
        edgecolor='white',
        linewidth=1,
        alpha=0.85,
        figsize=(14, 7)
    )
    
    plt.xlabel('月份', fontsize=14, weight='bold')
    plt.ylabel('花費金額 (元)', fontsize=14, weight='bold')
    plt.title('各類別每月花費趨勢（堆疊圖）', fontsize=18, weight='bold', pad=20)
    
    # 設定 x 軸標籤
    plt.xticks(rotation=45, ha='right')
    
    # 設定圖例
    plt.legend(title='類別', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    # 加入網格線
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 設定 y 軸格式
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 堆疊長條圖已儲存至: {output_path}")
    plt.close()


def main():
    """主程式"""
    # 設定檔案路徑
    project_root = Path(__file__).parent.parent
    
    # 輸入檔案
    input_file = project_root / 'data' / 'project_1_with_fake_data.xlsx'
    
    # 輸出圖片路徑
    output_dir = project_root / 'data' / 'charts'
    output_dir.mkdir(exist_ok=True)
    
    pie_chart_path = output_dir / 'category_pie_chart.png'
    bar_chart_path = output_dir / 'monthly_trend_chart.png'
    stacked_chart_path = output_dir / 'category_monthly_stacked_chart.png'
    
    # 確認輸入檔案存在
    if not input_file.exists():
        print(f"錯誤: 找不到輸入檔案 {input_file}")
        return
    
    try:
        # 讀取原始資料
        print(f"正在讀取檔案: {input_file}")
        df = pd.read_excel(input_file)
        
        print(f"\n總共有 {len(df)} 筆記帳資料")
        print(f"日期範圍: {df['日期'].min()} 至 {df['日期'].max()}")
        
        # 建立圓餅圖
        print("\n正在繪製圓餅圖...")
        create_category_pie_chart(df, pie_chart_path)
        
        # 建立長條圖
        print("\n正在繪製每月趨勢長條圖...")
        create_monthly_trend_chart(df, bar_chart_path)
        
        # 建立堆疊長條圖（額外圖表）
        print("\n正在繪製各類別每月堆疊圖...")
        create_category_monthly_trend_chart(df, stacked_chart_path)
        
        print("\n" + "="*60)
        print("視覺化完成！")
        print("="*60)
        print(f"圖表已儲存至: {output_dir}")
        print(f"  1. 類別佔比圓餅圖: {pie_chart_path.name}")
        print(f"  2. 每月趨勢長條圖: {bar_chart_path.name}")
        print(f"  3. 類別月度堆疊圖: {stacked_chart_path.name}")
        print("="*60)
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
