import pandas as pd
import sys

# Cấu hình hiển thị tiếng Việt cho Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_full_report_2021(file_path):
    try:
        # 1. Đọc dữ liệu
        df = pd.read_csv(file_path, encoding='utf-8')
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

        # 2. Lọc dữ liệu năm 2021
        df_2021 = df[df['transaction_date'].dt.year == 2021].copy()
        
        if df_2021.empty:
            print(">>> THÔNG BÁO: Không tìm thấy dữ liệu giao dịch cho năm 2021.")
            return

        total_tx = len(df_2021)

        # 3. Phân tích số liệu
        unique_customers = df_2021['customer_id'].nunique()
        duplicate_customers = df_2021.duplicated(subset=['customer_id']).sum()
        
        category_counts = df_2021['merchant_category'].value_counts()
        acc_counts = df_2021['account_type'].value_counts()
        method_counts = df_2021['channel'].value_counts()
        
        # Phân tích tổ hợp (Account Type + Channel)
        combined_stats = df_2021.groupby(['account_type', 'channel']).size().reset_index(name='count')
        combined_stats = combined_stats.sort_values(by='count', ascending=False)

        # --- XUẤT BÁO CÁO CHI TIẾT 2021 ---
        print("="*95)
        print(f"{'BÁO CÁO TỔNG LỰC DỮ LIỆU NGÂN HÀNG NĂM 2021 (FULL)':^95}")
        print("="*95)

        # PHẦN I: Quy mô
        print(f"I. THỐNG KÊ QUY MÔ GIAO DỊCH & KHÁCH HÀNG 2021")
        print(f"  - Tổng số lượt giao dịch thực hiện:   {total_tx:,}")
        print(f"  - Tổng số khách hàng riêng biệt:     {unique_customers:,}")
        print(f"  - Số lượt khách quay lại giao dịch:   {duplicate_customers:,}")
        print("-" * 95)

        # PHẦN II: Merchant Category
        print(f"II. CHI TIẾT HẠNG MỤC TIÊU DÙNG (MERCHANT CATEGORY) - 2021")
        print(f"  {'Hạng mục kinh doanh':<50} | {'Số lượng giao dịch':<20}")
        print(f"  {'-'*49} | {'-'*20}")
        for cat, count in category_counts.items():
            print(f"  {str(cat):<50} | {count:,}")
        print("-" * 95)

        # PHẦN III & IV: Cơ cấu
        print(f"III. CƠ CẤU LOẠI TÀI KHOẢN (2021)")
        for acc, count in acc_counts.items():
            percentage = (count / total_tx) * 100
            print(f"  + {acc:<25}: {count:,} GD ({percentage:.2f}%)")
        
        print(f"\nIV. CƠ CẤU PHƯƠNG THỨC THANH TOÁN (2021)")
        for meth, count in method_counts.items():
            percentage = (count / total_tx) * 100
            print(f"  + {meth:<25}: {count:,} GD ({percentage:.2f}%)")
        print("-" * 95)

        # PHẦN V: Tổ hợp chi tiết
        print(f"V. TOÀN BỘ TỔ HỢP TÀI KHOẢN & KÊNH GIAO DỊCH (2021)")
        print(f"  {'Loại tài khoản':<35} | {'Phương thức':<25} | {'Số lượng GD'}")
        print(f"  {'-'*34} | {'-'*24} | {'-'*15}")
        for _, row in combined_stats.iterrows():
            print(f"  {str(row['account_type']):<35} | {str(row['channel']):<25} | {row['count']:,}")

        print("="*95)
        print(f"{'KẾT THÚC BÁO CÁO NĂM 2021':^95}")
        print("="*95)

    except Exception as e:
        print(f">>> LỖI HỆ THỐNG: {e}")

if __name__ == "__main__":
    analyze_full_report_2021('indian_banking_transactions.csv')