"""
記帳分析程式
功能：
1. 讀取 Excel 記帳檔案
2. 計算每個類別的總花費
3. 找出花最多錢的類別
4. 輸出分析結果到新的 Excel 檔案
"""

import pandas as pd
from pathlib import Path


def analyze_expenses(input_file, output_file):
    """
    分析記帳資料並輸出結果
    
    參數:
        input_file (str): 輸入的 Excel 檔案路徑
        output_file (str): 輸出的 Excel 檔案路徑
    """
    
    # 1. 讀取 Excel 檔案
    print(f"正在讀取檔案: {input_file}")
    df = pd.read_excel(input_file)
    
    # 顯示原始資料的前幾筆
    print("\n原始資料預覽:")
    print(df.head())
    print(f"\n總共有 {len(df)} 筆記帳資料")
    
    # 2. 計算每個類別的總花費
    print("\n計算每個類別的總花費...")
    category_summary = df.groupby('類別')['金額'].agg([
        ('總花費', 'sum'),
        ('筆數', 'count'),
        ('平均花費', 'mean')
    ]).round(2)
    
    # 按總花費降序排列
    category_summary = category_summary.sort_values('總花費', ascending=False)
    
    print("\n各類別花費統計:")
    print(category_summary)
    
    # 3. 找出花最多錢的類別
    max_category = category_summary.index[0]
    max_amount = category_summary.loc[max_category, '總花費']
    
    print(f"\n花費最多的類別: {max_category}")
    print(f"總金額: ${max_amount:,.2f}")
    
    # 4. 輸出成新的 Excel
    print(f"\n正在輸出結果到: {output_file}")
    
    # 建立一個 Excel writer 物件
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 工作表1: 原始資料
        df.to_excel(writer, sheet_name='原始資料', index=False)
        
        # 工作表2: 類別統計
        category_summary.to_excel(writer, sheet_name='類別統計')
        
        # 工作表3: 最高花費類別
        max_spending_df = pd.DataFrame({
            '花費最多的類別': [max_category],
            '總金額': [max_amount],
            '筆數': [category_summary.loc[max_category, '筆數']],
            '平均花費': [category_summary.loc[max_category, '平均花費']]
        })
        max_spending_df.to_excel(writer, sheet_name='最高花費', index=False)
    
    print(f"\n✓ 分析完成！結果已儲存至: {output_file}")
    
    return category_summary, max_category, max_amount


def main():
    """主程式"""
    # 設定檔案路徑
    # 取得專案根目錄
    project_root = Path(__file__).parent.parent
    
    input_file = project_root / 'data' / 'project_1_with_fake_data.xlsx'
    output_file = project_root / 'data' / 'expense_analysis_result.xlsx'
    
    # 確認輸入檔案存在
    if not input_file.exists():
        print(f"錯誤: 找不到輸入檔案 {input_file}")
        return
    
    # 執行分析
    try:
        category_summary, max_category, max_amount = analyze_expenses(
            str(input_file), 
            str(output_file)
        )
        
        print("\n" + "="*50)
        print("分析摘要")
        print("="*50)
        print(f"總類別數: {len(category_summary)}")
        print(f"花費最多的類別: {max_category} (${max_amount:,.2f})")
        print("="*50)
        
    except Exception as e:
        print(f"執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
