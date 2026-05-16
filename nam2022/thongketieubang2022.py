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

class StateComparisonVisualizer2022:
    def __init__(self, df_2022):
        self.df = df_2022
        # Lấy danh sách các tiểu bang có dữ liệu trong năm 2022
        self.states = sorted(df_2022['state'].unique())
        self.current_slide = 0
        
        # Thiết lập giao diện
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        plt.subplots_adjust(bottom=0.2, left=0.1, right=0.9, top=0.88)

        # Nút bấm điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Lùi', color='#f0f0f0', hovercolor='#d0d0d0')
        self.btn_next = Button(self.ax_next, 'Tiếp >>', color='#f0f0f0', hovercolor='#d0d0d0')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

        self.draw_slide()
        plt.show()

    def draw_slide(self):
        self.ax.clear()
        # Xóa các text layer cũ (như số trang) để không bị đè lên nhau
        self.fig.texts.clear()
        
        state = self.states[self.current_slide]
        state_df = self.df[self.df['state'] == state]

        # 1. Chuẩn bị dữ liệu ghép (Loại tài khoản & Phương thức)
        acc_data = state_df.groupby('account_type')['transaction_amount'].sum().reset_index()
        acc_data.columns = ['Category', 'Amount']
        acc_data['Group'] = 'Loại tài khoản'
        
        chan_data = state_df.groupby('channel')['transaction_amount'].sum().reset_index()
        chan_data.columns = ['Category', 'Amount']
        chan_data['Group'] = 'Phương thức'
        
        combined = pd.concat([acc_data, chan_data])

        # 2. Vẽ biểu đồ cột ghép với Seaborn
        sns.set_style("whitegrid")
        palette = {'Loại tài khoản': '#2E86C1', 'Phương thức': '#D35400'}
        
        sns.barplot(
            x='Category', y='Amount', hue='Group', 
            data=combined, ax=self.ax, palette=palette,
            edgecolor='black', linewidth=0.5, alpha=0.9
        )

        # 3. Làm đẹp trục và tiêu đề cho năm 2022
        self.ax.set_title(f'PHÂN TÍCH DÒNG TIỀN NĂM 2022 - TIỂU BANG: {state.upper()}', 
                          fontsize=18, fontweight='bold', color='#1B2631', pad=30)
        self.ax.set_xlabel('Hạng mục phân tích', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Tổng số tiền (INR)', fontsize=12, fontweight='bold')
        
        # Ghi số tiền trên đầu cột
        for container in self.ax.containers:
            self.ax.bar_label(container, fmt='{:,.0f}', padding=8, fontsize=9, fontweight='bold', color='#212F3D')

        # Xoay nhãn trục X
        self.ax.tick_params(axis='x', rotation=15)
        
        # Định dạng lại trục Y
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        # Bỏ khung viền thừa
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        # Cập nhật trạng thái nút
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.states) - 1)
        
        # Hiển thị số trang
        plt.figtext(0.5, 0.15, f"Tiểu bang {self.current_slide + 1} / {len(self.states)}", 
                    ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

        self.fig.canvas.draw_idle()

    def next(self, event):
        if self.current_slide < len(self.states) - 1:
            self.current_slide += 1
            self.draw_slide()

    def previous(self, event):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.draw_slide()

def run_state_analysis(file_path):
    try:
        # Đọc dữ liệu
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # LỌC DỮ LIỆU NĂM 2022
        df_2022 = df[df['transaction_date'].dt.year == 2022].dropna(subset=['transaction_date', 'state']).copy()
        
        if df_2022.empty:
            print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2022.")
            return

        print(f">>> Đang khởi chạy phân tích so sánh tiểu bang cho {len(df_2022):,} giao dịch năm 2022...")
        StateComparisonVisualizer2022(df_2022)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{file_path}'")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    run_state_analysis('indian_banking_transactions.csv')