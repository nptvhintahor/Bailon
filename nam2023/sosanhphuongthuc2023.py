import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.legend as mlegend
import seaborn as sns
from matplotlib.widgets import Button

# Cấu hình hiển thị tiếng Việt trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class CategoryComparisonVisualizer:
    def __init__(self, df_2019):
        self.df = df_2019
        self.current_slide = 0
        
        # Lấy danh sách Top 15 danh mục chi tiêu để dùng chung cho cả 2 biểu đồ
        self.top_15_cats = self.df['merchant_category'].value_counts().head(15).index
        self.df_sub = self.df[self.df['merchant_category'].isin(self.top_15_cats)]
        
        # Khởi tạo cửa sổ
        self.fig = plt.figure(figsize=(15, 10))
        self.ax = self.fig.add_subplot(111)
        
        # Chừa lề rộng bên trái (0.3) cho tên danh mục và bên phải cho chú thích
        plt.subplots_adjust(bottom=0.2, right=0.75, left=0.3)

        self.slides = [self.draw_cat_vs_account, self.draw_cat_vs_method]
        
        # Nút bấm
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        self.btn_prev = Button(self.ax_prev, '<< Biểu đồ 4')
        self.btn_next = Button(self.ax_next, 'Biểu đồ 5 >>')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_current_slide()
        plt.show()

    def draw_current_slide(self):
        self.ax.clear()
        # Xóa Legend cũ
        for child in self.fig.get_children():
            if isinstance(child, mlegend.Legend):
                child.remove()
        
        self.slides[self.current_slide]()
        
        # Ẩn hiện nút
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.slides) - 1)
        
        self.fig.canvas.draw_idle()

    def next(self, event):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.draw_current_slide()

    def previous(self, event):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.draw_current_slide()

    def draw_cat_vs_account(self):
        """Biểu đồ 4: Hạng mục chi tiêu vs Loại tài khoản"""
        pivot = self.df_sub.groupby(['merchant_category', 'account_type']).size().unstack().fillna(0)
        pivot.plot(kind='barh', stacked=True, ax=self.ax, colormap='Set3')
        self.ax.set_title("BIỂU ĐỒ 4: PHÂN TÍCH LOẠI TÀI KHOẢN THEO HẠNG MỤC (2019)", fontsize=14, fontweight='bold')
        self.ax.legend(title="Loại tài khoản", loc="center left", bbox_to_anchor=(1, 0.5))
        self.ax.set_ylabel("")
        self.ax.set_xlabel("Số lượng giao dịch")

    def draw_cat_vs_method(self):
        """Biểu đồ 5: Hạng mục chi tiêu vs Phương thức thanh toán"""
        pivot = self.df_sub.groupby(['merchant_category', 'channel']).size().unstack().fillna(0)
        pivot.plot(kind='barh', stacked=True, ax=self.ax, colormap='tab20')
        self.ax.set_title("BIỂU ĐỒ 5: PHÂN TÍCH PHƯƠNG THỨC THANH TOÁN THEO HẠNG MỤC (2019)", fontsize=14, fontweight='bold')
        self.ax.legend(title="Phương thức (Channel)", loc="center left", bbox_to_anchor=(1, 0.5))
        self.ax.set_ylabel("")
        self.ax.set_xlabel("Số lượng giao dịch")

def run_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df_2019 = df[df['transaction_date'].dt.year == 2019].copy()
        
        if df_2019.empty:
            print("Dữ liệu năm 2019 trống.")
            return

        CategoryComparisonVisualizer(df_2019)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    # Đảm bảo file CSV nằm cùng thư mục hoặc ghi đúng đường dẫn
    run_analysis('indian_banking_transactions.csv')