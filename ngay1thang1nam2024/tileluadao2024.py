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

class FraudVisualizer:
    def __init__(self, df_2024):
        self.df = df_2024
        self.current_slide = 0
        
        # Danh sách các hàm vẽ biểu đồ phân tích gian lận năm 2024
        self.slides = [
            self.draw_fraud_count,   # Biểu đồ 1: Số lượng 0 & 1
            self.draw_fraud_amount,  # Biểu đồ 2: Tổng tiền An toàn vs Lừa đảo
            self.draw_state_fraud,   # Biểu đồ 3: Tỉ lệ theo Tiểu bang
            self.draw_monthly_fraud  # Biểu đồ 4: Thống kê theo Tháng
        ]
        
        # Khởi tạo khung hình
        self.fig = plt.figure(figsize=(14, 8))
        self.setup_ui()
        self.draw_current_slide()
        plt.show()

    def setup_ui(self):
        """Thiết lập lại giao diện để tránh xung đột giữa các biểu đồ"""
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

    # --- BIỂU ĐỒ 1: THỐNG KÊ SỐ LƯỢNG (2024) ---
    def draw_fraud_count(self):
        counts = self.df['is_fraud'].value_counts().reset_index()
        counts.columns = ['Status', 'Count']
        counts['Label'] = counts['Status'].map({0: 'An toàn (0)', 1: 'Lừa đảo (1)'})
        
        sns.barplot(x='Label', y='Count', data=counts, ax=self.ax, palette=['#27AE60', '#C0392B'])
        
        for i in self.ax.containers:
            self.ax.bar_label(i, fmt='{:,.0f}', padding=3, fontweight='bold', fontsize=11)
            
        self.ax.set_title("1. SỐ LƯỢNG GIAO DỊCH AN TOÀN VS LỪA ĐẢO (2024)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_ylabel("Số lượng giao dịch")
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

    # --- BIỂU ĐỒ 2: TỔNG SỐ TIỀN (2024) ---
    def draw_fraud_amount(self):
        amounts = self.df.groupby('is_fraud')['transaction_amount'].sum().reset_index()
        labels = amounts['is_fraud'].map({0: 'An toàn', 1: 'Lừa đảo'})
        
        self.ax.pie(amounts['transaction_amount'], labels=labels, autopct='%1.1f%%', 
                    startangle=140, colors=['#3498DB', '#E74C3C'], explode=[0, 0.2], 
                    shadow=True, textprops={'fontweight': 'bold'})
        
        self.ax.set_title("2. TỶ TRỌNG GIÁ TRỊ GIAO DỊCH GIAN LẬN (2024)", fontsize=15, fontweight='bold')

    # --- BIỂU ĐỒ 3: TỶ LỆ THEO TIỂU BANG (2024) ---
    def draw_state_fraud(self):
        state_fraud = pd.crosstab(self.df['state'], self.df['is_fraud'], normalize='index') * 100
        if 1 not in state_fraud.columns: state_fraud[1] = 0 # Phòng trường hợp không có gian lận
        
        state_fraud.columns = ['An toàn', 'Lừa đảo']
        state_fraud = state_fraud.sort_values(by='Lừa đảo', ascending=True).tail(15) # Top 15 rủi ro nhất

        state_fraud.plot(kind='barh', stacked=True, ax=self.ax, color=['#2ECC71', '#E74C3C'], alpha=0.8)
        
        for i, (idx, row) in enumerate(state_fraud.iterrows()):
            self.ax.text(100, i, f" {row['Lừa đảo']:.2f}% ", va='center', ha='right', 
                         color='white', fontweight='bold', fontsize=9)

        self.ax.set_title("3. TỶ LỆ (%) GIAO DỊCH LỪA ĐẢO THEO TIỂU BANG (2024)", fontsize=15, fontweight='bold', pad=20)
        self.ax.set_xlabel("Phần trăm (%)")
        self.ax.set_xlim(0, 100)
        self.ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2)

    # --- BIỂU ĐỒ 4: BIẾN ĐỘNG THEO THÁNG (2024) ---
    def draw_monthly_fraud(self):
        self.df['Month'] = self.df['transaction_date'].dt.month
        monthly_fraud = self.df[self.df['is_fraud'] == 1].groupby('Month').size()
        monthly_safe = self.df[self.df['is_fraud'] == 0].groupby('Month').size()
        
        # Đảm bảo hiển thị đủ các tháng có trong dữ liệu
        all_months = sorted(self.df['Month'].unique())
        month_labels = [f"Tháng {m}" for m in all_months]
        
        safe_values = [monthly_safe.get(m, 0) for m in all_months]
        fraud_values = [monthly_fraud.get(m, 0) for m in all_months]

        # Trục Y trái: An toàn
        self.ax.plot(month_labels, safe_values, marker='o', color='#27AE60', linewidth=2.5, label='An toàn')
        self.ax.set_ylabel("Số lượng An toàn", color='#27AE60', fontweight='bold')
        self.ax.tick_params(axis='y', labelcolor='#27AE60')
        
        # Trục Y phải: Lừa đảo
        ax2 = self.ax.twinx()
        ax2.bar(month_labels, fraud_values, color='#C0392B', alpha=0.3, label='Lừa đảo')
        ax2.set_ylabel("Số lượng Lừa đảo", color='#C0392B', fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='#C0392B')
        
        self.ax.set_title("4. BIẾN ĐỘNG GIAO DỊCH GIAN LẬN THEO THÁNG (2024)", fontsize=15, fontweight='bold', pad=20)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        lines, labels = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

def run_analysis(file_path):
    try:
        df = pd.read_csv(file_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # LỌC DỮ LIỆU NĂM 2024
        df_2024 = df[df['transaction_date'].dt.year == 2024].copy()
        
        if df_2024.empty:
            print("Thông báo: Không tìm thấy dữ liệu giao dịch cho năm 2024.")
            return

        FraudVisualizer(df_2024)
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    run_analysis('indian_banking_transactions.csv')