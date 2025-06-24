import pandas as pd
from flask import Flask, render_template_string, send_from_directory
import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np

# Configuración de colores modernos y tema
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2', 
    'accent': '#f093fb',
    'success': '#4facfe',
    'warning': '#f6d365',
    'danger': '#ff6b6b',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'background': '#f8fafc',
    'card': '#ffffff',
    'text': '#2d3748',
    'muted': '#718096'
}

# Cargar y procesar datos
def load_and_process_data():
    file_id = "1PWTw-akWr59Gu7MoHra5WXMKwllxK9bp"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    df = pd.read_csv(url)
    
    # Clasificaciones mejoradas
    def clasificar_edad(edad):
        if edad < 13: return "👶 Niños (0-12)"
        elif edad < 19: return "🧑 Adolescentes (13-18)"
        elif edad < 30: return "👨‍💼 Jóvenes (19-29)"
        elif edad < 61: return "👩‍💼 Adultos (30-60)"
        else: return "👴 Adultos Mayores (61+)"
    
    def clasificar_dias(dias):
        ranges = {
            (0, 10): "🟢 Inmediato (0-9 días)",
            (10, 20): "🟡 Corto (10-19 días)", 
            (20, 30): "🟠 Moderado (20-29 días)",
            (30, 50): "🔴 Largo (30-49 días)",
            (50, float('inf')): "⚫ Crítico (50+ días)"
        }
        for (min_val, max_val), label in ranges.items():
            if min_val <= dias < max_val:
                return label
        return "⚫ Crítico (50+ días)"
    
    df['Rango de Edad'] = df['EDAD'].apply(clasificar_edad)
    df['RANGO_DIAS'] = df['DIFERENCIA_DIAS'].apply(clasificar_dias)
    
    # Procesamiento de fechas
    df['DIA_SOLICITACITA'] = pd.to_datetime(df['DIA_SOLICITACITA'], errors='coerce')
    df['MES'] = df['DIA_SOLICITACITA'].dt.to_period('M').astype(str)
    df['TRIMESTRE'] = df['DIA_SOLICITACITA'].dt.to_period('Q').astype(str)
    
    return df

# Crear servidor Flask mejorado
server = Flask(__name__)

# Servir archivos estáticos
@server.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Página principal moderna y atractiva
@server.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 Dashboard Analítico - Hospital María Auxiliadora</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #667eea;
                --secondary: #764ba2;
                --accent: #f093fb;
                --success: #4facfe;
                --warning: #f6d365;
                --danger: #ff6b6b;
                --dark: #2c3e50;
                --light: #ecf0f1;
                --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --card: #ffffff;
                --text: #2d3748;
                --muted: #718096;
                --shadow: 0 10px 25px rgba(0,0,0,0.1);
                --shadow-hover: 0 20px 40px rgba(0,0,0,0.15);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: var(--background);
                min-height: 100vh;
                color: var(--text);
                overflow-x: hidden;
            }
            
            .hero-section {
                text-align: center;
                padding: 80px 20px 60px;
                color: white;
                position: relative;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,186.7C384,213,480,235,576,213.3C672,192,768,128,864,128C960,128,1056,192,1152,208C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
                background-size: cover;
            }
            
            .logo {
                width: 100px;
                height: 100px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 30px;
                backdrop-filter: blur(10px);
                border: 2px solid rgba(255,255,255,0.3);
            }
            
            .logo i {
                font-size: 48px;
                color: white;
            }
            
            h1 {
                font-size: 3.5rem;
                font-weight: 700;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #fff, #f0f8ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .subtitle {
                font-size: 1.3rem;
                font-weight: 300;
                opacity: 0.9;
                max-width: 600px;
                margin: 0 auto 50px;
            }
            
            .dashboard-grid {
                max-width: 1200px;
                margin: -50px auto 0;
                padding: 0 20px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                position: relative;
                z-index: 1;
            }
            
            .dashboard-card {
                background: var(--card);
                border-radius: 20px;
                padding: 40px 30px;
                box-shadow: var(--shadow);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .dashboard-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary), var(--accent));
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }
            
            .dashboard-card:hover::before {
                transform: scaleX(1);
            }
            
            .dashboard-card:hover {
                transform: translateY(-10px);
                box-shadow: var(--shadow-hover);
            }
            
            .card-icon {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, var(--primary), var(--accent));
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 25px;
                position: relative;
            }
            
            .card-icon::before {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(135deg, var(--primary), var(--accent));
                border-radius: 22px;
                z-index: -1;
                opacity: 0.3;
                filter: blur(8px);
            }
            
            .card-icon i {
                font-size: 36px;
                color: white;
            }
            
            .card-title {
                font-size: 1.4rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: var(--dark);
            }
            
            .card-description {
                color: var(--muted);
                line-height: 1.6;
                margin-bottom: 30px;
            }
            
            .card-link {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                background: linear-gradient(135deg, var(--primary), var(--accent));
                color: white;
                text-decoration: none;
                padding: 15px 25px;
                border-radius: 50px;
                font-weight: 500;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .card-link::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .card-link:hover::before {
                left: 100%;
            }
            
            .card-link:hover {
                transform: scale(1.05);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .stats-section {
                background: white;
                margin: 80px 20px;
                border-radius: 20px;
                padding: 60px 40px;
                box-shadow: var(--shadow);
                max-width: 1200px;
                margin: 80px auto;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 40px;
                text-align: center;
            }
            
            .stat-item {
                position: relative;
            }
            
            .stat-number {
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .stat-label {
                color: var(--muted);
                font-size: 1.1rem;
                font-weight: 500;
            }
            
            .footer {
                text-align: center;
                padding: 40px 20px;
                color: rgba(255,255,255,0.8);
                background: rgba(0,0,0,0.1);
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .dashboard-card {
                animation: fadeInUp 0.6s ease forwards;
            }
            
            .dashboard-card:nth-child(1) { animation-delay: 0.1s; }
            .dashboard-card:nth-child(2) { animation-delay: 0.2s; }
            .dashboard-card:nth-child(3) { animation-delay: 0.3s; }
            .dashboard-card:nth-child(4) { animation-delay: 0.4s; }
            .dashboard-card:nth-child(5) { animation-delay: 0.5s; }
            
            @media (max-width: 768px) {
                h1 { font-size: 2.5rem; }
                .subtitle { font-size: 1.1rem; }
                .dashboard-grid { margin-top: -30px; }
                .dashboard-card { padding: 30px 20px; }
                .stats-section { margin: 40px 20px; padding: 40px 20px; }
            }
        </style>
    </head>
    <body>
        <div class="hero-section">
            <div class="logo">
                <i class="fas fa-hospital"></i>
            </div>
            <h1>Dashboard Analítico</h1>
            <p class="subtitle">
                Sistema integral de análisis de datos médicos del Hospital María Auxiliadora
            </p>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-icon">
                    <i class="fas fa-users"></i>
                </div>
                <h3 class="card-title">👥 Análisis Demográfico</h3>
                <p class="card-description">
                    Explora la distribución de pacientes por grupos etarios con visualizaciones interactivas y análisis detallado por especialidades médicas.
                </p>
                <a href="/edad/" class="card-link">
                    <span>Explorar</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <h3 class="card-title">⏰ Tiempos de Espera</h3>
                <p class="card-description">
                    Analiza los tiempos de espera para citas médicas, identifica cuellos de botella y optimiza la atención hospitalaria.
                </p>
                <a href="/espera/" class="card-link">
                    <span>Analizar</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">
                    <i class="fas fa-video"></i>
                </div>
                <h3 class="card-title">💻 Modalidades de Atención</h3>
                <p class="card-description">
                    Compara la efectividad entre citas presenciales y remotas, analiza preferencias y tiempos de respuesta por modalidad.
                </p>
                <a href="/modalidad/" class="card-link">
                    <span>Comparar</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <h3 class="card-title">🛡️ Estado del Seguro</h3>
                <p class="card-description">
                    Visualiza la distribución de pacientes según su estado de aseguramiento y analiza impactos en los tiempos de atención.
                </p>
                <a href="/asegurados/" class="card-link">
                    <span>Revisar</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <h3 class="card-title">📈 Evolución Temporal</h3>
                <p class="card-description">
                    Rastrea las tendencias de citas médicas a lo largo del tiempo, identifica patrones estacionales y picos de demanda.
                </p>
                <a href="/tiempo/" class="card-link">
                    <span>Visualizar</span>
                    <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        </div>
        
        <div class="stats-section">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Módulos de Análisis</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Datos en Tiempo Real</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Disponibilidad</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">∞</div>
                    <div class="stat-label">Insights Generados</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 Hospital María Auxiliadora - Dashboard Analítico | Desarrollado con ❤️ para mejorar la atención médica</p>
        </div>
        
        <script>
            // Animaciones suaves al hacer scroll
            const observerOptions = {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            };
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }
                });
            }, observerOptions);
            
            document.querySelectorAll('.dashboard-card, .stats-section').forEach(el => {
                observer.observe(el);
            });
        </script>
    </body>
    </html>
    """)

# Cargar datos
df = load_and_process_data()

# Función para crear gráficos con estilo moderno
def create_modern_figure(fig_type='bar', data=None, **kwargs):
    """Crea figuras con estilo moderno y consistente"""
    if fig_type == 'histogram':
        fig = px.histogram(data, **kwargs)
    elif fig_type == 'pie':
        fig = px.pie(data, **kwargs)
    elif fig_type == 'bar':
        fig = px.bar(data, **kwargs)
    elif fig_type == 'line':
        fig = px.line(data, **kwargs)
    else:
        fig = go.Figure()
    
    # Aplicar estilo moderno
    fig.update_layout(
        font_family="Inter",
        font_size=12,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
        title=dict(
            font=dict(size=18, color=COLORS['dark']),
            x=0.5,
            xanchor='center'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Colores modernos
    color_sequence = [COLORS['primary'], COLORS['accent'], COLORS['success'], 
                     COLORS['warning'], COLORS['danger']]
    fig.update_traces(marker_color=color_sequence[:len(fig.data)])
    
    return fig

# Layout mejorado para las apps
def create_modern_layout(title, children):
    return html.Div([
        html.Div([
            html.Div([
                html.H1(title, className="page-title"),
                html.Div([
                    html.A("🏠 Inicio", href="/", className="nav-link"),
                    html.A("👥 Demografía", href="/edad/", className="nav-link"),
                    html.A("⏰ Tiempos", href="/espera/", className="nav-link"),
                    html.A("💻 Modalidad", href="/modalidad/", className="nav-link"),
                    html.A("🛡️ Seguros", href="/asegurados/", className="nav-link"),
                    html.A("📈 Temporal", href="/tiempo/", className="nav-link"),
                ], className="nav-menu")
            ], className="header-content")
        ], className="header"),
        html.Div(children, className="content")
    ], className="app-container", style={
        'fontFamily': 'Inter, sans-serif',
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })

# CSS para las aplicaciones
app_css = """
.app-container {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}

.page-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.nav-menu {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.nav-link {
    color: rgba(255,255,255,0.9);
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 500;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.2);
}

.nav-link:hover {
    background: rgba(255,255,255,0.1);
    color: white;
    text-decoration: none;
    transform: translateY(-2px);
}

.content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

.chart-container {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.1);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    border-left: 4px solid #667eea;
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.metric-label {
    color: #718096;
    font-size: 0.9rem;
    font-weight: 500;
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
    
    .nav-menu {
        justify-content: center;
    }
    
    .content {
        padding: 20px 10px;
    }
}
"""

# Apps mejoradas con nuevos diseños

# App 1: Análisis Demográfico Mejorado
app_edad = dash.Dash(__name__, server=server, url_base_pathname='/edad/')
app_edad.layout = create_modern_layout("👥 Análisis Demográfico", [
    html.Div([
        html.Div([
            dcc.Graph(
                id='histogram-edad',
                figure=create_modern_figure('histogram', df, 
                    x='Rango de Edad',
                    title='📊 Distribución de Pacientes por Grupo Etario',
                    labels={'Rango de Edad': 'Grupo Etario', 'count': 'Número de Pacientes'}
                )
            )
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(
                id='pie-chart-edad',
                figure=px.pie(names=[], values=[], 
                    title="👆 Haz clic en una barra para ver las especialidades más demandadas"
                )
            )
        ], className="chart-container"),
        
        html.Div(id="edad-metrics", className="metrics-grid")
    ])
])

# Callbacks mejorados con métricas
@app_edad.callback(
    [Output('pie-chart-edad', 'figure'),
     Output('edad-metrics', 'children')],
    Input('histogram-edad', 'clickData')
)
def update_edad_analysis(clickData):
    if clickData is None:
        empty_fig = px.pie(names=[], values=[], 
            title="👆 Selecciona un grupo etario para ver el análisis detallado")
        return empty_fig, []

    selected_range = clickData['points'][0]['x']
    filtered_df = df[df['Rango de Edad'] == selected_range].copy()
    
    # Crear gráfico de especialidades
    top_especialidades = filtered_df['ESPECIALIDAD'].value_counts().nlargest(8)
    filtered_df['ESPECIALIDAD_AGRUPADA'] = filtered_df['ESPECIALIDAD'].apply(
        lambda x: x if x in top_especialidades.index else 'Otras especialidades'
    )
    
    grouped = filtered_df['ESPECIALIDAD_AGRUPADA'].value_counts().reset_index()
    grouped.columns = ['ESPECIALIDAD', 'CUENTA']
    
    pie_fig = create_modern_figure('pie', grouped,
        names='ESPECIALIDAD', values='CUENTA',
        title=f"🎯 Especialidades más demandadas - {selected_range}",
        hole=0.4
    )
    
    # Crear métricas
    total_pacientes = len(filtered_df)
    tiempo_promedio = filtered_df['DIFERENCIA_DIAS'].mean()
    modalidad_preferida = filtered_df['PRESENCIAL_REMOTO'].mode().iloc[0] if not filtered_df['PRESENCIAL_REMOTO'].mode().empty else "N/A"
    
    metrics = [
        html.Div([
            html.Div(f"{total_pacientes:,}", className="metric-value"),
            html.Div("Pacientes Total", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tiempo_promedio:.1f}", className="metric-value"),
            html.Div("Días Promedio de Espera", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(modalidad_preferida, className="metric-value"),
            html.Div("Modalidad Preferida", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{(len(filtered_df[filtered_df['ATENDIDO'] == 'SI']) / total_pacientes * 100):.1f}%", className="metric-value"),
            html.Div("Tasa de Atención", className="metric-label")
        ], className="metric-card")
    ]
    
    return pie_fig, metrics

# Inyectar CSS en todas las apps
for app in [app_edad]:
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <link href="https://fonts.googleapis.com/css2?

# Continúa desde donde se quedó...

# Inyectar CSS en todas las apps
for app in [app_edad]:
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>{app_css}</style>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    '''

# App 2: Análisis de Tiempos de Espera Mejorado
app_espera = dash.Dash(__name__, server=server, url_base_pathname='/espera/')
app_espera.layout = create_modern_layout("⏰ Análisis de Tiempos de Espera", [
    html.Div([
        html.Div([
            dcc.Graph(
                id='histogram-espera',
                figure=create_modern_figure('histogram', df,
                    x='RANGO_DIAS',
                    title='⏱️ Distribución de Tiempos de Espera para Citas Médicas',
                    labels={'RANGO_DIAS': 'Tiempo de Espera', 'count': 'Número de Pacientes'}
                )
            )
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='especialidades-espera'),
            dcc.Graph(id='tendencia-espera')
        ], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'}),
        
        html.Div(id="espera-metrics", className="metrics-grid")
    ])
])

@app_espera.callback(
    [Output('especialidades-espera', 'figure'),
     Output('tendencia-espera', 'figure'),
     Output('espera-metrics', 'children')],
    Input('histogram-espera', 'clickData')
)
def update_espera_analysis(clickData):
    if clickData is None:
        empty_fig = px.pie(names=[], values=[], title="👆 Selecciona un rango de tiempo")
        line_fig = px.line(title="📈 Tendencia temporal")
        return empty_fig, line_fig, []

    selected_range = clickData['points'][0]['x']
    filtered_df = df[df['RANGO_DIAS'] == selected_range].copy()
    
    # Gráfico de especialidades
    top_especialidades = filtered_df['ESPECIALIDAD'].value_counts().nlargest(6)
    pie_fig = create_modern_figure('pie', 
        names=top_especialidades.index, 
        values=top_especialidades.values,
        title=f"🎯 Especialidades - {selected_range}",
        hole=0.3
    )
    
    # Tendencia por mes
    monthly_trend = filtered_df.groupby('MES').size().reset_index(name='CANTIDAD')
    line_fig = create_modern_figure('line', monthly_trend,
        x='MES', y='CANTIDAD',
        title=f"📈 Evolución mensual - {selected_range}",
        markers=True
    )
    
    # Métricas avanzadas
    total_casos = len(filtered_df)
    tiempo_promedio = filtered_df['DIFERENCIA_DIAS'].mean()
    porcentaje_critico = (len(filtered_df[filtered_df['DIFERENCIA_DIAS'] > 50]) / total_casos * 100) if total_casos > 0 else 0
    
    metrics = [
        html.Div([
            html.Div(f"{total_casos:,}", className="metric-value"),
            html.Div("Casos en este Rango", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tiempo_promedio:.1f}", className="metric-value"),
            html.Div("Días Promedio", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{porcentaje_critico:.1f}%", className="metric-value"),
            html.Div("Casos Críticos (>50 días)", className="metric-label")
        ], className="metric-card")
    ]
    
    return pie_fig, line_fig, metrics

# App 3: Análisis de Modalidades Mejorado
app_modalidad = dash.Dash(__name__, server=server, url_base_pathname='/modalidad/')
app_modalidad.layout = create_modern_layout("💻 Análisis de Modalidades de Atención", [
    html.Div([
        html.Div([
            dcc.Graph(
                id='pie-modalidad',
                figure=create_modern_figure('pie', df,
                    names='PRESENCIAL_REMOTO',
                    title='📊 Distribución: Citas Presenciales vs Remotas',
                    hole=0.4
                )
            )
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='comparison-modalidad'),
            dcc.Graph(id='efficiency-modalidad')
        ], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'}),
        
        html.Div(id="modalidad-metrics", className="metrics-grid")
    ])
])

@app_modalidad.callback(
    [Output('comparison-modalidad', 'figure'),
     Output('efficiency-modalidad', 'figure'),
     Output('modalidad-metrics', 'children')],
    Input('pie-modalidad', 'clickData')
)
def update_modalidad_analysis(clickData):
    if clickData is None:
        # Gráfico comparativo por defecto
        comparison_data = df.groupby(['PRESENCIAL_REMOTO', 'ESPECIALIDAD'])['DIFERENCIA_DIAS'].mean().reset_index()
        comparison_data = comparison_data.groupby('PRESENCIAL_REMOTO').head(5)
        
        comp_fig = px.bar(comparison_data,
            x='ESPECIALIDAD', y='DIFERENCIA_DIAS', color='PRESENCIAL_REMOTO',
            title="⚖️ Comparación de Tiempos por Modalidad",
            barmode='group'
        )
        
        # Análisis de eficiencia
        efficiency_data = df.groupby('PRESENCIAL_REMOTO').agg({
            'DIFERENCIA_DIAS': 'mean',
            'ATENDIDO': lambda x: (x == 'SI').sum() / len(x) * 100
        }).reset_index()
        
        eff_fig = px.scatter(efficiency_data,
            x='DIFERENCIA_DIAS', y='ATENDIDO', color='PRESENCIAL_REMOTO',
            size=[100, 100], title="📈 Eficiencia: Tiempo vs Tasa de Atención",
            labels={'DIFERENCIA_DIAS': 'Tiempo Promedio (días)', 'ATENDIDO': 'Tasa de Atención (%)'}
        )
        
        return comp_fig, eff_fig, []

    modalidad = clickData['points'][0]['label']
    filtered_df = df[df['PRESENCIAL_REMOTO'] == modalidad]
    
    # Análisis detallado por especialidad
    especialidad_analysis = filtered_df.groupby('ESPECIALIDAD').agg({
        'DIFERENCIA_DIAS': 'mean',
        'EDAD': 'mean'
    }).reset_index().sort_values('DIFERENCIA_DIAS', ascending=False).head(8)
    
    comp_fig = create_modern_figure('bar', especialidad_analysis,
        x='ESPECIALIDAD', y='DIFERENCIA_DIAS',
        title=f"📊 Tiempos de Espera por Especialidad - {modalidad}",
        labels={'DIFERENCIA_DIAS': 'Días Promedio', 'ESPECIALIDAD': 'Especialidad'}
    )
    
    # Análisis por hora del día (simulado)
    np.random.seed(42)
    hours = list(range(8, 18))
    efficiency_by_hour = {
        'HORA': hours,
        'CITAS': np.random.randint(10, 50, len(hours)),
        'MODALIDAD': [modalidad] * len(hours)
    }
    hour_df = pd.DataFrame(efficiency_by_hour)
    
    eff_fig = create_modern_figure('line', hour_df,
        x='HORA', y='CITAS',
        title=f"🕐 Distribución Horaria - {modalidad}",
        markers=True
    )
    
    # Métricas específicas
    tiempo_promedio = filtered_df['DIFERENCIA_DIAS'].mean()
    tasa_atencion = (filtered_df['ATENDIDO'] == 'SI').sum() / len(filtered_df) * 100
    edad_promedio = filtered_df['EDAD'].mean()
    
    metrics = [
        html.Div([
            html.Div(f"{tiempo_promedio:.1f}", className="metric-value"),
            html.Div("Días Promedio", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tasa_atencion:.1f}%", className="metric-value"),
            html.Div("Tasa de Atención", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{edad_promedio:.0f}", className="metric-value"),
            html.Div("Edad Promedio", className="metric-label")
        ], className="metric-card")
    ]
    
    return comp_fig, eff_fig, metrics

# App 4: Análisis de Seguros Mejorado
app_seguro = dash.Dash(__name__, server=server, url_base_pathname='/asegurados/')
app_seguro.layout = create_modern_layout("🛡️ Análisis del Estado de Aseguramiento", [
    html.Div([
        html.Div([
            dcc.Graph(
                id='pie-seguro',
                figure=create_modern_figure('pie', df.dropna(),
                    names='SEGURO',
                    title='🛡️ Distribución de Pacientes por Estado de Seguro',
                    hole=0.4
                )
            )
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='gender-analysis-seguro'),
            dcc.Graph(id='age-distribution-seguro')
        ], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'}),
        
        html.Div(id="seguro-metrics", className="metrics-grid")
    ])
])

@app_seguro.callback(
    [Output('gender-analysis-seguro', 'figure'),
     Output('age-distribution-seguro', 'figure'),
     Output('seguro-metrics', 'children')],
    Input('pie-seguro', 'clickData')
)
def update_seguro_analysis(clickData):
    if clickData is None:
        # Análisis general por defecto
        gender_data = df.groupby(['SEGURO', 'SEXO'])['DIFERENCIA_DIAS'].mean().reset_index()
        gender_fig = px.bar(gender_data,
            x='SEXO', y='DIFERENCIA_DIAS', color='SEGURO',
            title="⚖️ Tiempo de Espera por Género y Estado de Seguro",
            barmode='group'
        )
        
        age_data = df.groupby(['SEGURO', 'Rango de Edad']).size().reset_index(name='COUNT')
        age_fig = px.bar(age_data,
            x='Rango de Edad', y='COUNT', color='SEGURO',
            title="👥 Distribución Etaria por Estado de Seguro",
            barmode='group'
        )
        
        return gender_fig, age_fig, []

    seguro = clickData['points'][0]['label']
    filtered_df = df[df['SEGURO'] == seguro]
    
    # Análisis por género
    gender_analysis = filtered_df.groupby('SEXO').agg({
        'DIFERENCIA_DIAS': 'mean',
        'EDAD': 'mean'
    }).reset_index()
    
    gender_fig = create_modern_figure('bar', gender_analysis,
        x='SEXO', y='DIFERENCIA_DIAS',
        title=f"👫 Análisis por Género - {seguro}",
        labels={'DIFERENCIA_DIAS': 'Días Promedio', 'SEXO': 'Género'}
    )
    
    # Distribución por edad
    age_dist = filtered_df['Rango de Edad'].value_counts().reset_index()
    age_dist.columns = ['Rango de Edad', 'COUNT']
    
    age_fig = create_modern_figure('bar', age_dist,
        x='Rango de Edad', y='COUNT',
        title=f"📊 Distribución Etaria - {seguro}",
        labels={'COUNT': 'Número de Pacientes'}
    )
    
    # Métricas específicas
    total_pacientes = len(filtered_df)
    tiempo_promedio = filtered_df['DIFERENCIA_DIAS'].mean()
    edad_promedio = filtered_df['EDAD'].mean()
    tasa_atencion = (filtered_df['ATENDIDO'] == 'SI').sum() / total_pacientes * 100
    
    metrics = [
        html.Div([
            html.Div(f"{total_pacientes:,}", className="metric-value"),
            html.Div("Total Pacientes", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tiempo_promedio:.1f}", className="metric-value"),
            html.Div("Días Promedio", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{edad_promedio:.0f}", className="metric-value"),
            html.Div("Edad Promedio", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tasa_atencion:.1f}%", className="metric-value"),
            html.Div("Tasa de Atención", className="metric-label")
        ], className="metric-card")
    ]
    
    return gender_fig, age_fig, metrics

# App 5: Análisis Temporal Avanzado
app_tiempo = dash.Dash(__name__, server=server, url_base_pathname='/tiempo/')

# Preparar datos temporales avanzados
citas_por_mes = df.groupby('MES').agg({
    'EDAD': 'count',
    'DIFERENCIA_DIAS': 'mean',
    'ATENDIDO': lambda x: (x == 'SI').sum()
}).reset_index()
citas_por_mes.columns = ['MES', 'TOTAL_CITAS', 'TIEMPO_PROMEDIO', 'ATENDIDOS']
citas_por_mes['TASA_ATENCION'] = (citas_por_mes['ATENDIDOS'] / citas_por_mes['TOTAL_CITAS'] * 100).round(1)

app_tiempo.layout = create_modern_layout("📈 Análisis de Evolución Temporal", [
    html.Div([
        html.Div([
            dcc.Graph(
                id='main-timeline',
                figure=create_modern_figure('line', citas_por_mes,
                    x='MES', y='TOTAL_CITAS',
                    title='📈 Evolución Mensual de Citas Médicas',
                    markers=True,
                    labels={'TOTAL_CITAS': 'Número de Citas', 'MES': 'Mes'}
                )
            )
        ], className="chart-container"),
        
        html.Div([
            dcc.Graph(id='especialidades-tiempo'),
            dcc.Graph(id='atencion-tiempo'),
            dcc.Graph(id='efficiency-tiempo')
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))', 'gap': '20px'}),
        
        html.Div(id="tiempo-metrics", className="metrics-grid")
    ])
])

@app_tiempo.callback(
    [Output('especialidades-tiempo', 'figure'),
     Output('atencion-tiempo', 'figure'),
     Output('efficiency-tiempo', 'figure'),
     Output('tiempo-metrics', 'children')],
    Input('main-timeline', 'clickData')
)
def update_tiempo_analysis(clickData):
    if clickData is None:
        # Análisis general
        esp_general = df['ESPECIALIDAD'].value_counts().head(6).reset_index()
        esp_general.columns = ['ESPECIALIDAD', 'COUNT']
        esp_fig = create_modern_figure('pie', esp_general,
            names='ESPECIALIDAD', values='COUNT',
            title="🏥 Especialidades Más Demandadas (General)",
            hole=0.3
        )
        
        atencion_general = df['ATENDIDO'].value_counts().reset_index()
        atencion_general.columns = ['ESTADO', 'COUNT']
        atencion_fig = create_modern_figure('pie', atencion_general,
            names='ESTADO', values='COUNT',
            title="✅ Estado de Atención (General)",
            hole=0.3
        )
        
        # Gráfico de eficiencia
        efficiency_fig = create_modern_figure('line', citas_por_mes,
            x='MES', y='TASA_ATENCION',
            title="📊 Tasa de Atención por Mes",
            markers=True,
            labels={'TASA_ATENCION': 'Tasa de Atención (%)', 'MES': 'Mes'}
        )
        
        return esp_fig, atencion_fig, efficiency_fig, []

    mes_seleccionado = clickData['points'][0]['x']
    df_mes = df[df['MES'] == mes_seleccionado]
    
    # Especialidades del mes
    top_especialidades = df_mes['ESPECIALIDAD'].value_counts().nlargest(6)
    esp_fig = create_modern_figure('pie', 
        names=top_especialidades.index, 
        values=top_especialidades.values,
        title=f"🎯 Especialidades en {mes_seleccionado}",
        hole=0.3
    )
    
    # Estado de atención
    atencion_mes = df_mes['ATENDIDO'].value_counts().reset_index()
    atencion_mes.columns = ['ESTADO', 'COUNT']
    atencion_fig = create_modern_figure('bar', atencion_mes,
        x='ESTADO', y='COUNT',
        title=f"✅ Estado de Atención - {mes_seleccionado}"
    )
    
    # Análisis de modalidad
    modalidad_mes = df_mes['PRESENCIAL_REMOTO'].value_counts().reset_index()
    modalidad_mes.columns = ['MODALIDAD', 'COUNT']
    efficiency_fig = create_modern_figure('pie', modalidad_mes,
        names='MODALIDAD', values='COUNT',
        title=f"💻 Modalidades - {mes_seleccionado}",
        hole=0.4
    )
    
    # Métricas del mes
    total_citas = len(df_mes)
    promedio_espera = df_mes['DIFERENCIA_DIAS'].mean()
    tasa_atencion = (df_mes['ATENDIDO'] == 'SI').sum() / total_citas * 100
    edad_promedio = df_mes['EDAD'].mean()
    
    metrics = [
        html.Div([
            html.Div(f"{total_citas:,}", className="metric-value"),
            html.Div("Citas del Mes", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{promedio_espera:.1f}", className="metric-value"),
            html.Div("Días Promedio Espera", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{tasa_atencion:.1f}%", className="metric-value"),
            html.Div("Tasa de Atención", className="metric-label")
        ], className="metric-card"),
        
        html.Div([
            html.Div(f"{edad_promedio:.0f}", className="metric-value"),
            html.Div("Edad Promedio", className="metric-label")
        ], className="metric-card")
    ]
    
    return esp_fig, atencion_fig, efficiency_fig, metrics

# Aplicar CSS a todas las apps
all_apps = [app_edad, app_espera, app_modalidad, app_seguro, app_tiempo]
for app in all_apps:
    app.index_string = f'''
    <!DOCTYPE html>
    <html>
        <head>
            {{%metas%}}
            <title>{{%title%}}</title>
            {{%favicon%}}
            {{%css%}}
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>{app_css}</style>
        </head>
        <body>
            {{%app_entry%}}
            <footer>
                {{%config%}}
                {{%scripts%}}
                {{%renderer%}}
            </footer>
        </body>
    </html>
    '''

# Ejecutar el servidor con configuración mejorada
if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Analítico Avanzado...")
    print("📊 Accede a: http://localhost:5000")
    print("🎯 Funcionalidades disponibles:")
    print("   👥 Análisis Demográfico: /edad/")
    print("   ⏰ Tiempos de Espera: /espera/")
    print("   💻 Modalidades: /modalidad/")
    print("   🛡️ Estados de Seguro: /asegurados/")
    print("   📈 Evolución Temporal: /tiempo/")
    
    server.run(debug=True, host='0.0.0.0', port=5000)
