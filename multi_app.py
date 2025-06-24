import pandas as pd
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from flask import render_template_string
from datetime import datetime, date

# Cargar los datos
file_id = "1PWTw-akWr59Gu7MoHra5WXMKwllxK9bp"
url = f"https://drive.google.com/uc?export=download&id={file_id}"
df = pd.read_csv(url)

# Clasificación por edad
def clasificar_edad(edad):
    if edad < 13:
        return "Niño"
    elif edad < 19:
        return "Adolescente"
    elif edad < 30:
        return "Joven"
    elif edad < 61:
        return "Adulto"
    elif edad < 200:
        return "Adulto mayor"

df['Rango de Edad'] = df['EDAD'].apply(clasificar_edad)

# Clasificación por días de espera
def clasificar_dias(dias):
    if dias < 10:
        return "0-9"
    elif dias < 20:
        return "10-19"
    elif dias < 30:
        return "20-29"
    elif dias < 40:
        return "30-39"
    elif dias < 50:
        return "40-49"
    elif dias < 60:
        return "50-59"
    elif dias < 70:
        return "60-69"
    elif dias < 80:
        return "70-79"
    elif dias < 90:
        return "80-89"
    else:
        return "90+"

df['RANGO_DIAS'] = df['DIFERENCIA_DIAS'].apply(clasificar_dias)

# Preparar datos de fecha
df['DIA_SOLICITACITA'] = pd.to_datetime(df['DIA_SOLICITACITA'], errors='coerce')
df['MES'] = df['DIA_SOLICITACITA'].dt.to_period('M').astype(str)

# Crear servidor Flask compartido
server = Flask(__name__)

@server.route('/')
def index():
    return render_template_string("""
    <html>
    <head>
        <title>Dashboard Médico - Hospital María Auxiliadora</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 50px;
                color: #333;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                animation: fadeIn 1s ease-in-out;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #7f8c8d;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .card {
                background: linear-gradient(135deg, #3498db, #2980b9);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                color: white;
                text-decoration: none;
                display: block;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
                text-decoration: none;
                color: white;
            }
            .card h3 {
                margin: 0 0 10px 0;
                font-size: 1.1em;
            }
            .card p {
                margin: 0;
                opacity: 0.9;
                font-size: 0.9em;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Dashboard Médico</h1>
            <p class="subtitle">Hospital María Auxiliadora - Análisis de Citas Médicas</p>
            <div class="grid">
                <a href="/edad/" class="card">
                    <h3>👥 Distribución por Edad</h3>
                    <p>Análisis de pacientes por rangos etarios</p>
                </a>
                <a href="/espera/" class="card">
                    <h3>⏱️ Tiempos de Espera</h3>
                    <p>Análisis de tiempos de espera para citas</p>
                </a>
                <a href="/modalidad/" class="card">
                    <h3>💻 Modalidad de Atención</h3>
                    <p>Comparación presencial vs remota</p>
                </a>
                <a href="/asegurados/" class="card">
                    <h3>🛡️ Estado del Seguro</h3>
                    <p>Análisis de pacientes asegurados</p>
                </a>
                <a href="/tiempo/" class="card">
                    <h3>📈 Línea de Tiempo</h3>
                    <p>Evolución temporal de citas</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    """)

# App 1: Por Rango de Edad
app_edad = dash.Dash(__name__, server=server, url_base_pathname='/edad/')
app_edad.layout = html.Div([
    html.Div([
        html.H1("📊 Distribución por Rango de Edad", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label("Filtrar por Especialidad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-especialidad-edad',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': esp, 'value': esp} for esp in sorted(df['ESPECIALIDAD'].unique())],
                    value='Todas',
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Filtrar por Sexo:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-sexo-edad',
                    options=[{'label': 'Todos', 'value': 'Todos'}] + 
                            [{'label': sexo, 'value': sexo} for sexo in df['SEXO'].unique()],
                    value='Todos',
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Label("Rango de Días de Espera:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='range-slider-edad',
                min=df['DIFERENCIA_DIAS'].min(),
                max=df['DIFERENCIA_DIAS'].max(),
                value=[df['DIFERENCIA_DIAS'].min(), df['DIFERENCIA_DIAS'].max()],
                marks={i: str(i) for i in range(0, int(df['DIFERENCIA_DIAS'].max()), 20)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'marginBottom': '30px'}),
        
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '20px'}),
    
    dcc.Graph(id='histogram-edad'),
    dcc.Graph(id='pie-chart-edad')
])

@app_edad.callback(
    [Output('histogram-edad', 'figure'),
     Output('pie-chart-edad', 'figure')],
    [Input('dropdown-especialidad-edad', 'value'),
     Input('dropdown-sexo-edad', 'value'),
     Input('range-slider-edad', 'value'),
     Input('histogram-edad', 'clickData')]
)
def update_edad_charts(especialidad, sexo, dias_range, clickData):
    # Filtrar datos
    filtered_df = df.copy()
    
    if especialidad != 'Todas':
        filtered_df = filtered_df[filtered_df['ESPECIALIDAD'] == especialidad]
    if sexo != 'Todos':
        filtered_df = filtered_df[filtered_df['SEXO'] == sexo]
    
    filtered_df = filtered_df[
        (filtered_df['DIFERENCIA_DIAS'] >= dias_range[0]) & 
        (filtered_df['DIFERENCIA_DIAS'] <= dias_range[1])
    ]
    
    # Histograma
    fig_hist = px.histogram(
        filtered_df,
        x='Rango de Edad',
        category_orders={'Rango de Edad': ["Niño", "Adolescente", "Joven", "Adulto", "Adulto mayor"]},
        title=f'Distribución de Edades - {len(filtered_df)} pacientes',
        template='plotly_white'
    )
    
    # Gráfico de pastel
    if clickData is None:
        fig_pie = px.pie(names=[], values=[], title="Haga clic en una barra del histograma", height=500)
    else:
        selected_range = clickData['points'][0]['x']
        pie_df = filtered_df[filtered_df['Rango de Edad'] == selected_range].copy()
        
        if len(pie_df) > 0:
            top_especialidades = pie_df['ESPECIALIDAD'].value_counts().nlargest(5)
            pie_df['ESPECIALIDAD_AGRUPADA'] = pie_df['ESPECIALIDAD'].apply(
                lambda x: x if x in top_especialidades.index else 'Otras'
            )
            
            grouped = pie_df['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
            grouped.columns = ['ESPECIALIDAD', 'CUENTA']
            fig_pie = px.pie(
                grouped,
                names='ESPECIALIDAD',
                values='CUENTA',
                title=f"Top 5 Especialidades - {selected_range} ({len(pie_df)} pacientes)",
                height=600
            )
        else:
            fig_pie = px.pie(names=[], values=[], title="No hay datos para mostrar", height=500)
    
    return fig_hist, fig_pie

# App 2: Por Rango de Días de Espera
app_espera = dash.Dash(__name__, server=server, url_base_pathname='/espera/')
app_espera.layout = html.Div([
    html.Div([
        html.H1("⏱️ Análisis de Tiempos de Espera", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            html.Div([
                html.Label("Filtrar por Especialidad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-especialidad-espera',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': esp, 'value': esp} for esp in sorted(df['ESPECIALIDAD'].unique())],
                    value='Todas'
                )
            ], style={'width': '32%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Modalidad de Atención:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-modalidad-espera',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': mod, 'value': mod} for mod in df['PRESENCIAL_REMOTO'].unique()],
                    value='Todas'
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'}),
            
            html.Div([
                html.Label("Rango de Edad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-edad-espera',
                    options=[{'label': 'Todos', 'value': 'Todos'}] + 
                            [{'label': edad, 'value': edad} for edad in ["Niño", "Adolescente", "Joven", "Adulto", "Adulto mayor"]],
                    value='Todos'
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'})
        ], style={'marginBottom': '20px'}),
        
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '20px'}),
    
    dcc.Graph(id='histogram-espera'),
    dcc.Graph(id='pie-chart-espera')
])

@app_espera.callback(
    [Output('histogram-espera', 'figure'),
     Output('pie-chart-espera', 'figure')],
    [Input('dropdown-especialidad-espera', 'value'),
     Input('dropdown-modalidad-espera', 'value'),
     Input('dropdown-edad-espera', 'value'),
     Input('histogram-espera', 'clickData')]
)
def update_espera_charts(especialidad, modalidad, edad, clickData):
    filtered_df = df.copy()
    
    if especialidad != 'Todas':
        filtered_df = filtered_df[filtered_df['ESPECIALIDAD'] == especialidad]
    if modalidad != 'Todas':
        filtered_df = filtered_df[filtered_df['PRESENCIAL_REMOTO'] == modalidad]
    if edad != 'Todos':
        filtered_df = filtered_df[filtered_df['Rango de Edad'] == edad]
    
    fig_hist = px.histogram(
        filtered_df,
        x='RANGO_DIAS',
        category_orders={'RANGO_DIAS': ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90+"]},
        title=f'Distribución de Tiempos de Espera - {len(filtered_df)} pacientes',
        labels={'RANGO_DIAS': 'Rango de Días'},
        template='plotly_white'
    )
    
    if clickData is None:
        fig_pie = px.pie(names=[], values=[], title="Haga clic en una barra del histograma", height=500)
    else:
        selected_range = clickData['points'][0]['x']
        pie_df = filtered_df[filtered_df['RANGO_DIAS'] == selected_range].copy()
        
        if len(pie_df) > 0:
            top_especialidades = pie_df['ESPECIALIDAD'].value_counts().nlargest(5)
            pie_df['ESPECIALIDAD_AGRUPADA'] = pie_df['ESPECIALIDAD'].apply(
                lambda x: x if x in top_especialidades.index else 'Otras'
            )
            
            grouped = pie_df['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
            grouped.columns = ['ESPECIALIDAD', 'CUENTA']
            fig_pie = px.pie(
                grouped,
                names='ESPECIALIDAD',
                values='CUENTA',
                title=f"Top 5 Especialidades - Espera {selected_range} días ({len(pie_df)} pacientes)",
                height=600
            )
        else:
            fig_pie = px.pie(names=[], values=[], title="No hay datos para mostrar", height=500)
    
    return fig_hist, fig_pie

# App 3: Por Modalidad de Cita
app_modalidad = dash.Dash(__name__, server=server, url_base_pathname='/modalidad/')
app_modalidad.layout = html.Div([
    html.Div([
        html.H1("💻 Análisis de Modalidad de Atención", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            html.Div([
                html.Label("Filtrar por Rango de Edad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-edad-modalidad',
                    options=[{'label': 'Todos', 'value': 'Todos'}] + 
                            [{'label': edad, 'value': edad} for edad in ["Niño", "Adolescente", "Joven", "Adulto", "Adulto mayor"]],
                    value='Todos'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Umbral de Días de Espera:", style={'fontWeight': 'bold'}),
                dcc.Slider(
                    id='slider-umbral-modalidad',
                    min=0,
                    max=100,
                    value=30,
                    marks={i: str(i) for i in range(0, 101, 20)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'marginBottom': '20px'}),
        
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '20px'}),
    
    html.Div([
        dcc.Graph(id='pie-modalidad', style={'display': 'inline-block', 'width': '50%'}),
        dcc.Graph(id='metric-card-modalidad', style={'display': 'inline-block', 'width': '50%'})
    ]),
    dcc.Graph(id='bar-especialidad-modalidad')
])

@app_modalidad.callback(
    [Output('pie-modalidad', 'figure'),
     Output('bar-especialidad-modalidad', 'figure'),
     Output('metric-card-modalidad', 'figure')],
    [Input('dropdown-edad-modalidad', 'value'),
     Input('slider-umbral-modalidad', 'value'),
     Input('pie-modalidad', 'clickData')]
)
def update_modalidad_charts(edad, umbral, clickData):
    filtered_df = df.copy()
    
    if edad != 'Todos':
        filtered_df = filtered_df[filtered_df['Rango de Edad'] == edad]
    
    # Gráfico de pastel
    fig_pie = px.pie(
        filtered_df,
        names='PRESENCIAL_REMOTO',
        title=f'Distribución de Modalidades - {len(filtered_df)} citas',
        template='plotly_white'
    )
    
    # Métricas
    total_citas = len(filtered_df)
    citas_sobre_umbral = len(filtered_df[filtered_df['DIFERENCIA_DIAS'] > umbral])
    porcentaje_sobre_umbral = (citas_sobre_umbral / total_citas * 100) if total_citas > 0 else 0
    
    fig_metric = px.bar(
        x=['Total de Citas', f'Citas > {umbral} días', '% Sobre Umbral'],
        y=[total_citas, citas_sobre_umbral, porcentaje_sobre_umbral],
        title='Métricas de Tiempo de Espera',
        template='plotly_white'
    )
    
    # Gráfico de barras
    if clickData is None:
        fig_bar = px.bar(x=[], y=[], title="Seleccione una modalidad en el gráfico de pastel")
    else:
        modalidad = clickData['points'][0]['label']
        modal_df = filtered_df[filtered_df['PRESENCIAL_REMOTO'] == modalidad]
        mean_wait = modal_df.groupby('ESPECIALIDAD')['DIFERENCIA_DIAS'].mean().reset_index()
        mean_wait = mean_wait.sort_values(by='DIFERENCIA_DIAS', ascending=False)
        
        fig_bar = px.bar(
            mean_wait,
            x='ESPECIALIDAD',
            y='DIFERENCIA_DIAS',
            title=f"Tiempo Promedio de Espera por Especialidad - {modalidad}",
            labels={'DIFERENCIA_DIAS': 'Días de Espera Promedio'},
            template='plotly_white'
        )
        fig_bar.update_xaxis(tickangle=45)
    
    return fig_pie, fig_bar, fig_metric

# App 4: Por Estado de Seguro
app_seguro = dash.Dash(__name__, server=server, url_base_pathname='/asegurados/')
app_seguro.layout = html.Div([
    html.Div([
        html.H1("🛡️ Análisis de Estado del Seguro", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            html.Div([
                html.Label("Filtrar por Especialidad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-especialidad-seguro',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': esp, 'value': esp} for esp in sorted(df['ESPECIALIDAD'].unique())],
                    value='Todas'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Estado de Atención:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-atencion-seguro',
                    options=[{'label': 'Todos', 'value': 'Todos'}] + 
                            [{'label': estado, 'value': estado} for estado in df['ATENDIDO'].unique()],
                    value='Todos'
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'marginBottom': '20px'}),
        
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '20px'}),
    
    html.Div([
        dcc.Graph(id='pie-seguro', style={'display': 'inline-block', 'width': '50%'}),
        dcc.Graph(id='comparison-seguro', style={'display': 'inline-block', 'width': '50%'})
    ]),
    dcc.Graph(id='bar-espera-seguro')
])

@app_seguro.callback(
    [Output('pie-seguro', 'figure'),
     Output('bar-espera-seguro', 'figure'),
     Output('comparison-seguro', 'figure')],
    [Input('dropdown-especialidad-seguro', 'value'),
     Input('dropdown-atencion-seguro', 'value'),
     Input('pie-seguro', 'clickData')]
)
def update_seguro_charts(especialidad, atencion, clickData):
    filtered_df = df.dropna(subset=['SEGURO']).copy()
    
    if especialidad != 'Todas':
        filtered_df = filtered_df[filtered_df['ESPECIALIDAD'] == especialidad]
    if atencion != 'Todos':
        filtered_df = filtered_df[filtered_df['ATENDIDO'] == atencion]
    
    # Gráfico de pastel
    fig_pie = px.pie(
        filtered_df,
        names='SEGURO',
        title=f'Distribución por Estado de Seguro - {len(filtered_df)} pacientes',
        template='plotly_white'
    )
    
    # Comparación de tiempos de espera
    comparison_data = filtered_df.groupby('SEGURO')['DIFERENCIA_DIAS'].agg(['mean', 'median', 'std']).reset_index()
    fig_comparison = px.bar(
        comparison_data,
        x='SEGURO',
        y='mean',
        title='Tiempo Promedio de Espera por Estado de Seguro',
        labels={'mean': 'Días Promedio'},
        template='plotly_white'
    )
    
    # Gráfico de barras por sexo
    if clickData is None:
        fig_bar = px.bar(x=[], y=[], title="Seleccione un estado en el gráfico de pastel")
    else:
        seguro = clickData['points'][0]['label']
        seguro_df = filtered_df[filtered_df['SEGURO'] == seguro]
        mean_wait = seguro_df.groupby('SEXO')['DIFERENCIA_DIAS'].mean().reset_index()
        
        fig_bar = px.bar(
            mean_wait,
            x='SEXO',
            y='DIFERENCIA_DIAS',
            title=f"Tiempo Promedio de Espera por Sexo - {seguro}",
            labels={'DIFERENCIA_DIAS': 'Días de Espera Promedio'},
            template='plotly_white'
        )
    
    return fig_pie, fig_bar, fig_comparison

# App 5: Línea de Tiempo
app_tiempo = dash.Dash(__name__, server=server, url_base_pathname='/tiempo/')
app_tiempo.layout = html.Div([
    html.Div([
        html.H1("📈 Análisis Temporal de Citas", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            html.Div([
                html.Label("Filtrar por Especialidad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-especialidad-tiempo',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': esp, 'value': esp} for esp in sorted(df['ESPECIALIDAD'].unique())],
                    value='Todas'
                )
            ], style={'width': '32%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Modalidad:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-modalidad-tiempo',
                    options=[{'label': 'Todas', 'value': 'Todas'}] + 
                            [{'label': mod, 'value': mod} for mod in df['PRESENCIAL_REMOTO'].unique()],
                    value='Todas'
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'}),
            
            html.Div([
                html.Label("Estado de Atención:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-estado-tiempo',
                    options=[{'label': 'Todos', 'value': 'Todos'}] + 
                            [{'label': estado, 'value': estado} for estado in df['ATENDIDO'].unique()],
                    value='Todos'
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginLeft': '2%'})
        ], style={'marginBottom': '20px'}),
        
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'margin': '20px'}),
    
    dcc.Graph(id='grafico-lineal'),
    html.Div([
        dcc.Graph(id='grafico-pie-especialidades', style={'display': 'inline-block', 'width': '50%'}),
        dcc.Graph(id='grafico-pie-atencion', style={'display': 'inline-block', 'width': '50%'})
    ])
])

@app_tiempo.callback(
    [Output('grafico-lineal', 'figure'),
     Output('grafico-pie-especialidades', 'figure'),
     Output('grafico-pie-atencion', 'figure')],
    [Input('dropdown-especialidad-tiempo', 'value'),
     Input('dropdown-modalidad-tiempo', 'value'),
     Input('dropdown-estado-tiempo', 'value'),
     Input('grafico-lineal', 'clickData')]
)
def update_tiempo_charts(especialidad, modalidad, estado, clickData):
    filtered_df = df.copy()
    
    if especialidad != 'Todas':
        filtered_df = filtered_df[filtered_df['ESPECIALIDAD'] == especialidad]
    if modalidad != 'Todas':
        filtered_df = filtered_df[filtered_df['PRESENCIAL_REMOTO'] == modalidad]
    if estado != 'Todos':
        filtered_df = filtered_df[filtered_df['ATENDIDO'] == estado]
    
    # Línea de tiempo
    citas_por_mes = filtered_df.groupby('MES').size().reset_index(name='CANTIDAD_CITAS')
    fig_lineal = px.line(
        citas_por_mes, 
        x='MES', 
        y='CANTIDAD_CITAS', 
        markers=True,
        title=f'Evolución Temporal de Citas - {len(filtered_df)} total',
        template='plotly_white'
    )
    fig_lineal.update_xaxis(tickangle=45)
    
    # Gráficos de pastel
    if clickData is None:
        fig_especialidades = px.pie(names=[], values=[], title="Seleccione un mes en la línea de tiempo")
        fig_atencion = px.pie(names=[], values=[], title="Seleccione un mes en la línea de tiempo")
    else:
        mes_seleccionado = clickData['points'][0]['x']
       df_mes = filtered_df[filtered_df['MES'] == mes_seleccionado]
       
       if len(df_mes) > 0:
           # Gráfico de especialidades
           top_especialidades = df_mes['ESPECIALIDAD'].value_counts().nlargest(5)
           df_mes_copy = df_mes.copy()
           df_mes_copy['ESPECIALIDAD_AGRUPADA'] = df_mes_copy['ESPECIALIDAD'].apply(
               lambda x: x if x in top_especialidades.index else 'Otras'
           )
           
           grouped = df_mes_copy['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
           grouped.columns = ['ESPECIALIDAD', 'CUENTA']
           
           fig_especialidades = px.pie(
               grouped, 
               names='ESPECIALIDAD', 
               values='CUENTA', 
               title=f'Top 5 Especialidades - {mes_seleccionado} ({len(df_mes)} citas)'
           )
           
           # Gráfico de atención
           fig_atencion = px.pie(
               df_mes, 
               names='ATENDIDO', 
               title=f'Estado de Atención - {mes_seleccionado}'
           )
       else:
           fig_especialidades = px.pie(names=[], values=[], title="No hay datos para este mes")
           fig_atencion = px.pie(names=[], values=[], title="No hay datos para este mes")
   
   return fig_lineal, fig_especialidades, fig_atencion

# Ejecutar el servidor
if __name__ == '__main__':
   server.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
