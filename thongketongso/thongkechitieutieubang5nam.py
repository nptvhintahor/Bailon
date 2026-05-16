import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import os
import sys

# Khử lỗi hiển thị tiếng Việt trên Terminal
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
    
    # Lọc 5 năm từ 2019 - 2023
    years_list = [2019, 2020, 2021, 2022, 2023]
    df_filtered = df[df['Year'].isin(years_list)].copy()

    # Gom nhóm theo Bang, Năm và Hạng mục để phục vụ Hover chi tiết
    state_year_cat_data = df_filtered.groupby([STATE_COL, 'Year', CAT_COL])['transaction_amount'].sum().reset_index()

    # Gom nhóm theo Bang và Năm cho biểu đồ Stacked chính
    state_year_sum = df_filtered.groupby([STATE_COL, 'Year'])['transaction_amount'].sum().reset_index()
    
    # Tính tổng 5 năm để sắp xếp thứ tự Bang trên trục X (Từ cao đến thấp)
    total_per_state = state_year_sum.groupby(STATE_COL)['transaction_amount'].sum().sort_values(ascending=False).reset_index()
    state_order = total_per_state[STATE_COL].tolist()
    
    colors_palette = ['#D1E8E4', '#94B49F', '#789395', '#5E8B7E', '#2F5D62']

# 2. KHỞI TẠO GIAO DIỆN (DASH)
    app = Dash(__name__)

    app.layout = html.Div(style={'backgroundColor': '#FDFDFD', 'padding': '20px', 'fontFamily': 'Arial'}, children=[
        
        html.H1("PHÂN TÍCH TIỂU BANG & CHI TIẾT 15 HẠNG MỤC CHI TIÊU", 
                style={'textAlign': 'left', 'color': '#2F5D62', 'fontWeight': '800'}),

        # CỤM ĐIỀU KHIỂN
        html.Div(style={
            'display': 'flex', 'justifyContent': 'flex-end', 'alignItems': 'flex-end', 
            'gap': '15px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 
            'borderRadius': '12px', 'marginBottom': '20px', 'border': '1px solid #e9ecef'
        }, children=[
            html.Div([
                html.Label("1. Chọn Năm", style={'fontSize': '12px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='year-select', options=[{'label': y, 'value': y} for y in years_list], 
                             placeholder="Năm", style={'width': '110px'})
            ]),
            html.Div([
                html.Label("2. Tiểu bang A", style={'fontSize': '12px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='state-1', placeholder="Chọn bang A", style={'width': '180px'})
            ]),
            html.Div([
                html.Label("3. Tiểu bang B", style={'fontSize': '12px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='state-2', placeholder="Chọn bang B", style={'width': '180px'})
            ]),
            html.Button('SO SÁNH', id='btn-compare', n_clicks=0, style={
                'backgroundColor': '#2F5D62', 'color': 'white', 'border': 'none', 
                'padding': '10px 20px', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'
            })
        ]),

        html.Div(id='comparison-result-area'),
        dcc.Graph(id='main-display-graph', style={'height': '80vh'})
    ])

# 3. CALLBACK XỬ LÝ TƯƠNG TÁC

    @app.callback(
        [Output('state-1', 'options'), Output('state-2', 'options')],
        Input('year-select', 'value')
    )
    def update_states(year):
        if not year: return [], []
        states = sorted(df[df['Year'] == year][STATE_COL].unique())
        options = [{'label': s, 'value': s} for s in states]
        return options, options

    @app.callback(
        [Output('main-display-graph', 'figure'), Output('comparison-result-area', 'children')],
        Input('btn-compare', 'n_clicks'),
        [State('year-select', 'value'), State('state-1', 'value'), State('state-2', 'value')]
    )
    def handle_display(n_clicks, year, s1, s2):
        # CHẾ ĐỘ MẶC ĐỊNH: Biểu đồ Stacked 5 năm
        if n_clicks == 0 or not all([year, s1, s2]):
            fig = go.Figure()

            for i, y_val in enumerate(years_list):
                # Lấy dữ liệu tổng của năm
                y_data = state_year_sum[state_year_sum['Year'] == y_val].set_index(STATE_COL).reindex(state_order).reset_index()
                
                # Tạo Hover text chi tiết 15 hạng mục
                hover_texts = []
                for state in state_order:
                    # Lọc 15 hạng mục của bang này trong năm đó
                    cat_details = state_year_cat_data[(state_year_cat_data[STATE_COL] == state) & 
                                                     (state_year_cat_data['Year'] == y_val)]
                    cat_details = cat_details.sort_values('transaction_amount', ascending=False)
                    
                    details_str = "<br>".join([f"• {r[CAT_COL]}: {r['transaction_amount']:,.0f} INR" for _, r in cat_details.iterrows()])
                    
                    total_val = y_data[y_data[STATE_COL] == state]['transaction_amount'].values[0]
                    
                    hover_texts.append(
                        f"<b>BANG: {state} ({y_val})</b><br>" +
                        f"Tổng chi tiêu: {total_val:,.0f} INR<br>" +
                        f"----------------------------------<br>" +
                        f"<b>CHI TIẾT HẠNG MỤC TẠI {state}:</b><br>{details_str}"
                    )

                fig.add_trace(go.Bar(
                    name=str(y_val), x=y_data[STATE_COL], y=y_data['transaction_amount'],
                    marker_color=colors_palette[i],
                    customdata=hover_texts,
                    hovertemplate="%{customdata}<extra></extra>"
                ))

            # GHIM TỔNG CỘNG TRÊN ĐẦU CỘT
            fig.add_trace(go.Scatter(
                x=state_order, 
                y=total_per_state['transaction_amount'],
                mode='text', 
                text=[f"<b>{v:,.0f}</b>" for v in total_per_state['transaction_amount']],
                textposition='top center', 
                showlegend=False, 
                hoverinfo='skip'
            ))

            fig.update_layout(
                barmode='stack', paper_bgcolor='#FDFDFD', plot_bgcolor='#FDFDFD',
                xaxis={'title': "Tiểu bang", 'categoryorder': 'array', 'categoryarray': state_order},
                yaxis={'title': "Số tiền giao dịch (INR)"},
                margin=dict(t=100, b=100, l=80, r=60)
            )
            return fig, ""

        # CHẾ ĐỘ SO SÁNH
        v1 = df[(df['Year'] == year) & (df[STATE_COL] == s1)]['transaction_amount'].sum()
        v2 = df[(df['Year'] == year) & (df[STATE_COL] == s2)]['transaction_amount'].sum()
        diff = abs(v1 - v2)
        
        fig_comp = go.Figure(data=[
            go.Bar(name=s1, x=[s1], y=[v1], marker_color='#457b9d', text=f"{v1:,.0f}", textposition='outside'),
            go.Bar(name=s2, x=[s2], y=[v2], marker_color='#e63946', text=f"{v2:,.0f}", textposition='outside')
        ])
        fig_comp.update_layout(title=f"SO SÁNH NĂM {year}: {s1} VS {s2}", template='plotly_white')
        
        result_box = html.Div(style={
            'padding': '20px', 'backgroundColor': 'white', 'borderLeft': '10px solid #2F5D62', 
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'marginBottom': '20px'
        }, children=[
            html.H2(f"Mức chênh lệch: {diff:,.0f} INR", style={'color': '#c0392b', 'margin': '0'})
        ])

        return fig_comp, result_box

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")