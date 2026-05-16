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
    df = pd.read_csv(file_path)
    
    # Gán tên cột dựa trên vị trí index (Dựa trên cấu trúc dữ liệu ngân hàng Ấn Độ)
    # 1:Cust_ID, 2:Date, 6:Amount, 9:Category, 10:State, 12:Is_Fraud, 15:Status, 17:KYC_Status
    df['Cust_ID'] = df.iloc[:, 1]
    df['Year'] = pd.to_datetime(df.iloc[:, 2], errors='coerce').dt.year
    df['Amount'] = pd.to_numeric(df.iloc[:, 6], errors='coerce').fillna(0)
    df['Category'] = df.iloc[:, 9].astype(str)
    df['State'] = df.iloc[:, 10].astype(str)
    df['Is_Fraud'] = pd.to_numeric(df.iloc[:, 12], errors='coerce').fillna(0)
    df['Status'] = df.iloc[:, 15].astype(str)
    df['KYC'] = df.iloc[:, 17].astype(str) # Cột trạng thái KYC

    # Lọc giai đoạn 2019 - 2023
    years_list = [2019, 2020, 2021, 2022, 2023]
    df_filtered = df[df['Year'].isin(years_list)].copy()
    yearly_summary = df_filtered.groupby('Year').size().reset_index(name='Total_TXNs')

# 2. GIAO DIỆN
    app = Dash(__name__)

    app.layout = html.Div(style={'backgroundColor': '#f0f2f5', 'padding': '30px', 'fontFamily': 'Segoe UI'}, children=[
        html.H1("PHÂN TÍCH GIAO DỊCH & TỶ LỆ KYC", style={'textAlign': 'center', 'color': '#1a365d'}),
        
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='year-bar-graph')
        ]),

        html.Div(id='detail-panel', style={'marginTop': '30px'})
    ])

# 3. CALLBACK CHI TIẾT
    @app.callback(
        Output('detail-panel', 'children'),
        Input('year-bar-graph', 'clickData')
    )
    def update_dashboard(clickData):
        if not clickData:
            return html.Div("Chọn một năm trên biểu đồ để xem báo cáo KYC và Lừa đảo.", 
                            style={'textAlign': 'center', 'padding': '50px', 'color': '#718096'})

        selected_year = int(clickData['points'][0]['x'])
        data_year = df_filtered[df_filtered['Year'] == selected_year]

        # --- Thống kê KYC ---
        kyc_counts = data_year['KYC'].value_counts()
        total_year = len(data_year)
        verified_count = kyc_counts.get('Verified', 0)
        kyc_rate = (verified_count / total_year) * 100 if total_year > 0 else 0

        # --- Thống kê User ---
        user_counts = data_year['Cust_ID'].value_counts()
        distinct_users = len(user_counts[user_counts == 1])
        repeat_txns = len(data_year[data_year['Cust_ID'].isin(user_counts[user_counts >= 2].index)])

        # --- Thống kê Trạng thái Lừa đảo ---
        fraud_data = data_year[data_year['Is_Fraud'] == 1]
        f_status = fraud_data['Status'].value_counts()

        # --- Top 15 Bang & Hạng mục ---
        state_stats = data_year.groupby('State').agg(total=('Amount', 'count'), fraud=('Is_Fraud', 'sum')).sort_values('total', ascending=False).head(15).reset_index()
        cat_stats = data_year.groupby('Category').agg(total=('Amount', 'count'), fraud=('Is_Fraud', 'sum')).sort_values('total', ascending=False).head(15).reset_index()

        return html.Div([
            # Khung KPI phía trên
            html.Div(style={'display': 'flex', 'gap': '15px', 'marginBottom': '20px'}, children=[
                # Thẻ KYC
                html.Div(style={'flex': '1', 'backgroundColor': '#3182ce', 'color': 'white', 'padding': '20px', 'borderRadius': '12px'}, children=[
                    html.H4("TỶ LỆ KYC (XÁC MINH)", style={'margin': '0'}),
                    html.H2(f"{kyc_rate:.1f}%"),
                    html.P(f"{verified_count:,} / {total_year:,} Verified")
                ]),
                # Thẻ Fraud Status
                html.Div(style={'flex': '1.5', 'backgroundColor': '#e53e3e', 'color': 'white', 'padding': '20px', 'borderRadius': '12px'}, children=[
                    html.H4("TRẠNG THÁI CA LỪA ĐẢO"),
                    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '10px'}, children=[
                        html.B(f"Thành công: {f_status.get('Success', 0)}"),
                        html.B(f"Thất bại: {f_status.get('Failed', 0)}"),
                        html.B(f"Chờ: {f_status.get('Pending', 0)}")
                    ]),
                    html.P(f"Tổng: {len(fraud_data)} ca", style={'borderTop': '1px solid white', 'marginTop': '10px'})
                ]),
                # Thẻ User
                html.Div(style={'flex': '1', 'backgroundColor': '#38a169', 'color': 'white', 'padding': '20px', 'borderRadius': '12px'}, children=[
                    html.H4("NGƯỜI DÙNG"),
                    html.P(f"Riêng biệt: {distinct_users:,}"),
                    html.P(f"Trùng lặp: {repeat_txns:,}")
                ]),
            ]),

            # Hai bảng chi tiết (15 dòng)
            html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
                html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'}, children=[
                    html.H4("📍 TOP 15 TIỂU BANG", style={'color': '#2b6cb0', 'borderBottom': '2px solid #2b6cb0'}),
                    html.Table(style={'width': '100%', 'marginTop': '10px'}, children=[
                        html.Tr([html.Th("Bang"), html.Th("Tổng GD"), html.Th("Lừa đảo")]),
                        *[html.Tr([
                            html.Td(r['State']),
                            html.Td(f"{r['total']:,}", style={'textAlign': 'center'}),
                            html.Td(f"{r['fraud']:,}", style={'textAlign': 'center', 'color': 'red' if r['fraud'] > 0 else 'black', 'fontWeight': 'bold'})
                        ], style={'borderBottom': '1px solid #edf2f7'}) for _, r in state_stats.iterrows()]
                    ])
                ]),
                html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'}, children=[
                    html.H4("🛒 TOP 15 HẠNG MỤC", style={'color': '#c05621', 'borderBottom': '2px solid #c05621'}),
                    html.Table(style={'width': '100%', 'marginTop': '10px'}, children=[
                        html.Tr([html.Th("Hạng mục"), html.Th("Tổng GD"), html.Th("Lừa đảo")]),
                        *[html.Tr([
                            html.Td(r['Category'][:25]),
                            html.Td(f"{r['total']:,}", style={'textAlign': 'center'}),
                            html.Td(f"{r['fraud']:,}", style={'textAlign': 'center', 'color': 'red' if r['fraud'] > 0 else 'black', 'fontWeight': 'bold'})
                        ], style={'borderBottom': '1px solid #edf2f7'}) for _, r in cat_stats.iterrows()]
                    ])
                ])
            ])
        ])

# 4. BIỂU ĐỒ NĂM
    @app.callback(
        Output('year-bar-graph', 'figure'),
        Input('year-bar-graph', 'id')
    )
    def render_year_chart(_):
        fig = go.Figure(data=[go.Bar(x=yearly_summary['Year'], y=yearly_summary['Total_TXNs'], marker_color='#4299e1')])
        fig.update_layout(title="Tổng giao dịch theo năm (Click để xem KYC & Fraud)", xaxis=dict(type='category'), plot_bgcolor='white')
        return fig

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")