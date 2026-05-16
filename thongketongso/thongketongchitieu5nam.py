import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys

# Đảm bảo hiển thị tiếng Việt mượt mà
sys.stdout.reconfigure(encoding='utf-8')

# Thiết lập đường dẫn file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

try:
    # 1. Xử lý dữ liệu chuyên sâu
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['Year'] = df['transaction_date'].dt.year
    
    # Lọc và tính toán
    data = df[df['Year'].isin([2019, 2020, 2021, 2022, 2023])]
    summary = data.groupby('Year')['transaction_amount'].sum().reset_index()
    
    # Tính % tăng trưởng (YoY Growth)
    summary['growth'] = summary['transaction_amount'].pct_change() * 100

    # 2. Thiết lập giao diện Dark Premium
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 8), facecolor='#121212')
    ax.set_facecolor('#121212')

    # 3. Vẽ biểu đồ Vùng (Area Chart) với Gradient
    x = summary['Year']
    y = summary['transaction_amount']
    
    # Vẽ đường line chính (màu Neon Blue)
    ax.plot(x, y, color='#00d4ff', linewidth=4, marker='o', 
            markersize=10, markerfacecolor='#ffffff', markeredgewidth=3, zorder=5)
    
    # Đổ màu vùng phía dưới (Gradient Fill)
    ax.fill_between(x, y, color='#00d4ff', alpha=0.15, zorder=3)

    # 4. Tùy chỉnh trục và lưới
    ax.grid(color='#2c2c2c', linestyle='--', linewidth=0.5, alpha=0.5, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#2c2c2c')
    ax.spines['bottom'].set_color('#2c2c2c')

    # 5. Thêm Data Labels và Chỉ số tăng trưởng
    for i, row in summary.iterrows():
        # Hiển thị số tiền chính
        ax.annotate(f'{row["transaction_amount"]:,.0f}', 
                    (row['Year'], row['transaction_amount']),
                    textcoords="offset points", xytext=(0, 20),
                    ha='center', fontsize=11, fontweight='bold', color='#ffffff')
        
        # Hiển thị % tăng trưởng (nếu có)
        if not np.isnan(row['growth']):
            color = '#00ff88' if row['growth'] >= 0 else '#ff4444'
            prefix = '+' if row['growth'] >= 0 else ''
            ax.annotate(f'{prefix}{row["growth"]:.1f}% YoY', 
                        (row['Year'], row['transaction_amount']),
                        textcoords="offset points", xytext=(0, -25),
                        ha='center', fontsize=10, color=color, fontweight='600')

    # 6. Tiêu đề và chú thích phong cách Dashboard
    plt.title('BANKING TRANSACTION ANALYSIS REPORT', fontsize=24, fontweight='bold', 
              pad=40, color='#ffffff', loc='left', family='sans-serif')
    
    # Chú thích góc trên bên trái
    ax.text(0, 1.05, f"Period: 2019 - 2023 | Currency: INR | Data Source: Indian Banking Dataset", 
            transform=ax.transAxes, fontsize=11, color='#888888')

    plt.xticks(summary['Year'], fontsize=11, fontweight='bold')
    plt.yticks([]) # Ẩn trục Y để tối giản
    
    plt.tight_layout()
    plt.show()

    # In báo cáo tóm tắt ra Terminal
    print("\n" + "="*50)
    print(" FINANCIAL SUMMARY REPORT (2019-2023) ".center(50, " "))
    print("="*50)
    for _, row in summary.iterrows():
        growth_str = f"({row['growth']:+.1f}%)" if not np.isnan(row['growth']) else "(Baseline)"
        print(f"Năm {int(row['Year'])}: {row['transaction_amount']:15,.0f} INR | Growth: {growth_str}")
    print("="*50)

except Exception as e:
    print(f"Lỗi hệ thống: {e}")