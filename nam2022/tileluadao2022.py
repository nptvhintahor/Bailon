import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button

# Cấu hình hiển thị tiếng Việt trên Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình font để tránh lỗi hiển thị tiếng Việt trên biểu đồ
plt.rcParams['font.family'] = 'Arial'

class FraudVisualizer2022:
    def __init__(self, df_2022):
        self.df = df_2022
        self.current_slide = 0
        
        # Danh sách các hàm vẽ biểu đồ cho năm 2022
        self.slides = [
            self.draw_fraud_count,   # Biểu đồ 1: Số lượng An toàn vs Lừa đảo
            self.draw_fraud_amount,  # Biểu đồ 2: Tỷ trọng tổng giá trị
            self.draw_state_fraud,   # Biểu đồ 3: Tỉ lệ theo Tiểu bang
            self.draw_monthly_fraud  # Biểu đồ 4: Biến động theo Tháng
        ]
        
        # Khởi tạo khung hình
        self.fig = plt.figure(figsize=(14, 8))
        self.setup_ui()
        self.draw_current_slide()
        plt.show()

    def setup_ui(self):
        """Xóa sạch và thiết lập lại giao diện để tránh xung đột giữa các biểu đồ"""
        self.fig.clf() 
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(bottom=0.25, left=0.15, right=0.85, top=0.88)

        # Tạo nút bấm điều hướng
        self.ax_prev = plt.axes([0.35, 0.05, 0.1, 0.06])
        self.ax_next = plt.axes([0.55, 0.05, 0.1, 0.06])
        
        self.btn_prev = Button(self.ax_prev, '<< Lùi', color='#f0f0f0', hovercolor='lightblue')
        self.btn_next = Button(self.ax_next, 'Tiếp >>', color='#f0f0f0', hovercolor='lightblue')
        
        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)

    def draw_current_slide(self):
        self.setup_ui()
        self.slides[self.current_slide]()
        
        # Ẩn/Hiện nút dựa trên vị trí trang
        self.ax_prev.set_visible(self.current_slide > 0)
        self.ax_next.set_visible(self.current_slide < len(self.slides) - 1)
        
        # Hiển thị số trang
        plt.figtext(0.5, 0.15, f"Trang {self.current_slide + 1} / {len(self.slides)}", 
                    ha="center", fontsize=10, fontweight='bold', 
                    bbox={"facecolor":"red", "alpha":0.1, "pad":5})
        
        self.fig.canvas.draw_idle()

    def next(self, event):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            self.draw_current_slide()

    def previous(self, event):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.draw_current_slide()

    # --- BIỂU ĐỒ 1: THỐNG KÊ SỐ LƯỢNG (2022) ---
    def draw_fraud_count(self):
        counts = self.df['is_fraud'].value_counts().reset_index()
        counts.columns = ['Status', 'Count']
        counts['Label'] = counts['Status'].map({0: 'An toàn (0)', 1: 'Lừa đảo (1)'})
        
        sns.barplot(x='Label', y='Count', data=counts, ax=self.ax, palette=['#27AE60', '#C0392B'])
        
        for i in self.ax.containers:
            self.ax.bar_label(i, fmt='{:,.0f}', padding=3, fontweight='bold', fontsize=11)
            
        self.ax.set_title("1. SỐ LƯỢNG GIAO DỊCH AN TOÀN VS LỪA ĐẢO (2022)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_ylabel("Số lượng giao dịch")
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

    # --- BIỂU ĐỒ 2: TỔNG SỐ TIỀN (2022) ---
    def draw_fraud_amount(self):
        amounts = self.df.groupby('is_fraud')['transaction_amount'].sum().reset_index()
        labels = amounts['is_fraud'].map({0: 'An toàn', 1: 'Lừa đảo'})
        
        self.ax.pie(amounts['transaction_amount'], labels=labels, autopct='%1.1f%%', 
                    startangle=140, colors=['#3498DB', '#E74C3C'], explode=[0, 0.2], 
                    shadow=True, textprops={'fontweight': 'bold'})
        
        self.ax.set_title("2. TỶ TRỌNG TỔNG GIÁ TRỊ GIAO DỊCH (2022)", fontsize=15, fontweight='bold')

    # --- BIỂU ĐỒ 3: TỶ LỆ THEO TIỂU BANG (2022) ---
    def draw_state_fraud(self):
        # Tính toán tỷ lệ phần trăm
        state_fraud = pd.crosstab(self.df['state'], self.df['is_fraud'], normalize='index') * 100
        state_fraud.columns = ['An toàn', 'Lừa đảo']
        state_fraud = state_fraud.sort_values(by='Lừa đảo', ascending=True).tail(20) # Lấy top 20 rủi ro nhất

        state_fraud.plot(kind='barh', stacked=True, ax=self.ax, color=['#2ECC71', '#E74C3C'], alpha=0.8)
        
        for i, (idx, row) in enumerate(state_fraud.iterrows()):
            self.ax.text(100, i, f" {row['Lừa đảo']:.2f}% ", va='center', ha='right', 
                         color='white', fontweight='bold', fontsize=9)

        self.ax.set_title("3. TỶ LỆ (%) GIAO DỊCH LỪA ĐẢO THEO TIỂU BANG (2022)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_xlabel("Phần trăm (%)")
        self.ax.set_xlim(0, 105)
        self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2)

    # --- BIỂU ĐỒ 4: THỐNG KÊ THEO THÁNG (2022) ---
    def draw_monthly_fraud(self):
        self.df['Month'] = self.df['transaction_date'].dt.month
        
        # Tạo khung đầy đủ 12 tháng để tránh thiếu dữ liệu
        all_months = pd.DataFrame({'Month': range(1, 13)})
        
        monthly_fraud = self.df[self.df['is_fraud'] == 1].groupby('Month').size().reset_index(name='Lừa đảo')
        monthly_safe = self.df[self.df['is_fraud'] == 0].groupby('Month').size().reset_index(name='An toàn')
        
        stats = all_months.merge(monthly_fraud, on='Month', how='left').merge(monthly_safe, on='Month', how='left').fillna(0)
        month_labels = [f"T{m}" for m in stats['Month']]

        # Trục Y trái: An toàn
        self.ax.plot(month_labels, stats['An toàn'], marker='o', color='#27AE60', linewidth=2.5, label='An toàn')
        self.ax.set_ylabel("Số lượng An toàn", color='#27AE60', fontweight='bold')
        self.ax.tick_params(axis='y', labelcolor='#27AE60')
        
        # Trục Y phải: Lừa đảo
        ax2 = self.ax.twinx()
        ax2.bar(month_labels, stats['Lừa đảo'], color='#C0392B', alpha=0.3, label='Lừa đảo')
        ax2.set_ylabel("Số lượng Lừa đảo", color='#C0392B', fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='#C0392B')
        
        self.ax.set_title("4. BIẾN ĐỘNG GIAO DỊCH THEO THÁNG (2022)", fontsize=15, fontweight='bold', pad=20)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        lines, labels = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

def run_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # LỌC DỮ LIỆU NĂM 2022
        df_2022 = df[df['transaction_date'].dt.year == 2022].dropna(subset=['transaction_date']).copy()
        
        if df_2022.empty:
            print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2022.")
            return

        print(f">>> Đang khởi chạy phân tích gian lận cho {len(df_2022):,} giao dịch năm 2022...")
        FraudVisualizer2022(df_2022)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    # Đảm bảo file indian_banking_transactions.csv nằm cùng thư mục
    run_analysis('indian_banking_transactions.csv')