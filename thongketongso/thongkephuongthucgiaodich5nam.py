import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import os
import sys
import json

# Khử lỗi hiển thị tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

# 1. ĐỌC VÀ XỬ LÝ DỮ LIỆU
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

try:
    df = pd.read_csv(file_path)
    
    df['Year'] = pd.to_datetime(df.iloc[:, 2], errors='coerce').dt.year
    df['Amount'] = pd.to_numeric(df.iloc[:, 6], errors='coerce').fillna(0)
    df['Payment_Method'] = df.iloc[:, 5].astype(str)
    df['Payment_Type'] = df.iloc[:, 7].astype(str)
    df['State'] = df.iloc[:, 10].astype(str)
    df['Channel'] = df.iloc[:, 16].astype(str)

    df_filtered = df[df['Year'].isin([2019, 2020, 2021, 2022, 2023])].copy()
    yearly_summary = df_filtered.groupby('Year').size().reset_index(name='Total_TXNs')

# 2. GIAO DIỆN (LAYOUT)
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container(fluid=True, style={'backgroundColor': '#f1f5f9', 'padding': '30px'}, children=[
        html.H1("TRỰC QUAN HOÁ DÒNG TIỀN & PHƯƠNG THỨC GIAO DỊCH", className="text-center mb-4", style={'color': '#1e293b'}),
        
        dbc.Card(dbc.CardBody(dcc.Graph(id='main-year-chart')), className="shadow-sm mb-4"),
        html.Div(id='detail-panel'),

        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-title"), close_button=True),
            dbc.ModalBody(id="modal-content"),
        ], id="state-detail-modal", size="xl", is_open=False)
    ])

# 3. CALLBACK XỬ LÝ CLICK BIỂU ĐỒ NĂM
    @app.callback(
        Output('detail-panel', 'children'),
        Input('main-year-chart', 'clickData')
    )
    def update_dashboard(clickData):
        if not clickData:
            return html.Div("💡 Chọn một năm để xem báo cáo chi tiết.", className="text-center p-5 text-muted border rounded bg-white")

        selected_year = int(clickData['points'][0]['x'])
        data_year = df_filtered[df_filtered['Year'] == selected_year]

        total_txn = len(data_year)
        total_amt = data_year['Amount'].sum()
        avg_amt = total_amt / total_txn if total_txn > 0 else 0
        
        def get_summary(col):
            return data_year.groupby(col).agg(cnt=('Amount','count'), total=('Amount','sum')).sort_values('cnt', ascending=False).reset_index()

        m_stats = get_summary('Payment_Method')
        t_stats = get_summary('Payment_Type')
        c_stats = get_summary('Channel')
        state_stats = data_year.groupby('State').agg(cnt=('Amount','count'), total=('Amount','sum')).sort_values('cnt', ascending=False).head(15).reset_index()

        return html.Div([
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("TỔNG GIAO DỊCH"), html.H3(f"{total_txn:,}")]), color="dark", inverse=True), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("TỔNG GIÁ TRỊ (INR)"), html.H3(f"{total_amt:,.0f}")]), color="success", inverse=True), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.H6("GIÁ TRỊ TRUNG BÌNH"), html.H3(f"{avg_amt:,.0f}")]), color="info", inverse=True), width=4),
            ], className="mb-4"),

            # Bảng tóm tắt phía trên (Thêm Bordered và Header màu)
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("💳 PHƯƠNG THỨC", className="text-primary"),
                    dbc.Table([
                        html.Thead(html.Tr([html.Th("Tên"), html.Th("Lượt"), html.Th("Tiền")], style={'backgroundColor': '#f8fafc'})),
                        html.Tbody([html.Tr([html.Td(r[0]), html.Td(f"{r[1]:,}"), html.Td(f"{r[2]:,.0f}")]) for r in m_stats.values[:5]])
                    ], size="sm", bordered=True, hover=True)
                ])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("🔄 LOẠI HÌNH", className="text-success"),
                    dbc.Table([
                        html.Thead(html.Tr([html.Th("Loại"), html.Th("Lượt"), html.Th("Tiền")], style={'backgroundColor': '#f8fafc'})),
                        html.Tbody([html.Tr([html.Td(r[0]), html.Td(f"{r[1]:,}"), html.Td(f"{r[2]:,.0f}")]) for r in t_stats.values[:5]])
                    ], size="sm", bordered=True, hover=True)
                ])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H5("📱 KÊNH GIAO DỊCH", className="text-info"),
                    dbc.Table([
                        html.Thead(html.Tr([html.Th("Kênh"), html.Th("Lượt"), html.Th("Tiền")], style={'backgroundColor': '#f8fafc'})),
                        html.Tbody([html.Tr([html.Td(r[0]), html.Td(f"{r[1]:,}"), html.Td(f"{r[2]:,.0f}")]) for r in c_stats.values[:5]])
                    ], size="sm", bordered=True, hover=True)
                ])), width=4),
            ], className="mb-4"),

            dbc.Card([
                dbc.CardHeader(html.H4(f"Phân tích theo Tiểu Bang - Năm {selected_year}")),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Tiểu Bang"), html.Th("Số Lượt GD"), html.Th("Tổng Tiền (INR)"), html.Th("Hành động")], style={'backgroundColor': '#f8fafc'})),
                    html.Tbody([
                        html.Tr([
                            html.Td(r['State']),
                            html.Td(f"{r['cnt']:,}"),
                            html.Td(f"{r['total']:,.0f}"),
                            html.Td(dbc.Button("Xem chi tiết", id={'type': 'btn-state', 'index': f"{selected_year}|{r['State']}"}, color="primary", size="sm"))
                        ]) for _, r in state_stats.iterrows()
                    ])
                ], hover=True, striped=True, bordered=True)
            ], className="shadow-sm")
        ])

# 4. CALLBACK MỞ MODAL VÀ KẺ CỘT CHI TIẾT
    @app.callback(
        Output("state-detail-modal", "is_open"),
        Output("modal-title", "children"),
        Output("modal-content", "children"),
        Input({'type': 'btn-state', 'index': ALL}, 'n_clicks'),
        State("state-detail-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_modal(n_clicks, is_open):
        if not any(n_clicks):
            return is_open, "", ""

        ctx = callback_context
        triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        year, state_name = triggered_id['index'].split('|')
        
        s_data = df_filtered[(df_filtered['Year'] == int(year)) & (df_filtered['State'] == state_name)]

        m_stats = s_data.groupby('Payment_Method').agg(cnt=('Amount','count'), total=('Amount','sum')).reset_index()
        c_stats = s_data.groupby('Channel').agg(cnt=('Amount','count'), total=('Amount','sum')).reset_index()
        mc_stats = s_data.groupby(['Payment_Method', 'Channel']).agg(cnt=('Amount','count'), total=('Amount','sum')).reset_index()

        modal_body = dbc.Row([
            # Cột 1: Có kẻ bảng chi tiết
            dbc.Col([
                html.H6("1. PHƯƠNG THỨC", className="text-primary fw-bold text-center mb-2"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Tên"), html.Th("GD"), html.Th("Tổng Tiền")], style={'backgroundColor': '#eef2ff'})),
                    html.Tbody([html.Tr([html.Td(r[0]), html.Td(f"{r[1]:,}"), html.Td(f"{r[2]:,.0f}")]) for r in m_stats.values])
                ], size="sm", bordered=True, hover=True, striped=True)
            ], width=4, style={'borderRight': '2px solid #dee2e6'}), # Kẻ đường phân cách dọc
            
            # Cột 2
            dbc.Col([
                html.H6("2. KÊNH GIAO DỊCH", className="text-success fw-bold text-center mb-2"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Kênh"), html.Th("GD"), html.Th("Tổng Tiền")], style={'backgroundColor': '#f0fdf4'})),
                    html.Tbody([html.Tr([html.Td(r[0]), html.Td(f"{r[1]:,}"), html.Td(f"{r[2]:,.0f}")]) for r in c_stats.values])
                ], size="sm", bordered=True, hover=True, striped=True)
            ], width=4, style={'borderRight': '2px solid #dee2e6'}), # Kẻ đường phân cách dọc

            # Cột 3
            dbc.Col([
                html.H6("3. CẶP PHỐI HỢP", className="text-warning fw-bold text-center mb-2"),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Cặp"), html.Th("GD"), html.Th("Tổng Tiền")], style={'backgroundColor': '#fffbeb'})),
                    html.Tbody([html.Tr([html.Td(f"{r[0]} - {r[1]}", style={'fontSize': '11px'}), html.Td(f"{r[2]:,}"), html.Td(f"{r[3]:,.0f}")]) for r in mc_stats.values])
                ], size="sm", bordered=True, hover=True, striped=True)
            ], width=4),
        ])

        return True, f"Phân tích dữ liệu: {state_name} ({year})", modal_body

# 5. BIỂU ĐỒ CHÍNH
    @app.callback(Output('main-year-chart', 'figure'), Input('main-year-chart', 'id'))
    def render_main_chart(_):
        fig = go.Figure(go.Bar(x=yearly_summary['Year'], y=yearly_summary['Total_TXNs'], marker_color='#1e293b'))
        fig.update_layout(title="Tổng giao dịch toàn quốc 2019-2023", xaxis=dict(type='category'), template="plotly_white")
        return fig

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")