import pandas as pd
import sys

# Cấu hình hiển thị tiếng Việt cho Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_full_report_2020_complete(file_path):
    try:
        # 1. Đọc dữ liệu
        df = pd.read_csv(file_path, encoding='utf-8')
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

        # 2. Lọc dữ liệu năm 2020
        df_2020 = df[df['transaction_date'].dt.year == 2020].copy()
        
        if df_2020.empty:
            print(">>> THÔNG BÁO: Không có dữ liệu giao dịch trong năm 2020.")
            return

        total_tx = len(df_2020)

        # 3. Phân tích chi tiết
        unique_customers = df_2020['customer_id'].nunique()
        duplicate_customers = df_2020.duplicated(subset=['customer_id']).sum()
        
        category_counts = df_2020['merchant_category'].value_counts()
        acc_counts = df_2020['account_type'].value_counts()
        method_counts = df_2020['channel'].value_counts()
        
        # Phân tích tổ hợp (Account Type + Channel)
        combined_stats = df_2020.groupby(['account_type', 'channel']).size().reset_index(name='count')
        combined_stats = combined_stats.sort_values(by='count', ascending=False)

        # --- XUẤT BÁO CÁO CHI TIẾT ---
        print("="*90)
        print(f"{'BÁO CÁO TỔNG LỰC DỮ LIỆU NGÂN HÀNG NĂM 2020 (FULL)':^90}")
        print("="*90)

        # PHẦN I
        print(f"I. THỐNG KÊ GIAO DỊCH & KHÁCH HÀNG")
        print(f"  - Tổng số lượt giao dịch:          {total_tx:,}")
        print(f"  - Tổng số khách hàng riêng biệt:   {unique_customers:,}")
        print(f"  - Số lượt khách quay lại giao dịch: {duplicate_customers:,}")
        print("-" * 90)

        # PHẦN II
        print(f"II. CHI TIẾT HẠNG MỤC TIÊU DÙNG (MERCHANT CATEGORY)")
        print(f"  {'Hạng mục':<45} | {'Số lượng giao dịch':<20}")
        print(f"  {'-'*44} | {'-'*20}")
        for cat, count in category_counts.items():
            print(f"  {str(cat):<45} | {count:,}")
        print("-" * 90)

        # PHẦN III
        print(f"III. CƠ CẤU LOẠI TÀI KHOẢN")
        for acc, count in acc_counts.items():
            percentage = (count / total_tx) * 100
            print(f"  + {acc:<25}: {count:,} GD ({percentage:.2f}%)")
        
        print(f"\nIV. CƠ CẤU PHƯƠNG THỨC THANH TOÁN (CHANNEL)")
        for meth, count in method_counts.items():
            percentage = (count / total_tx) * 100
            print(f"  + {meth:<25}: {count:,} GD ({percentage:.2f}%)")
        print("-" * 90)

        # PHẦN V
        print(f"V. TOÀN BỘ TỔ HỢP TÀI KHOẢN & PHƯƠNG THỨC THANH TOÁN")
        print(f"  {'Loại tài khoản':<30} | {'Phương thức':<20} | {'Số lượng GD'}")
        print(f"  {'-'*29} | {'-'*19} | {'-'*15}")
        for _, row in combined_stats.iterrows():
            print(f"  {str(row['account_type']):<30} | {str(row['channel']):<20} | {row['count']:,}")

        print("="*90)
        print(f"{'KẾT THÚC BÁO CÁO CHI TIẾT NĂM 2020':^90}")
        print("="*90)

    except Exception as e:
        print(f">>> LỖI: {e}")

if __name__ == "__main__":
    analyze_full_report_2020_complete('indian_banking_transactions.csv')