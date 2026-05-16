import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button

# 1. Cấu hình hệ thống và tiếng Việt
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình font để tránh lỗi hiển thị tiếng Việt trên biểu đồ
plt.rcParams['font.family'] = 'Arial' 
sns.set_theme(style="whitegrid")

class BankingVisualizer:
    def __init__(self, df_2020):
        self.df = df_2020
        self.current_slide = 0
        
        # Khởi tạo cửa sổ biểu đồ với kích thước cố định
        self.fig = plt.figure(figsize=(15, 9))
        self.ax = self.fig.add_subplot(111)
        
        # Cố định lề để tránh nhảy khung hình
        plt.subplots_adjust(bottom=0.2, left=0.25, right=0.9, top=0.9)

        # Danh sách các hàm vẽ biểu đồ
        self.slides = [
            self.draw_merchant_slide, 
            self.draw_account_slide, 
            self.draw_method_slide
        ]
        
        # Thiết lập vị trí các nút điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Lùi', color='#f0f0f0', hovercolor='0.95')
        self.btn_next = Button(self.ax_next, 'Tiếp >>', color='#f0f0f0', hovercolor='0.95')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_current_slide()
        plt.show()

    def update_navigation(self):
        """Cập nhật trạng thái hiển thị của các nút"""
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.slides) - 1)
        self.fig.canvas.draw_idle()

    def draw_current_slide(self):
        """Xóa sạch trục và vẽ slide hiện tại"""
        self.ax.clear()
        
        # Xóa các chú thích cũ nếu có
        if self.fig.legends:
            self.fig.legends.clear()
            
        self.slides[self.current_slide]()
        self.update_navigation()

    def next(self, event):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.draw_current_slide()

    def previous(self, event):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.draw_current_slide()

    # --- BIỂU ĐỒ 1: TOP 15 DANH MỤC (2020) ---
    def draw_merchant_slide(self):
        data = self.df['merchant_category'].value_counts().head(15).reset_index()
        data.columns = ['Category', 'Count']
        
        sns.barplot(x='Count', y='Category', data=data, palette='viridis', ax=self.ax)
        self.ax.set_title("1. TOP 15 DANH MỤC KINH DOANH (2020)", fontsize=14, fontweight='bold', pad=20)
        self.ax.set_xlabel("Số lượng giao dịch")
        self.ax.set_ylabel("")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, padding=5, fontsize=9)

    # --- BIỂU ĐỒ 2: 5 LOẠI TÀI KHOẢN (2020) ---
    def draw_account_slide(self):
        data = self.df['account_type'].value_counts().head(5).reset_index()
        data.columns = ['Type', 'Count']
        
        sns.barplot(x='Type', y='Count', data=data, palette='magma', ax=self.ax)
        self.ax.set_title("2. SO SÁNH 5 LOẠI TÀI KHOẢN (2020)", fontsize=14, fontweight='bold', pad=20)
        self.ax.set_ylabel("Số lượng giao dịch")
        self.ax.set_xlabel("Loại tài khoản")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, padding=3, fontsize=10)

    # --- BIỂU ĐỒ 3: 6 PHƯƠNG THỨC THANH TOÁN (2020) ---
    def draw_method_slide(self):
        data = self.df['channel'].value_counts().head(6).reset_index()
        data.columns = ['Method', 'Count']
        
        sns.barplot(x='Method', y='Count', data=data, palette='coolwarm', ax=self.ax)
        self.ax.set_title("3. TỶ LỆ PHƯƠNG THỨC THANH TOÁN (2020)", fontsize=14, fontweight='bold', pad=20)
        self.ax.set_ylabel("Số lượng giao dịch")
        self.ax.set_xlabel("Phương thức")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, padding=3, fontsize=10)

def run_banking_analysis(file_path):
    try:
        # Đọc dữ liệu
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Lọc dữ liệu NĂM 2020
        df_2020 = df[df['transaction_date'].dt.year == 2020].dropna(subset=['transaction_date']).copy()
        
        if df_2020.empty:
            print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2020.")
            return

        BankingVisualizer(df_2020)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{file_path}'")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    run_banking_analysis('indian_banking_transactions.csv')