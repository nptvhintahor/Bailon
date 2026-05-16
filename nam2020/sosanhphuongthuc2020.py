import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.legend as mlegend
import seaborn as sns
from matplotlib.widgets import Button

# 1. Cấu hình hiển thị tiếng Việt trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình font để tránh lỗi hiển thị tiếng Việt
plt.rcParams['font.family'] = 'Arial'
sns.set_theme(style="whitegrid")

class CategoryComparisonVisualizer:
    def __init__(self, df_2020):
        self.df = df_2020
        self.current_slide = 0
        
        # Lấy danh sách Top 15 danh mục chi tiêu của năm 2020
        self.top_15_cats = self.df['merchant_category'].value_counts().head(15).index
        self.df_sub = self.df[self.df['merchant_category'].isin(self.top_15_cats)]
        
        # Khởi tạo cửa sổ
        self.fig = plt.figure(figsize=(15, 10))
        self.ax = self.fig.add_subplot(111)
        
        # Chừa lề rộng bên trái (0.3) cho tên danh mục và bên phải (0.75) cho chú thích
        plt.subplots_adjust(bottom=0.2, right=0.75, left=0.3)

        self.slides = [self.draw_cat_vs_account, self.draw_cat_vs_method]
        
        # Cấu hình các nút điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Biểu đồ 4', color='#f0f0f0', hovercolor='0.95')
        self.btn_next = Button(self.ax_next, 'Biểu đồ 5 >>', color='#f0f0f0', hovercolor='0.95')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_current_slide()
        plt.show()

    def draw_current_slide(self):
        """Dọn dẹp và vẽ lại slide hiện tại"""
        self.ax.clear()
        
        # Xóa các Legend cũ để tránh bị chồng hình khi lùi trang
        if self.ax.get_legend():
            self.ax.get_legend().remove()
            
        for child in self.fig.get_children():
            if isinstance(child, mlegend.Legend):
                child.remove()
        
        # Vẽ nội dung slide mới
        self.slides[self.current_slide]()
        
        # Cập nhật trạng thái ẩn/hiện nút
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
        """Biểu đồ 4: Hạng mục chi tiêu vs Loại tài khoản (2020)"""
        pivot = self.df_sub.groupby(['merchant_category', 'account_type']).size().unstack().fillna(0)
        # Sử dụng colormap đa dạng để phân biệt các loại tài khoản
        pivot.plot(kind='barh', stacked=True, ax=self.ax, colormap='Set3')
        
        self.ax.set_title("BIỂU ĐỒ 4: PHÂN TÍCH LOẠI TÀI KHOẢN THEO HẠNG MỤC (2020)", fontsize=14, fontweight='bold', pad=20)
        self.ax.legend(title="Loại tài khoản", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
        self.ax.set_ylabel("")
        self.ax.set_xlabel("Số lượng giao dịch")

    def draw_cat_vs_method(self):
        """Biểu đồ 5: Hạng mục chi tiêu vs Phương thức thanh toán (2020)"""
        pivot = self.df_sub.groupby(['merchant_category', 'channel']).size().unstack().fillna(0)
        pivot.plot(kind='barh', stacked=True, ax=self.ax, colormap='tab20')
        
        self.ax.set_title("BIỂU ĐỒ 5: PHÂN TÍCH PHƯƠNG THỨC THANH TOÁN THEO HẠNG MỤC (2020)", fontsize=14, fontweight='bold', pad=20)
        self.ax.legend(title="Phương thức (Channel)", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
        self.ax.set_ylabel("")
        self.ax.set_xlabel("Số lượng giao dịch")

def run_analysis(file_path):
    try:
        # Đọc dữ liệu
        df = pd.read_csv(file_path)
        
        # Chuyển đổi ngày tháng và xử lý lỗi nếu có
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Lọc dữ liệu năm 2020
        df_2020 = df[df['transaction_date'].dt.year == 2020].dropna(subset=['transaction_date']).copy()
        
        if df_2020.empty:
            print("Thông báo: Dữ liệu năm 2020 không tồn tại hoặc bị trống.")
            return

        # Khởi chạy giao diện trực quan hóa
        CategoryComparisonVisualizer(df_2020)
        
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{file_path}'. Vui lòng kiểm tra lại tên file.")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    # Thay đổi đường dẫn file nếu cần thiết
    run_analysis('indian_banking_transactions.csv')