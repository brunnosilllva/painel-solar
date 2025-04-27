import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import dash
import os
from dash import dcc, html, Input, Output, State

# Token do Mapbox
px.set_mapbox_access_token("pk.eyJ1IjoiYnJ1bm9zaWx2YTkyIiwiYSI6ImNsaWFrdmU1azAzeWczbHQ3MzYzaHlhMmcifQ.r84qOFtY3ZFJGE7o7RYzGg")

# Carregar e preparar dados
df = pd.read_excel("data/Dados_energia_solar.xlsx")
gdf = gpd.read_file("data/Dados_energia_solar.geojson")

if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

merged = gdf.merge(df, on="OBJECTID")
geojson = json.loads(merged.to_json())

centroid_all = merged.geometry.union_all().centroid
initial_center = {"lat": centroid_all.y, "lon": centroid_all.x}
initial_zoom = 12

prod_cols = [
    'Produção de energia no mês de janeiro kW do telhado do edifício',
    'Produção de energia no mês de fevereiro kW do telhado do edifício',
    'Produção de energia no mês de março kW do telhado do edifício',
    'Produção de energia no mês de abril kW do telhado do edifício',
    'Produção de energia no mês de maio kW do telhado do edifício',
    'Produção de energia no mês de junho kW do telhado do edifício',
    'Produção de energia no mês de julho kW do telhado do edifício',
    'Produção de energia no mês de agosto kW do telhado do edifício',
    'Produção de energia no mês de setembro kW do telhado do edifício',
    'Produção de energia no mês de outubro kW do telhado do edifício',
    'Produção de energia no mês de novembro kW do telhado do edifício',
    'Produção de energia no mês de dezembro kW do telhado do edifício'
]

rad_cols = [
    'Quantidade de Radiação Solar no mês de janeiro (kW.m²)',
    'Quantidade de Radiação Solar no mês de Fevereiro (kW.m²)',
    'Quantidade de Radiação Solar no mês de Março (kW.m²)',
    'Quantidade de Radiação Solar no mês de Abril (kW.m²)',
    'Quantidade de Radiação Solar no mês de Maio (kW.m²)',
    'Quantidade de Radiação Solar no mês de Junho (kW.m²)',
    'Quantidade de Radiação Solar no mês de Julho (kW.m²)',
    'Quantidade de Radiação Solar no mês de Agosto (kW.m²)',
    'Quantidade de Radiação Solar no mês de Setembro (kW.m²)',
    'Quantidade de Radiação Solar no mês de Outubro (kW.m²)',
    'Quantidade de Radiação Solar no mês de Novembro (kW.m²)',
    'Quantidade de Radiação Solar no mês de Dezembro (kW.m²)'
]

media_producao = merged[prod_cols].mean().tolist()
media_radiacao = merged[rad_cols].mean().tolist()

# Cálculos estatísticos para os cards
qtd_imoveis = merged.shape[0]
producao_total = merged['Produção de energia kW do telhado do edifício'].sum()
media_producao_geral = merged['Produção de energia kW do telhado do edifício'].mean()

# Estilos reutilizáveis
card_style = {
    'width': '23%',
    'display': 'inline-block',
    'backgroundColor': '#F2F2F2',
    'padding': '15px',
    'margin': '5px',
    'textAlign': 'center',
    'borderRadius': '12px'
}

row_style = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'marginBottom': '10px'
}

# Layout do Dash
app = dash.Dash(__name__)
server = app.server  # ESSA LINHA É FUNDAMENTAL pro Render

app.layout = html.Div([
    html.H1("⚡ Painel Interativo para prospecção de clientes – Solar Map ⚡", style={'textAlign': 'center'}),
    html.P("Explore imóveis com alto potencial para geração de energia solar. Consulte a capacidade estimada de produção fotovoltaica, dados detalhados sobre radiação solar média mensal e indicadores que auxiliam na escolha dos melhores locais para instalação de sistemas solares. Identifique oportunidades ideais para economia e sustentabilidade com base em critérios técnicos e ambientais.",
           style={'textAlign': 'center'}),

    # Caixas de informações (Passo 01)
    html.Div([
        html.Div([
            html.H4("Total de Imóveis"),
            html.P(f"{qtd_imoveis}")
        ], style={'width': '29%', 'display': 'inline-block', 'backgroundColor': '#F2F2F2',
                  'padding': '15px', 'margin': '5px', 'textAlign': 'center', 'borderRadius': '12px'}),

        html.Div([
            html.H4("Produção Total Estimada (kW)"),
            html.P(f"{producao_total:,.0f}")
        ], style={'width': '29%', 'display': 'inline-block', 'backgroundColor': '#F2F2F2',
                  'padding': '15px', 'margin': '5px', 'textAlign': 'center', 'borderRadius': '12px'}),

        html.Div([
            html.H4("Média de Produção por Imóvel (kW)"),
            html.P(f"{media_producao_geral:,.2f}")
        ], style={'width': '29%', 'display': 'inline-block', 'backgroundColor': '#F2F2F2',
                  'padding': '15px', 'margin': '5px', 'textAlign': 'center', 'borderRadius': '12px'}),
    ], style={'marginBottom': '20px'}),

    # Filtros e dropdowns
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='bairro-dropdown',
                options=[{'label': b, 'value': b} for b in merged['Bairros'].unique()],
                placeholder="Selecione um ou mais Bairros",
                multi=True
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='info-dropdown',
                options=[
                    {'label': 'Capacidade de Produção de energia em kW por m²',
                     'value': 'Capacidade de Produção de energia em kW por m²'},
                    {'label': 'Produção de energia kW do telhado do edifício',
                     'value': 'Produção de energia kW do telhado do edifício'}
                ],
                placeholder="Selecione a Informação"
            )
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Input(id='min-value', type='number', placeholder='Valor Mínimo',
                  style={'marginRight': '10px'}),
        dcc.Input(id='max-value', type='number', placeholder='Valor Máximo'),
        html.Button('Limpar Filtros', id='reset-button', n_clicks=0,
                    style={'marginLeft': '15px'})
    ], style={'marginTop': '10px', 'marginBottom': '10px'}),

    dcc.Graph(id='choropleth-map', style={'height': '80vh'}, config={'scrollZoom': True}),

    html.Div([
        html.Div([
            dcc.Graph(id='grafico-producao')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 1%'}),

        html.Div([
            dcc.Graph(id='grafico-radiacao')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 1%'})
    ]),

    # Caixas de informações adicionais (Passo 02)
    html.Div([
        # Primeira fileira
        html.Div([
            html.Div([
                html.H4("Área da Edificação (m²)"),
                html.P(id="area-edificacao-display")
            ], style=card_style),

            html.Div([
                html.H4("Radiação Solar Máxima (kW/m²)"),
                html.P(id="radiacao-max-display")
            ], style=card_style),

            html.Div([
                html.H4("Capacidade por m² (kW)"),
                html.P(id="capacidade-por-m2-display")
            ], style=card_style),

            html.Div([
                html.H4("Produção do Telhado (kW)"),
                html.P(id="producao-telhado-display")
            ], style=card_style),
        ], style=row_style),

        # Segunda fileira
        html.Div([
            html.Div([
                html.H4("Produção com Placas (kWh/dia)"),
                html.P(id="capacidade-placas-dia-display")
            ], style=card_style),

            html.Div([
                html.H4("Produção com Placas (kWh/mês)"),
                html.P(id="capacidade-placas-mes-display")
            ], style=card_style),

            html.Div([
                html.H4("Qtde de Placas Necessárias"),
                html.P(id="quantidade-placas-display")
            ], style=card_style),

            html.Div([
                html.H4("Potencial Médio Diário (kW·dia/m²)"),
                html.P(id="potencial-medio-dia-display")
            ], style=card_style),
        ], style=row_style),

        # Terceira fileira
        html.Div([
            html.Div([
                html.H4("Renda Total (R$)"),
                html.P(id="renda-total-display")
            ], style=card_style),

            html.Div([
                html.H4("Renda per capita (R$)"),
                html.P(id="renda-per-capita-display")
            ], style=card_style),

            html.Div([
                html.H4("Renda domiciliar per capita (R$)"),
                html.P(id="renda-domiciliar-per-capita-display")
            ], style=card_style),

            html.Div([], style=card_style)  # Caixa vazia para completar o layout
        ], style=row_style),
    ], style={'marginBottom': '40px'}),
])

@app.callback(
    [
        Output('choropleth-map', 'figure'),
        Output('grafico-producao', 'figure'),
        Output('grafico-radiacao', 'figure'),
        Output('bairro-dropdown', 'value'),
        Output('info-dropdown', 'value'),
        Output('min-value', 'value'),
        Output('max-value', 'value'),
        Output('area-edificacao-display', 'children'),
        Output('radiacao-max-display', 'children'),
        Output('capacidade-por-m2-display', 'children'),
        Output('producao-telhado-display', 'children'),
        Output('capacidade-placas-dia-display', 'children'),
        Output('capacidade-placas-mes-display', 'children'),
        Output('quantidade-placas-display', 'children'),
        Output('potencial-medio-dia-display', 'children'),
        Output('renda-total-display', 'children'),
        Output('renda-per-capita-display', 'children'),
        Output('renda-domiciliar-per-capita-display', 'children')
    ],
    [
        Input('bairro-dropdown', 'value'),
        Input('info-dropdown', 'value'),
        Input('min-value', 'value'),
        Input('max-value', 'value'),
        Input('choropleth-map', 'clickData'),
        Input('reset-button', 'n_clicks')
    ],
    [
        State('bairro-dropdown', 'value'),
        State('info-dropdown', 'value'),
        State('min-value', 'value'),
        State('max-value', 'value')
    ]
)
def update_outputs(selected_bairros, selected_info, min_value, max_value, clickData, n_clicks,
                   state_bairros, state_info, state_min, state_max):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered_id == 'reset-button':
        return (
            go.Figure(), go.Figure(), go.Figure(),
            None, None, None, None,
            "0.0", "0.0", "0.0", "0.0",
            "0.0", "0.0", "0", "0.0",
            "0.0", "0.0", "0.0"
        )

    info = selected_info or "Produção de energia kW do telhado do edifício"
    df_f = merged.copy()

    if selected_bairros:
        df_f = df_f[df_f['Bairros'].isin(selected_bairros)]

    if min_value is not None or max_value is not None:
        lo = min_value if min_value is not None else df_f[info].min()
        hi = max_value if max_value is not None else df_f[info].max()
        df_f = df_f[(df_f[info] >= lo) & (df_f[info] <= hi)]

    map_center = initial_center
    map_zoom = initial_zoom
    selected_id = None

    if clickData:
        selected_id = clickData['points'][0]['location']
        selected_row = df_f[df_f['OBJECTID'] == selected_id]
        if not selected_row.empty:
            map_center = {
                "lat": selected_row.geometry.iloc[0].centroid.y,
                "lon": selected_row.geometry.iloc[0].centroid.x
            }
            map_zoom = 15

    # Mapa
    if df_f.empty or info not in df_f.columns:
        fig_map = px.choropleth_mapbox()
        fig_map.update_layout(title="Nenhum dado encontrado com os filtros selecionados")
    else:
        fig_map = px.choropleth_map(
            df_f,
            geojson=geojson,
            locations="OBJECTID",
            featureidkey="properties.OBJECTID",
            color=info,
            color_continuous_scale="Viridis",
            center=map_center,
            zoom=map_zoom,
            opacity=0.6,
            labels={info: info}
        )
        if selected_id:
            sel_geom = df_f[df_f['OBJECTID'] == selected_id].geometry.iloc[0]
            fig_map.add_trace(go.Scattermap(
                lat=[sel_geom.centroid.y],
                lon=[sel_geom.centroid.x],
                mode='markers',
                marker=go.scattermap.Marker(size=15, color='red'),
                name='Selecionado'
            ))

    # Gráficos
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto',
             'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    if selected_id:
        filtered_df = df_f[df_f['OBJECTID'] == selected_id]
        if not filtered_df.empty:
            dados = filtered_df.iloc[0]
            fig_producao = px.bar(x=meses, y=[dados[col] for col in prod_cols],
                                  labels={"x": "Mês", "y": "kW"},
                                  title=f"Produção de energia - Imóvel {selected_id}")
            fig_producao.add_scatter(x=meses, y=media_producao, mode='lines', name='Média Geral')

            fig_radiacao = px.bar(x=meses, y=[dados[col] for col in rad_cols],
                                  labels={"x": "Mês", "y": "kW/m²"},
                                  title=f"Radiação Solar - Imóvel {selected_id}")
            fig_radiacao.add_scatter(x=meses, y=media_radiacao, mode='lines', name='Média Geral')

            # Atualizar valores das caixas de informações adicionais
            area_edificacao = dados['Área em metros quadrados da edificação']
            radiacao_max = dados['Quantidade de Radiação Máxima Solar nos mêses (kW.m²']
            capacidade_por_m2 = dados['Capacidade de Produção de energia em kW por m²']
            producao_telhado = dados['Produção de energia kW do telhado do edifício']
            capacidade_placas_dia = dados['Capacidade de Produção de energia em Placas Fotovoltaicas em kW.h.dia']
            capacidade_placas_mes = dados['Capacidade de Produção de energia em Placas Fotovoltaicas em kW.h.mês']
            quantidade_placas = dados['Quantidade de Placas Fotovoltaicas capaz de gerar a energia gerada do imovel']
            potencial_medio_dia = dados['Potencial médio de geração FV em um dia (kW.dia.m²)']
            renda_total = dados['Renda Total']
            renda_per_capita = dados['Renda per capita']
            renda_domiciliar_per_capita = dados['Renda domiciliar per capita']
        else:
            fig_producao = px.bar(title="Sem dados para este imóvel")
            fig_radiacao = px.bar(title="Sem dados para este imóvel")
            area_edificacao = radiacao_max = capacidade_por_m2 = producao_telhado = 0.0
            capacidade_placas_dia = capacidade_placas_mes = potencial_medio_dia = 0.0
            quantidade_placas = 0
            renda_total = renda_per_capita = renda_domiciliar_per_capita = 0.0
    else:
        fig_producao = px.bar(x=meses, y=media_producao,
                              labels={"x": "Mês", "y": "kW"},
                              title="Produção Média de Energia (kW)")
        fig_radiacao = px.bar(x=meses, y=media_radiacao,
                              labels={"x": "Mês", "y": "kW/m²"},
                              title="Radiação Solar Média (kW/m²)")

        # Valores padrão para os cards quando nenhum imóvel está selecionado
        area_edificacao = radiacao_max = capacidade_por_m2 = producao_telhado = 0.0
        capacidade_placas_dia = capacidade_placas_mes = potencial_medio_dia = 0.0
        quantidade_placas = 0
        renda_total = renda_per_capita = renda_domiciliar_per_capita = 0.0

    return (fig_map, fig_producao, fig_radiacao, state_bairros, state_info, state_min, state_max,
            f"{area_edificacao:,.2f}", f"{radiacao_max:,.2f}", f"{capacidade_por_m2:,.2f}",
            f"{producao_telhado:,.2f}", f"{capacidade_placas_dia:,.2f}", f"{capacidade_placas_mes:,.2f}",
            f"{quantidade_placas:,.0f}", f"{potencial_medio_dia:,.2f}", f"{renda_total:,.2f}",
            f"{renda_per_capita:,.2f}", f"{renda_domiciliar_per_capita:,.2f}")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Render vai passar o PORT pelo ambiente
    app.run(host="0.0.0.0", port=port, debug=False)
