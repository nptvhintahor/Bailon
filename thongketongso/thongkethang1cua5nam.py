import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os
import sys

# Khử lỗi hiển thị tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

# 1. ĐỌC VÀ XỬ LÝ DỮ LIỆU
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

try:
    df = pd.read_csv(file_path)
    
    # Xử lý ngày tháng
    df['Date'] = pd.to_datetime(df.iloc[:, 2], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    
    # Ép kiểu dữ liệu
    df['Amount'] = pd.to_numeric(df.iloc[:, 6], errors='coerce').fillna(0)
    df['State'] = df.iloc[:, 10].astype(str)
    df['Category'] = df.iloc[:, 9].astype(str)
    df['Payment_Method'] = df.iloc[:, 5].astype(str)
    df['Channel'] = df.iloc[:, 16].astype(str)
    df['Is_Fraud'] = pd.to_numeric(df.iloc[:, 12], errors='coerce').fillna(0)

    # LỌC DỮ LIỆU: ĐÚNG NGÀY 01/01 TỪ 2019 ĐẾN 2024
    df_filtered = df[
        (df['Day'] == 1) & 
        (df['Month'] == 1) & 
        (df['Year'].isin([2019, 2020, 2021, 2022, 2023, 2024]))
    ].copy()

# 2. GIAO DIỆN (LAYOUT)
    app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    app.layout = dbc.Container(fluid=True, children=[
        html.H1("PHÂN TÍCH GIAO DỊCH NGÀY ĐẦU NĂM (01/01/2019 - 01/01/2024)", 
                className="text-center my-4", style={'color': '#2c3e50'}),
        
        dcc.Tabs(id="main-tabs", value='tab-1', children=[
            dcc.Tab(label='TỔNG QUAN NGÀY 1/1', value='tab-1'),
            dcc.Tab(label='TIỂU BANG (1/1)', value='tab-2'),
            dcc.Tab(label='HẠNG MỤC KINH DOANH', value='tab-3'),
            dcc.Tab(label='PHƯƠNG THỨC & KÊNH', value='tab-4'),
            dcc.Tab(label='PHÂN TÍCH LỪA ĐẢO', value='tab-5'),
        ]),
        html.Div(id='tabs-content', className="p-4")
    ])

# 3. CALLBACK XỬ LÝ CHUYỂN TRANG
    @app.callback(Output('tabs-content', 'children'), Input('main-tabs', 'value'))
    def render_content(tab):
        
        if len(df_filtered) == 0:
            return html.Div("⚠️ Không có dữ liệu ngày 01/01 trong file CSV.", className="text-center p-5 text-danger")

        # TRANG 1: TỔNG QUAN
        if tab == 'tab-1':
            summary = df_filtered.groupby('Year').agg(cnt=('Amount', 'count'), total=('Amount', 'sum')).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=summary['Year'], y=summary['cnt'], name='Số giao dịch', marker_color='#2c3e50'))
            fig.add_trace(go.Scatter(x=summary['Year'], y=summary['total'], name='Tổng tiền', yaxis='y2', line=dict(color='#e67e22', width=3)))
            fig.update_layout(title="Hoạt động ngày 01/01 qua các năm", yaxis2=dict(overlaying='y', side='right'), template="plotly_white")
            return dcc.Graph(figure=fig)

        # TRANG 2: TIỂU BANG
        elif tab == 'tab-2':
            state_data = df_filtered.groupby('State')['Amount'].sum().sort_values(ascending=False).head(20).reset_index()
            fig = px.bar(state_data, x='State', y='Amount', title="Dòng tiền theo Tiểu bang (Ngày 1/1)", color='Amount', color_continuous_scale='YlGnBu')
            return dcc.Graph(figure=fig)

        # TRANG 3: HẠNG MỤC KINH DOANH (BIỂU ĐỒ CỘT + HOVER INFO)
        elif tab == 'tab-3':
            cat_data = df_filtered.groupby('Category').agg(
                Số_lượng=('Amount', 'count'), 
                Tổng_tiền=('Amount', 'sum')
            ).sort_values('Số_lượng', ascending=False).head(15).reset_index()
            
            # Sử dụng Bar chart thay cho Treemap
            fig = px.bar(
                cat_data, 
                x='Category', 
                y='Số_lượng',
                color='Tổng_tiền', # Màu sắc đại diện cho tiền
                title="Top 15 Hạng mục kinh doanh ngày 1/1 (Di chuột để xem chi tiết)",
                labels={'Số_lượng': 'Số lượng giao dịch', 'Category': 'Hạng mục'},
                color_continuous_scale='Viridis',
                custom_data=['Số_lượng', 'Tổng_tiền'] # Dữ liệu ẩn để dùng cho Hover
            )
            
            # Cấu hình Hover: Chỉ hiện khi di chuột, không hiện chữ trên cột
            fig.update_traces(
                hovertemplate="<br>".join([
                    "<b>Hạng mục: %{x}</b>",
                    "Số giao dịch: %{customdata[0]:,}",
                    "Tổng số tiền: %{customdata[1]:,.0f} INR",
                    "<extra></extra>" # Ẩn phần tên trace thừa bên cạnh
                ])
            )
            
            fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
            return dcc.Graph(figure=fig)

        # TRANG 4: PHƯƠNG THỨC & KÊNH
        elif tab == 'tab-4':
            m_data = df_filtered.groupby('Payment_Method').size().reset_index(name='count')
            c_data = df_filtered.groupby('Channel').size().reset_index(name='count')
            fig_m = px.pie(m_data, values='count', names='Payment_Method', title="Phương thức")
            fig_c = px.pie(c_data, values='count', names='Channel', title="Kênh", hole=0.4)
            return dbc.Row([dbc.Col(dcc.Graph(figure=fig_m), width=6), dbc.Col(dcc.Graph(figure=fig_c), width=6)])

        # TRANG 5: LỪA ĐẢO
        elif tab == 'tab-5':
            fraud_summary = df_filtered.groupby('Year').agg(Total=('Is_Fraud', 'count'), Fraud=('Is_Fraud', 'sum')).reset_index()
            fig = px.bar(fraud_summary, x='Year', y=['Total', 'Fraud'], title="Thống kê lừa đảo ngày 1/1", barmode='group')
            return dcc.Graph(figure=fig)

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"❌ Lỗi: {e}")