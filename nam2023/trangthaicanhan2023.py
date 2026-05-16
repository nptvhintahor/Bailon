import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button

# Cấu hình hiển thị tiếng Việt trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình font để tránh lỗi hiển thị tiếng Việt trên biểu đồ
plt.rcParams['font.family'] = 'Arial'

class BankingDashboard:
    def __init__(self, file_path):
        try:
            # 1. Đọc và lọc dữ liệu năm 2023
            df = pd.read_csv(file_path)
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            
            # LẤY DỮ LIỆU NĂM 2023
            self.df_2023 = df[df['transaction_date'].dt.year == 2023].dropna(subset=['transaction_date']).copy()
            
            if self.df_2023.empty:
                print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2023!")
                return

            self.current_slide = 0
            
            # Danh sách các slide phân tích năm 2023
            self.slides = [
                self.draw_kyc_fraud_comparison, # Trang 1: Tổng quan KYC & Rủi ro
                self.draw_account_kyc_stats,     # Trang 2: Loại tài khoản vs KYC
                self.draw_channel_kyc_stats      # Trang 3: Phương thức vs KYC
            ]
            
            self.fig = plt.figure(figsize=(16, 9))
            self.setup_ui()
            self.draw_current_slide()
            plt.show()

        except Exception as e:
            print(f"Lỗi khởi tạo: {e}")

    def setup_ui(self):
        """Thiết lập giao diện nút bấm và khung chứa biểu đồ"""
        self.fig.clf()
        self.fig.subplots_adjust(bottom=0.2, left=0.1, right=0.9, top=0.88)

        # Tạo các nút điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Lùi lại', color='#f0f0f0', hovercolor='lightblue')
        self.btn_next = Button(self.ax_next, 'Chuyển tiếp >>', color='#f0f0f0', hovercolor='lightblue')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

    def draw_current_slide(self):
        self.setup_ui()
        self.slides[self.current_slide]()
        
        # Ẩn/Hiện nút thông minh
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.slides) - 1)
        
        # Ghi chú số trang
        plt.figtext(0.5, 0.13, f"Trang {self.current_slide + 1} / {len(self.slides)}", 
                    ha="center", fontweight='bold', bbox={"facecolor":"blue", "alpha":0.1, "pad":5})
        
        self.fig.canvas.draw_idle()

    def next(self, event):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.draw_current_slide()

    def previous(self, event):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.draw_current_slide()

    # --- TRANG 1: TỶ LỆ KYC & TƯƠNG QUAN LỪA ĐẢO (2023) ---
    def draw_kyc_fraud_comparison(self):
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        
        # Pie Chart
        kyc_counts = self.df_2023['kyc_status'].value_counts()
        ax1.pie(kyc_counts, labels=kyc_counts.index, autopct='%1.1f%%', startangle=140, 
                colors=['#27AE60', '#F1C40F', '#E67E22'], shadow=True, textprops={'fontweight': 'bold'})
        ax1.set_title("1. PHÂN BỔ TRẠNG THÁI KYC (2023)", fontweight='bold', pad=20)

        # Grouped Bar
        fraud_kyc = pd.crosstab(self.df_2023['kyc_status'], self.df_2023['is_fraud'])
        # Đảm bảo có đủ 2 cột ngay cả khi không có lừa đảo
        if 0 not in fraud_kyc.columns: fraud_kyc[0] = 0
        if 1 not in fraud_kyc.columns: fraud_kyc[1] = 0
        
        fraud_kyc = fraud_kyc[[0, 1]]
        fraud_kyc.columns = ['An toàn', 'Lừa đảo']
        fraud_kyc.plot(kind='bar', ax=ax2, color=['#2ECC71', '#C0392B'], edgecolor='black', alpha=0.8)
        for container in ax2.containers: 
            ax2.bar_label(container, fmt='{:,.0f}', padding=3, fontweight='bold')
        
        ax2.set_title("2. KYC VS LỪA ĐẢO (2023)", fontweight='bold', pad=20)
        plt.suptitle("PHÂN TÍCH TƯƠNG QUAN ĐỊNH DANH (KYC) VÀ RỦI RO GIAO DỊCH NĂM 2023", 
                     fontsize=18, fontweight='bold', color='#1A5276')

    # --- TRANG 2: LOẠI TÀI KHOẢN VS KYC (2023) ---
    def draw_account_kyc_stats(self):
        ax = self.fig.add_subplot(111)
        acc_kyc = pd.crosstab(self.df_2023['account_type'], self.df_2023['kyc_status'])
        
        cols = [c for c in ['Verified', 'Pending', 'Expired'] if c in acc_kyc.columns]
        acc_kyc[cols].plot(kind='bar', ax=ax, stacked=True, color=['#27AE60', '#F1C40F', '#E67E22'], alpha=0.8)
        
        ax.set_title("THỐNG KÊ KYC TRÊN CÁC LOẠI HÌNH TÀI KHOẢN (2023)", fontsize=15, fontweight='bold', pad=20)
        ax.set_xlabel("Loại hình tài khoản")
        ax.set_ylabel("Số lượng giao dịch")
        ax.legend(title="Trạng thái KYC")
        plt.xticks(rotation=0)

    # --- TRANG 3: PHƯƠNG THỨC THANH TOÁN VS KYC (2023) ---
    def draw_channel_kyc_stats(self):
        ax = self.fig.add_subplot(111)
        chan_kyc = pd.crosstab(self.df_2023['channel'], self.df_2023['kyc_status'])
        
        cols = [c for c in ['Verified', 'Pending', 'Expired'] if c in chan_kyc.columns]
        chan_kyc[cols].plot(kind='barh', ax=ax, stacked=True, color=['#27AE60', '#F1C40F', '#E67E22'], alpha=0.8)
        
        ax.set_title("THỐNG KÊ KYC TRÊN CÁC PHƯƠNG THỨC THANH TOÁN (2023)", fontsize=15, fontweight='bold', pad=20)
        ax.set_xlabel("Số lượng giao dịch")
        ax.set_ylabel("Kênh giao dịch (Channel)")
        ax.legend(title="Trạng thái KYC")

if __name__ == "__main__":
    BankingDashboard('indian_banking_transactions.csv')