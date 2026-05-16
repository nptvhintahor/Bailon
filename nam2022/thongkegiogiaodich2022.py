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

class TimeAnalysisVisualizer2022:
    def __init__(self, df_2022):
        self.df = df_2022
        self.current_slide = 0
        
        # Đảm bảo có cột giờ giao dịch (giả định cột này đã tồn tại hoặc cần trích xuất)
        if 'transaction_hour' not in self.df.columns:
            self.df['transaction_hour'] = self.df['transaction_date'].dt.hour
            
        # Danh sách slide phân tích thời gian cho năm 2022
        self.slides = [
            self.draw_hourly_distribution, # Biểu đồ 1
            self.draw_monthly_hourly_heatmap # Biểu đồ 2
        ]
        
        self.fig = plt.figure(figsize=(15, 8))
        self.setup_ui()
        self.draw_current_slide()
        plt.show()

    def setup_ui(self):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(bottom=0.2, left=0.1, right=0.9, top=0.9)

        # Nút điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        self.btn_prev = Button(self.ax_prev, '<< Lùi', color='#f0f0f0', hovercolor='lightblue')
        self.btn_next = Button(self.ax_next, 'Tiếp >>', color='#f0f0f0', hovercolor='lightblue')
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

    def draw_current_slide(self):
        self.setup_ui()
        self.slides[self.current_slide]()
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

    # --- BIỂU ĐỒ 1: TỔNG QUAN GIỜ GIAO DỊCH TRONG NĂM 2022 ---
    def draw_hourly_distribution(self):
        hourly_counts = self.df['transaction_hour'].value_counts().sort_index()
        
        # Sử dụng gradient màu để nhấn mạnh các khung giờ cao điểm
        colors = sns.color_palette("YlOrRd", len(hourly_counts))
        
        self.ax.bar(hourly_counts.index, hourly_counts.values, color=colors, edgecolor='black', alpha=0.8)
        
        self.ax.set_xticks(range(0, 24))
        self.ax.set_title("1. PHÂN BỔ SỐ LƯỢNG GIAO DỊCH THEO KHUNG GIỜ (2022)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_xlabel("Giờ trong ngày (0h - 23h)", fontsize=12)
        self.ax.set_ylabel("Số lượng giao dịch", fontsize=12)
        
        # Ghi chú giờ có giao dịch nhiều nhất
        if not hourly_counts.empty:
            max_hour = hourly_counts.idxmax()
            max_val = hourly_counts.max()
            self.ax.annotate(f'Cao điểm: {max_hour}h\n({max_val:,.0f} GD)', 
                             xy=(max_hour, max_val), xytext=(max_hour+2, max_val),
                             arrowprops=dict(facecolor='black', shrink=0.05),
                             fontsize=10, fontweight='bold', color='red')

    # --- BIỂU ĐỒ 2: HEATMAP THÁNG VS GIỜ (2022) ---
    def draw_monthly_hourly_heatmap(self):
        self.df['Month'] = self.df['transaction_date'].dt.month
        
        # Tạo bảng chéo (Pivot table) giữa Tháng và Giờ
        heatmap_data = pd.crosstab(self.df['Month'], self.df['transaction_hour'])
        
        # Vẽ bản đồ nhiệt
        sns.heatmap(heatmap_data, annot=False, cmap="YlGnBu", ax=self.ax, cbar_kws={'label': 'Số lượng giao dịch'})
        
        self.ax.set_title("2. BIỂU ĐỒ TƯƠNG QUAN GIỮA THÁNG VÀ GIỜ GIAO DỊCH (2022)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_xlabel("Giờ trong ngày", fontsize=12)
        self.ax.set_ylabel("Tháng trong năm", fontsize=12)
        
        # Cập nhật nhãn tháng dựa trên dữ liệu thực tế có trong năm 2022
        present_months = sorted(self.df['Month'].unique())
        self.ax.set_yticklabels([f"Tháng {int(m)}" for m in present_months], rotation=0)

def run_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # LỌC DỮ LIỆU NĂM 2022
        df_2022 = df[df['transaction_date'].dt.year == 2022].dropna(subset=['transaction_date']).copy()
        
        if df_2022.empty:
            print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2022.")
            return

        print(f">>> Đang khởi chạy phân tích thời gian cho {len(df_2022):,} giao dịch năm 2022...")
        TimeAnalysisVisualizer2022(df_2022)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    run_analysis('indian_banking_transactions.csv')