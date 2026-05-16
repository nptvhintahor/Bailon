import pandas as pd
import sys

# Đảm bảo hiển thị tiếng Việt chuẩn trên Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_full_report_2024(file_path):
    try:
        # 1. Đọc dữ liệu ban đầu
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Chuyển đổi định dạng ngày tháng
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

        # 2. Lọc dữ liệu duy nhất trong năm 2024
        df_2024 = df[df['transaction_date'].dt.year == 2024].copy()
        total_tx_2024 = len(df_2024)

        if df_2024.empty:
            print("Thông báo: Không có dữ liệu giao dịch trong năm 2024.")
            return

        # 3. Phân tích Khách hàng (Làm sạch trùng lặp)
        unique_customers_count = df_2024['customer_id'].nunique()
        duplicate_customer_tx = df_2024.duplicated(subset=['customer_id']).sum()

        # 4. Phân tích Merchant Category
        unique_categories = df_2024['merchant_category'].nunique()
        category_counts = df_2024['merchant_category'].value_counts()
        duplicate_categories = category_counts[category_counts > 1]

        # 5. Phân tích Account Type
        acc_counts = df_2024['account_type'].value_counts()
        unique_acc_types = len(acc_counts)

        # 6. Phân tích Payment Method (Sử dụng cột 'channel')
        method_col = 'channel'
        method_counts = df_2024[method_col].value_counts()
        unique_methods = len(method_counts)
        duplicate_methods = method_counts[method_counts > 1]

        # 7. Phân tích tổ hợp (Account Type + Payment Method)
        combined_stats = df_2024.groupby(['account_type', method_col]).size().reset_index(name='count')
        combined_duplicates = combined_stats[combined_stats['count'] > 1].sort_values(by='count', ascending=False)

        # --- XUẤT BÁO CÁO TỔNG HỢP ---
        print("="*80)
        print(f"{'BÁO CÁO TỔNG LỰC DỮ LIỆU NGÂN HÀNG NĂM 2024':^80}")
        print("="*80)

        # Phần I: Giao dịch & Khách hàng
        print(f"I. GIAO DỊCH & KHÁCH HÀNG")
        print(f"- Tổng số lượt giao dịch trong năm:         {total_tx_2024}")
        print(f"- Số lượt giao dịch bị trùng mã khách hàng: {duplicate_customer_tx}")
        print(f"- TỔNG SỐ KHÁCH HÀNG RIÊNG BIỆT:           {unique_customers_count}")
        print("-" * 80)

        # Phần II: Hạng mục kinh doanh (Merchant Category)
        print(f"II. HẠNG MỤC TIÊU DÙNG (MERCHANT CATEGORY)")
        print(f"- Tổng số loại hình kinh doanh riêng biệt:   {unique_categories}")
        print(f"- Chi tiết các loại hình có giao dịch trùng nhau:")
        for cat, count in duplicate_categories.items():
            print(f"  + {str(cat):<35} | {count} giao dịch")
        print("-" * 80)

        # Phần III: Loại tài khoản & Phương thức thanh toán
        print(f"III. TÀI KHOẢN & PHƯƠNG THỨC THANH TOÁN")
        print(f"1. Tổng số loại tài khoản riêng biệt: {unique_acc_types}")
        for acc, count in acc_counts.items():
            print(f"   + {acc:<20}: {count} giao dịch")
            
        print(f"\n2. Tổng số phương thức thanh toán riêng biệt: {unique_methods}")
        for meth, count in duplicate_methods.items():
            print(f"   + {meth:<20}: {count} giao dịch trùng loại")
        print("-" * 80)

        # Phần IV: Phân tích tổ hợp
        print(f"IV. LOẠI TÀI KHOẢN CÙNG THỰC HIỆN PHƯƠNG THỨC TRÙNG NHAU")
        print(f"{'Loại tài khoản':<25} | {'Phương thức':<15} | {'Số lượng trùng'}")
        print("-" * 80)
        for _, row in combined_duplicates.iterrows():
            print(f"{str(row['account_type']):<25} | {str(row[method_col]):<15} | {row['count']}")
        
        print("="*80)
        print(f"{'KẾT THÚC BÁO CÁO NĂM 2024':^80}")
        print("="*80)

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{file_path}'.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {str(e)}")

if __name__ == "__main__":
    analyze_full_report_2024('indian_banking_transactions.csv')