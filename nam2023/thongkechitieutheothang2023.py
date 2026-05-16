import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button

# Cấu hình hiển thị tiếng Việt trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class BankingVisualizer:
    def __init__(self, df_2023):
        self.df = df_2023
        self.current_slide = 0
        
        # Tạo cửa sổ biểu đồ
        self.fig = plt.figure(figsize=(15, 8))
        self.ax = self.fig.add_subplot(111)
        
        # Điều chỉnh lề
        plt.subplots_adjust(bottom=0.2, left=0.15, right=0.85)

        # Danh sách slide: 1. Tháng, 2. Tiểu bang
        self.slides = [self.draw_monthly_trend_premium, self.draw_state_lollipop]
        
        # Thiết lập nút bấm
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Tháng', color='whitesmoke', hovercolor='#D5D8DC')
        self.btn_next = Button(self.ax_next, 'Tiểu Bang >>', color='whitesmoke', hovercolor='#D5D8DC')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_current_slide()
        plt.show()

    def update_navigation(self):
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

    # --- BIỂU ĐỒ 1: TỔNG TIỀN THEO THÁNG (2023) ---
    def draw_monthly_trend_premium(self):
        self.df['month_num'] = self.df['transaction_date'].dt.month
        monthly_data = self.df.groupby('month_num')['transaction_amount'].sum().reset_index()
        month_labels = [f"Tháng {int(m)}" for m in monthly_data['month_num']]

        self.ax.set_facecolor('white')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#BDC3C7')

        # Vẽ đường chính
        self.ax.plot(month_labels, monthly_data['transaction_amount'], 
                     color='#1A5276', linewidth=3.5, marker='o', 
                     markersize=8, markerfacecolor='white', markeredgewidth=2.5, 
                     markeredgecolor='#1A5276')
        
        self.ax.fill_between(month_labels, monthly_data['transaction_amount'], 
                             color='#AED6F1', alpha=0.4)

        max_val = monthly_data['transaction_amount'].max()
        
        # Ghi số tiền xen kẽ trên dưới
        bottom_months = [2, 4, 6, 9, 11]

        for i, row in monthly_data.iterrows():
            m_num = int(row['month_num'])
            val = row['transaction_amount']
            
            if m_num in bottom_months:
                y_pos = val - (max_val * 0.05)
                v_align = 'top'
            else:
                y_pos = val + (max_val * 0.03)
                v_align = 'bottom'
            
            self.ax.text(i, y_pos, f'{val:,.0f}', 
                         ha='center', va=v_align, 
                         fontsize=8.5, fontweight='bold', color='#1F618D')

        self.ax.set_title('PHÂN TÍCH BIẾN ĐỘNG DÒNG TIỀN HÀNG THÁNG (2023)', 
                          fontsize=15, fontweight='bold', color='#1A5276', pad=25)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

    # --- BIỂU ĐỒ 2: TIỂU BANG LOLLIPOP (2023) ---
    def draw_state_lollipop(self):
        state_data = self.df.groupby('state')['transaction_amount'].sum().reset_index()
        state_data = state_data.sort_values(by='transaction_amount', ascending=True).tail(15)

        self.ax.hlines(y=state_data['state'], xmin=0, xmax=state_data['transaction_amount'], 
                        color='#D5D8DC', alpha=0.8, linewidth=1.5)
        
        colors = sns.color_palette("viridis", len(state_data))
        self.ax.scatter(state_data['transaction_amount'], state_data['state'], 
                        color=colors, s=120, alpha=1, edgecolors='white', linewidth=1.2, zorder=3)

        for i, row in state_data.iterrows():
            self.ax.text(row['transaction_amount'], row['state'], 
                          f"    {row['transaction_amount']:,.0f}", 
                          va='center', ha='left', fontsize=9, fontweight='bold', color='#34495E')

        self.ax.set_title('TOP 15 TIỂU BANG CÓ TỔNG CHI TIÊU CAO NHẤT (2023)', 
                          fontsize=15, fontweight='bold', color='#212F3D', pad=25)
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        max_val = state_data['transaction_amount'].max()
        self.ax.set_xlim(0, max_val * 1.25)
        self.ax.grid(axis='x', linestyle='--', alpha=0.3)

def run_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # LỌC DỮ LIỆU NĂM 2023
        df_2023 = df[df['transaction_date'].dt.year == 2023].dropna(subset=['transaction_date']).copy()
        
        if df_2023.empty:
            print("Thông báo: Không tìm thấy dữ liệu cho năm 2023.")
            return

        BankingVisualizer(df_2023)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    run_analysis('indian_banking_transactions.csv')