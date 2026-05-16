import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import os
import sys

# Khử lỗi hiển thị tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

# 1. ĐƯỜNG DẪN VÀ XỬ LÝ DỮ LIỆU
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

STATE_COL = 'state'
CAT_COL = 'merchant_category'

try:
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['Year'] = df['transaction_date'].dt.year
    df['Month'] = df['transaction_date'].dt.month
    
    years_list = [2019, 2020, 2021, 2022, 2023]
    months_list = list(range(1, 13))
    df_filtered = df[df['Year'].isin(years_list)].copy()

    month_year_sum = df_filtered.groupby(['Month', 'Year'])['transaction_amount'].sum().reset_index()
    month_state_data = df_filtered.groupby(['Month', 'Year', STATE_COL])['transaction_amount'].sum().reset_index()
    month_cat_data = df_filtered.groupby(['Month', 'Year', CAT_COL])['transaction_amount'].sum().reset_index()

    colors_palette = ['#495867', '#577399', '#BDD5EA', '#A2D2FF', '#FE5F55']

# 2. KHỞI TẠO GIAO DIỆN
    app = Dash(__name__)

    app.layout = html.Div(style={'backgroundColor': '#0f1115', 'padding': '40px', 'fontFamily': 'Arial', 'color': 'white'}, children=[
        html.H1("PHÂN TÍCH TÀI CHÍNH 2 CỘT DỌC", style={'color': '#A2D2FF', 'textAlign': 'center'}),
        
        # CỤM ĐIỀU KHIỂN
        html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '15px', 'marginBottom': '30px'}, children=[
            dcc.Dropdown(id='year-select', options=[{'label': y, 'value': y} for y in years_list], placeholder="Năm", style={'width': '100px', 'color': 'black'}),
            dcc.Dropdown(id='month-1', options=[{'label': f"Tháng {m}", 'value': m} for m in months_list], placeholder="Tháng A", style={'width': '120px', 'color': 'black'}),
            dcc.Dropdown(id='month-2', options=[{'label': f"Tháng {m}", 'value': m} for m in months_list], placeholder="Tháng B", style={'width': '120px', 'color': 'black'}),
            html.Button('SO SÁNH', id='btn-compare', n_clicks=0, style={'backgroundColor': '#FE5F55', 'color': 'white', 'border': 'none', 'padding': '0 20px', 'borderRadius': '8px', 'cursor': 'pointer'})
        ]),

        html.Div(id='comparison-result-area'),
        dcc.Graph(id='main-display-graph', style={'height': '75vh'})
    ])

# 3. CALLBACK
    @app.callback(
        [Output('main-display-graph', 'figure'), Output('comparison-result-area', 'children')],
        Input('btn-compare', 'n_clicks'),
        [State('year-select', 'value'), State('month-1', 'value'), State('month-2', 'value')]
    )
    def handle_display(n_clicks, year, m1, m2):
        if n_clicks == 0 or not all([year, m1, m2]):
            fig = go.Figure()

            for i, y_val in enumerate(years_list):
                y_data = month_year_sum[month_year_sum['Year'] == y_val].set_index('Month').reindex(months_list).reset_index().fillna(0)
                
                hover_texts = []
                for m in months_list:
                    # Lấy Top 15
                    st_df = month_state_data[(month_state_data['Month'] == m) & (month_state_data['Year'] == y_val)].sort_values('transaction_amount', ascending=False).head(15)
                    ct_df = month_cat_data[(month_cat_data['Month'] == m) & (month_cat_data['Year'] == y_val)].sort_values('transaction_amount', ascending=False).head(15)
                    total_m = y_data.loc[y_data['Month']==m, 'transaction_amount'].values[0]

                    # --- KỸ THUẬT PHÂN CỘT DỌC BẰNG KHOẢNG TRẮNG ĐƠN GIẢN (PRE-FORMATTED) ---
                    header = f"<b>THÁNG {m}/{y_val}</b><br>Tổng: {total_m:,.0f} INR<br>"
                    sub_header = f"<b>{'TIỂU BANG':<25} {'HẠNG MỤC':<25}</b><br>"
                    line = f"{'-'*55}<br>"
                    
                    details = ""
                    max_rows = max(len(st_df), len(ct_df))
                    for idx in range(max_rows):
                        s_name = st_df.iloc[idx][STATE_COL][:12] if idx < len(st_df) else ""
                        s_val = f"{st_df.iloc[idx]['transaction_amount']:,.0f}" if idx < len(st_df) else ""
                        s_str = f"{s_name}: {s_val}"
                        
                        c_name = ct_df.iloc[idx][CAT_COL][:12] if idx < len(ct_df) else ""
                        c_val = f"{ct_df.iloc[idx]['transaction_amount']:,.0f}" if idx < len(ct_df) else ""
                        c_str = f"{c_name}: {c_val}"
                        
                        # Sử dụng khoảng trắng không ngắt (non-breaking spaces) để giữ cột
                        # Mỗi hàng gồm 2 cụm thông tin cách nhau bởi nhiều khoảng trắng
                        details += f"• {s_str:<25}   • {c_str}<br>"

                    hover_texts.append(header + sub_header + line + details)

                fig.add_trace(go.Bar(
                    name=str(y_val), x=[f"Tháng {m}" for m in months_list], y=y_data['transaction_amount'],
                    marker_color=colors_palette[i],
                    customdata=hover_texts,
                    hovertemplate="%{customdata}<extra></extra>"
                ))

            fig.update_layout(
                barmode='stack', paper_bgcolor='#0f1115', plot_bgcolor='#0f1115',
                font=dict(color='#E0E0E0', family="Courier New"), # Dùng font Courier để các cột thẳng hàng
                hoverlabel=dict(bgcolor="#1a1d23", font_size=12, font_family="Courier New", align="left"),
                xaxis={'title': "Tháng"}, yaxis={'title': "Số tiền (INR)"}
            )
            return fig, ""

        # Logic so sánh giữ nguyên
        v1 = df[(df['Year'] == year) & (df['Month'] == m1)]['transaction_amount'].sum()
        v2 = df[(df['Year'] == year) & (df['Month'] == m2)]['transaction_amount'].sum()
        return go.Figure(data=[go.Bar(x=[f"T.{m1}", f"T.{m2}"], y=[v1, v2], marker_color=['#BDD5EA', '#FE5F55'])]), html.H2(f"Chênh lệch: {abs(v1-v2):,.0f} INR")

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")