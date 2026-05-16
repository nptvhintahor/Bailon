import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import os
import sys

# Khử lỗi hiển thị tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

# 1. ĐỌC VÀ XỬ LÝ DỮ LIỆU
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

try:
    # Đọc dữ liệu (Bỏ qua header nếu cần, ở đây giả định file có header hoặc dùng index)
    df = pd.read_csv(file_path)
    
    # Vị trí các cột dựa trên dữ liệu mẫu bạn gửi:
    # 2: Date, 3: Time, 6: Amount, 9: Category, 10: State
    idx_date, idx_time, idx_amt, idx_cat, idx_state = 2, 3, 6, 9, 10
    
    # Ép kiểu và gộp Ngày + Giờ
    df['dt_combined'] = pd.to_datetime(df.iloc[:, idx_date].astype(str) + ' ' + df.iloc[:, idx_time].astype(str), errors='coerce')
    df = df.dropna(subset=['dt_combined'])
    
    df['Year'] = df['dt_combined'].dt.year
    df['Hour'] = df['dt_combined'].dt.hour
    df['Amount'] = pd.to_numeric(df.iloc[:, idx_amt], errors='coerce').fillna(0)
    df['Category'] = df.iloc[:, idx_cat].astype(str)
    df['State'] = df.iloc[:, idx_state].astype(str)

    years_list = [2019, 2020, 2021, 2022, 2023]
    df_filtered = df[df['Year'].isin(years_list)].copy()

    hour_year_sum = df_filtered.groupby(['Hour', 'Year'])['Amount'].sum().reset_index()
    colors = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51']

# 2. GIAO DIỆN
    app = Dash(__name__)

    app.layout = html.Div(style={'backgroundColor': '#f8f9fa', 'padding': '40px', 'fontFamily': 'Arial'}, children=[
        html.H1("PHÂN TÍCH GIAO DỊCH 24 GIỜ", style={'textAlign': 'center', 'color': '#264653'}),
        
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='hour-graph')
        ]),

        # Vùng kết quả chi tiết
        html.Div(id='detail-output', style={'marginTop': '30px'})
    ])

# 3. CALLBACK XỬ LÝ CLICK (SỬA LỖI fullData)
    @app.callback(
        Output('detail-output', 'children'),
        Input('hour-graph', 'clickData')
    )
    def update_details(clickData):
        if not clickData:
            return html.Div("Bấm vào một cột bất kỳ trên biểu đồ để xem chi tiết.", 
                            style={'textAlign': 'center', 'padding': '30px', 'color': '#999', 'border': '1px dashed #ccc'})

        try:
            # Lấy thông tin an toàn hơn
            point = clickData['points'][0]
            
            # 1. Lấy Giờ (Trục X)
            h_clicked = int(point['x'])
            
            # 2. Lấy Năm (Dựa trên curveNumber - thứ tự của trace)
            # Trace 0 = 2019, Trace 1 = 2020...
            trace_index = point['curveNumber']
            y_clicked = years_list[trace_index]

            # Lọc dữ liệu chi tiết
            sub = df_filtered[(df_filtered['Hour'] == h_clicked) & (df_filtered['Year'] == y_clicked)]
            
            # Thống kê Top 15 cho 2 cột
            st_df = sub.groupby('State').agg(cnt=('Amount', 'count'), total=('Amount', 'sum')).sort_values('total', ascending=False).head(15).reset_index()
            ct_df = sub.groupby('Category').agg(cnt=('Amount', 'count'), total=('Amount', 'sum')).sort_values('total', ascending=False).head(15).reset_index()

            return html.Div([
                # Header thông tin tổng quát
                html.Div(style={'backgroundColor': '#264653', 'color': 'white', 'padding': '20px', 'borderRadius': '10px 10px 0 0', 'display': 'flex', 'justifyContent': 'space-between'}, children=[
                    html.Div([
                        html.H2(f"CHI TIẾT: {h_clicked}:00 (Năm {y_clicked})", style={'margin': '0'}),
                        html.P(f"Số lượng giao dịch: {len(sub):,}", style={'margin': '5px 0 0 0', 'opacity': '0.8'})
                    ]),
                    html.H2(f"{sub['Amount'].sum():,.2f} INR", style={'color': '#e9c46a', 'margin': '0'})
                ]),

                # Hai cột dữ liệu
                html.Div(style={'display': 'flex', 'gap': '20px', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '0 0 10px 10px'}, children=[
                    # Cột 1: Tiểu bang
                    html.Div(style={'flex': '1'}, children=[
                        html.H4("📍 TIỂU BANG", style={'color': '#2a9d8f', 'borderBottom': '2px solid #2a9d8f'}),
                        html.Table(style={'width': '100%'}, children=[
                            html.Tr([html.Th("Bang", style={'textAlign': 'left'}), html.Th("Giao dịch"), html.Th("Tổng tiền", style={'textAlign': 'right'})]),
                            *[html.Tr([
                                html.Td(r['State']), 
                                html.Td(f"{r['cnt']:,}", style={'textAlign': 'center'}), 
                                html.Td(f"{r['total']:,.0f}", style={'textAlign': 'right'})
                            ]) for _, r in st_df.iterrows()]
                        ])
                    ]),
                    # Cột 2: Hạng mục
                    html.Div(style={'flex': '1'}, children=[
                        html.H4("🛒 HẠNG MỤC KINH DOANH", style={'color': '#e76f51', 'borderBottom': '2px solid #e76f51'}),
                        html.Table(style={'width': '100%'}, children=[
                            html.Tr([html.Th("Hạng mục", style={'textAlign': 'left'}), html.Th("Giao dịch"), html.Th("Tổng tiền", style={'textAlign': 'right'})]),
                            *[html.Tr([
                                html.Td(r['Category']), 
                                html.Td(f"{r['cnt']:,}", style={'textAlign': 'center'}), 
                                html.Td(f"{r['total']:,.0f}", style={'textAlign': 'right'})
                            ]) for _, r in ct_df.iterrows()]
                        ])
                    ])
                ])
            ])
        except Exception as e:
            return html.Div(f"Lỗi truy xuất dữ liệu: {str(e)}", style={'color': 'red', 'fontWeight': 'bold'})

# 4. BIỂU ĐỒ
    @app.callback(
        Output('hour-graph', 'figure'),
        Input('hour-graph', 'id')
    )
    def render_fig(_):
        fig = go.Figure()
        for i, y in enumerate(years_list):
            y_data = hour_year_sum[hour_year_sum['Year'] == y].set_index('Hour').reindex(range(24)).reset_index().fillna(0)
            fig.add_trace(go.Bar(
                name=str(y), 
                x=y_data['Hour'], 
                y=y_data['Amount'],
                marker_color=colors[i],
                hovertemplate="Giờ: %{x}h<br>Tiền: %{y:,.2f}<extra></extra>"
            ))
        fig.update_layout(
            barmode='stack',
            xaxis=dict(title="Giờ trong ngày", tickmode='linear', type='category'),
            yaxis=dict(title="Tổng số tiền (INR)"),
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=60, r=20)
        )
        return fig

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")