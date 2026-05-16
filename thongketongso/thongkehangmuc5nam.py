import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import os
import sys

# Đảm bảo hiển thị tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

# 1. ĐƯỜNG DẪN VÀ XỬ LÝ DỮ LIỆU
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, 'indian_banking_transactions.csv')

CAT_COL = 'merchant_category' 

try:
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['Year'] = df['transaction_date'].dt.year
    
    years_list = [2019, 2020, 2021, 2022, 2023]
    df_filtered = df[df['Year'].isin(years_list)].copy()

    # Gom nhóm theo Loại hình, Năm và Bang (Sắp xếp bang theo bảng chữ cái hoặc số tiền)
    cat_year_state_data = df_filtered.groupby([CAT_COL, 'Year', 'state'])['transaction_amount'].sum().reset_index()

    # Tính tổng theo Loại hình và Năm cho biểu đồ chính
    cat_year_data = df_filtered.groupby([CAT_COL, 'Year'])['transaction_amount'].sum().reset_index()
    
    # Tính tổng 5 năm để sắp xếp thứ tự cột (từ cao đến thấp)
    total_per_cat = cat_year_data.groupby(CAT_COL)['transaction_amount'].sum().sort_values(ascending=False).reset_index()
    cat_order = total_per_cat[CAT_COL].tolist()
    
    colors_palette = ['#D1E8E4', '#94B49F', '#789395', '#5E8B7E', '#2F5D62']

    # 2. KHỞI TẠO DASHBOARD
    app = Dash(__name__)

    app.layout = html.Div(style={'backgroundColor': '#FDFDFD', 'padding': '30px', 'fontFamily': 'Arial'}, children=[
        html.H1("PHÂN TÍCH LOẠI HÌNH CHI TIÊU CHI TIẾT THEO TOÀN BỘ BANG", 
                style={'textAlign': 'left', 'color': '#2F5D62', 'fontWeight': '800'}),

        # CỤM ĐIỀU KHIỂN GÓC TRÊN PHẢI
        html.Div(style={
            'position': 'absolute', 'top': '30px', 'right': '30px', 'zIndex': '1000',
            'display': 'flex', 'gap': '15px', 'alignItems': 'flex-end',
            'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '15px',
            'boxShadow': '0 10px 25px rgba(0,0,0,0.1)', 'border': '1px solid #eee'
        }, children=[
            html.Div([
                html.Label("1. CHỌN NĂM", style={'fontSize': '11px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='year-select', options=[{'label': f"Năm {y}", 'value': y} for y in years_list], 
                             placeholder="Năm", style={'width': '100px'})
            ]),
            html.Div([
                html.Label("2. LOẠI HÌNH A", style={'fontSize': '11px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='cat-1', placeholder="Chọn loại A", style={'width': '180px'})
            ]),
            html.Div([
                html.Label("3. LOẠI HÌNH B", style={'fontSize': '11px', 'fontWeight': 'bold'}),
                dcc.Dropdown(id='cat-2', placeholder="Chọn loại B", style={'width': '180px'})
            ]),
            html.Button('SO SÁNH', id='btn-compare', n_clicks=0, style={
                'backgroundColor': '#2F5D62', 'color': 'white', 'border': 'none', 
                'padding': '10px 20px', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'
            })
        ]),

        html.Div(id='comparison-result-area'),
        dcc.Graph(id='main-display-graph', style={'height': '80vh'})
    ])

    @app.callback(
        [Output('cat-1', 'options'), Output('cat-2', 'options')],
        Input('year-select', 'value')
    )
    def update_categories(year):
        if not year: return [], []
        categories = sorted(df[df['Year'] == year][CAT_COL].unique())
        options = [{'label': c, 'value': c} for c in categories]
        return options, options

    @app.callback(
        [Output('main-display-graph', 'figure'), Output('comparison-result-area', 'children')],
        Input('btn-compare', 'n_clicks'),
        [State('year-select', 'value'), State('cat-1', 'value'), State('cat-2', 'value')]
    )
    def handle_graph_update(n_clicks, year, c1, c2):
        if n_clicks == 0 or not all([year, c1, c2]):
            fig = go.Figure()
            
            for i, y_val in enumerate(years_list):
                # Dữ liệu của từng năm
                y_data = cat_year_data[cat_year_data['Year'] == y_val].set_index(CAT_COL).reindex(cat_order).reset_index()
                
                # Logic hiển thị TOÀN BỘ CÁC BANG khi di chuột
                hover_texts = []
                for cat in cat_order:
                    # Lấy tất cả các bang có phát sinh chi tiêu cho loại hình này
                    state_list = cat_year_state_data[(cat_year_state_data[CAT_COL] == cat) & (cat_year_state_data['Year'] == y_val)]
                    state_list = state_list.sort_values('transaction_amount', ascending=False)
                    
                    # Tạo chuỗi hiển thị toàn bộ bang
                    details = "<br>".join([f"• {row['state']}: {row['transaction_amount']:,.0f} INR" for _, row in state_list.iterrows()])
                    
                    # Tính tổng của năm đó để hiện ở dòng đầu hover
                    total_year_cat = y_data[y_data[CAT_COL] == cat]['transaction_amount'].values[0]
                    
                    hover_texts.append(
                        f"<b>{cat} ({y_val})</b><br>" +
                        f"Tổng năm: {total_year_cat:,.0f} INR<br>" +
                        f"--------------------------<br>" +
                        f"<b>Chi tiết tất cả các bang:</b><br>{details}"
                    )

                fig.add_trace(go.Bar(
                    name=str(y_val), 
                    x=y_data[CAT_COL], 
                    y=y_data['transaction_amount'],
                    marker_color=colors_palette[i],
                    customdata=hover_texts,
                    hovertemplate="%{customdata}<extra></extra>"
                ))
            
            # --- HIỂN THỊ TỔNG CỘNG TRÊN ĐẦU CỘT ---
            # Dùng Scatter mode text để ghim con số tổng 5 năm lên đỉnh
            fig.add_trace(go.Scatter(
                x=total_per_cat[CAT_COL],
                y=total_per_cat['transaction_amount'],
                mode='text',
                text=[f"<b>{v:,.0f}</b>" for v in total_per_cat['transaction_amount']],
                textposition='top center',
                showlegend=False,
                hoverinfo='skip'
            ))

            fig.update_layout(
                barmode='stack',
                paper_bgcolor='#FDFDFD',
                plot_bgcolor='#FDFDFD',
                xaxis={'title': "Loại hình CHI TIÊU", 'categoryorder': 'array', 'categoryarray': cat_order},
                yaxis={'title': "Tổng tiền (INR)", 'showgrid': True, 'gridcolor': '#eee'},
                # Tăng lề trên để con số tổng không bị mất
                margin=dict(t=100, b=100, l=80, r=60),
                legend_title_text='Giai đoạn năm'
            )
            return fig, ""

        # Chế độ So sánh (Giữ nguyên)
        v1 = df[(df['Year'] == year) & (df[CAT_COL] == c1)]['transaction_amount'].sum()
        v2 = df[(df['Year'] == year) & (df[CAT_COL] == c2)]['transaction_amount'].sum()
        diff = abs(v1 - v2)
        
        fig_comp = go.Figure(data=[
            go.Bar(name=c1, x=[c1], y=[v1], marker_color='#457b9d', text=f"{v1:,.0f}", textposition='outside'),
            go.Bar(name=c2, x=[c2], y=[v2], marker_color='#e63946', text=f"{v2:,.0f}", textposition='outside')
        ])
        fig_comp.update_layout(title=f"SO SÁNH NĂM {year}: {c1} VS {c2}", template='plotly_white')
        res_ui = html.Div(style={'padding': '20px', 'backgroundColor': 'white', 'borderLeft': '10px solid #2F5D62', 'boxShadow': '0 4px 15px rgba(0,0,0,0.05)', 'marginBottom': '20px'}, 
                           children=[html.H2(f"Chênh lệch: {diff:,.0f} INR", style={'color': '#c0392b', 'margin': '0'})])

        return fig_comp, res_ui

    if __name__ == '__main__':
        app.run(debug=True)

except Exception as e:
    print(f"Lỗi: {e}")