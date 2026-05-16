import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button

# Cấu hình hiển thị tiếng Việt trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class MoneyVisualizer:
    def __init__(self, df_2023):
        self.df = df_2023
        self.current_slide = 0
        
        # Khởi tạo cửa sổ biểu đồ
        self.fig = plt.figure(figsize=(15, 9))
        self.ax = self.fig.add_subplot(111)
        
        # Điều chỉnh lề để chứa bảng chú thích và nút bấm
        plt.subplots_adjust(bottom=0.2, left=0.25, right=0.85)

        # Danh sách các hàm vẽ biểu đồ dòng tiền
        self.slides = [
            self.draw_amount_by_category, 
            self.draw_amount_by_account, 
            self.draw_amount_by_method
        ]
        
        # Thiết lập nút bấm
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Lùi')
        self.btn_next = Button(self.ax_next, 'Tiếp >>')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_current_slide()
        plt.show()

    def update_navigation(self):
        """Ẩn/Hiện nút bấm theo logic"""
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.slides) - 1)
        self.fig.canvas.draw_idle()

    def draw_current_slide(self):
        self.ax.clear()
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

    # --- BIỂU ĐỒ 1: TỔNG TIỀN THEO 15 HẠNG MỤC (2023) ---
    def draw_amount_by_category(self):
        data = self.df.groupby('merchant_category')['transaction_amount'].sum().reset_index()
        data = data.sort_values(by='transaction_amount', ascending=False).head(15)
        
        sns.barplot(x='transaction_amount', y='merchant_category', data=data, palette='YlOrRd_r', ax=self.ax)
        self.ax.set_title("1. TỔNG TIỀN CHI TIÊU THEO 15 HẠNG MỤC (2023)", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Tổng số tiền")
        self.ax.set_ylabel("")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, fmt='{:,.0f}', padding=5, fontsize=9)

    # --- BIỂU ĐỒ 2: TỔNG TIỀN THEO 5 LOẠI TÀI KHOẢN (2023) ---
    def draw_amount_by_account(self):
        data = self.df.groupby('account_type')['transaction_amount'].sum().reset_index()
        data = data.sort_values(by='transaction_amount', ascending=False).head(5)
        
        sns.barplot(x='account_type', y='transaction_amount', data=data, palette='viridis', ax=self.ax)
        self.ax.set_title("2. TỔNG TIỀN THEO 5 LOẠI TÀI KHOẢN (2023)", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Loại tài khoản")
        self.ax.set_ylabel("Tổng số tiền")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, fmt='{:,.0f}', padding=3, fontsize=10)

    # --- BIỂU ĐỒ 3: TỔNG TIỀN THEO 6 PHƯƠNG THỨC (2023) ---
    def draw_amount_by_method(self):
        data = self.df.groupby('channel')['transaction_amount'].sum().reset_index()
        data = data.sort_values(by='transaction_amount', ascending=False).head(6)
        
        sns.barplot(x='channel', y='transaction_amount', data=data, palette='coolwarm', ax=self.ax)
        self.ax.set_title("3. TỔNG TIỀN THEO 6 PHƯƠNG THỨC THANH TOÁN (2023)", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Phương thức (Channel)")
        self.ax.set_ylabel("Tổng số tiền")
        
        for i in self.ax.containers:
            self.ax.bar_label(i, fmt='{:,.0f}', padding=3, fontsize=10)

def run_money_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # CHUYỂN SANG LẤY DỮ LIỆU NĂM 2023
        df_2023 = df[df['transaction_date'].dt.year == 2023].copy()
        
        if df_2023.empty:
            print("Thông báo: Dữ liệu năm 2023 không tồn tại.")
            return

        MoneyVisualizer(df_2023)
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    run_money_analysis('indian_banking_transactions.csv')