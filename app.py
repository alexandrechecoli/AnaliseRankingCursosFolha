import streamlit as st
import pandas as pd
import plotly.express as px


'streamlit run c:/Users/x-eco/Downloads/AnaliseCursos/app.py'
# ----------------------------------------------------------------------
# CONFIGURAÇÃO DO APP
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard UFPR – Engenharias",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------
# ESTILO CUSTOMIZADO (CSS)
# ----------------------------------------------------------------------
st.markdown("""
<style>
/* Cards */
.metric-card {
    background-color: #4CAF50;        /* COR DO FUNDO DO CARD */
    border-radius: 12px;              /* Cantos arredondados */
    padding: 20px;                    /* Espaçamento interno */
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1); /* Sombra suave */
    text-align: center;               /* Centralizar texto */
}

.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #4CAF50;
}
.metric-label {
    font-size: 15px;
    color: #ddd;
}

/* Divisor estilizado */
.section-divider {
    border-top: 1px solid #333;
    margin-top: 25px;
    margin-bottom: 25px;
}

/* Títulos */
h1, h2, h3 {
    color: #4CAF50 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CARREGAR DADOS
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/cursos.csv", sep=";")

    # Limpa valores como "201-250"
    df["Posição Nota dos concluintes"] = (
        df["Posição Nota dos concluintes"].astype(str).str.replace("201-250", "225")
    )
    df["Posição Nota dos concluintes"] = pd.to_numeric(df["Posição Nota dos concluintes"], errors="coerce")

    return df

df = load_data()

# ----------------------------------------------------------------------
# TÍTULO PRINCIPAL
# ----------------------------------------------------------------------
st.title("🏛️ Dashboard dos Cursos de Engenharia – UFPR")
st.subheader("Análise histórica de desempenho no Ranking da Folha")
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# FILTROS SIDEBAR
# ----------------------------------------------------------------------
st.sidebar.header("🔎 Filtros")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df["Ano"].unique()),
    default=sorted(df["Ano"].unique())
)

cursos = st.sidebar.multiselect(
    "Curso",
    sorted(df["Curso"].unique()),
    default=sorted(df["Curso"].unique())
)

df_filtered = df[(df["Ano"].isin(anos)) & (df["Curso"].isin(cursos))]

# ----------------------------------------------------------------------
# CARDS DE INDICADORES
# ----------------------------------------------------------------------
st.subheader("📌 Indicadores gerais")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{df_filtered["Curso"].nunique()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Cursos analisados</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{df_filtered["Ano"].nunique()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Anos incluídos</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{len(df_filtered)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Registros totais</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# EVOLUÇÃO TEMPORAL
# ----------------------------------------------------------------------
st.subheader("📈 Evolução dos Indicadores ao Longo do Tempo")

indicador = st.selectbox(
    "Selecione o indicador",
    [
        "Posição",
        "Nota em avaliação do Mercado",
        "Nota em qualidade de ensino",
        "Nota em Professores com doutorado e mestrado",
        "Nota dos concluintes",
        "Nota em Tempo de Dedicação dos Professores",
        "Nota em Permanência dos alunos",
        "Nota em avaliação dos docentes"
    ]
)

fig = px.line(
    df_filtered,
    x="Ano",
    y=indicador,
    color="Curso",
    markers=True,
    line_shape="spline",
    title=f"Evolução de {indicador}"
)
fig.update_layout(
    template="plotly_dark",
    height=500,
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# COMPARAÇÃO ENTRE CURSOS EM UM ANO
# ----------------------------------------------------------------------
st.subheader("🏆 Comparação entre Cursos em um Ano Específico")

ano_comp = st.selectbox("Escolha o ano", sorted(df["Ano"].unique()))

df_year = df[df["Ano"] == ano_comp]

fig2 = px.bar(
    df_year,
    x="Curso",
    y="Posição",
    text="Posição",
    color="Curso",
    title=f"Ranking dos cursos UFPR em {ano_comp}",
)
fig2.update_traces(textposition="outside")
fig2.update_layout(template="plotly_dark", height=500)

st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------
# INSIGHTS AUTOMÁTICOS
# ----------------------------------------------------------------------
st.subheader("🧠 Insights Automáticos - Posição")

for curso in sorted(df_filtered["Curso"].unique()):
    df_c = df_filtered[df_filtered["Curso"] == curso].sort_values("Ano")

    if len(df_c) <= 1:
        continue

    pos_ini = df_c.iloc[0]["Posição"]
    pos_fim = df_c.iloc[-1]["Posição"]

    if pos_fim < pos_ini:
        tendencia = "⬆️ Melhorou"
        cor = "green"
    elif pos_fim > pos_ini:
        tendencia = "⬇️ Piorou"
        cor = "red"
    else:
        tendencia = "➡️ Estável"
        cor = "DarkOrange"

    st.markdown(
        f"**{curso}**: posição {pos_ini:.0f} → {pos_fim:.0f} "
        f"<span style='color:{cor}'><b>{tendencia}</b></span>",
        unsafe_allow_html=True
    )


st.subheader("🧠 Insights Automáticos - Posição em Avaliação do Mercado")

for curso in sorted(df_filtered["Curso"].unique()):
    df_c = df_filtered[df_filtered["Curso"] == curso].sort_values("Ano")

    if len(df_c) <= 1:
        continue

    pos_ini = df_c.iloc[0]["Nota em avaliação do Mercado"]
    pos_fim = df_c.iloc[-1]["Nota em avaliação do Mercado"]

    if pos_fim < pos_ini:
        tendencia = "⬆️ Melhorou"
        cor = "green"
    elif pos_fim > pos_ini:
        tendencia = "⬇️ Piorou"
        cor = "red"
    else:
        tendencia = "➡️ Estável"
        cor = "DarkOrange"

    st.markdown(
        f"**{curso}**: posição {pos_ini:.0f} → {pos_fim:.0f} "
        f"<span style='color:{cor}'><b>{tendencia}</b></span>",
        unsafe_allow_html=True
    )


st.subheader("🧠 Insights Automáticos - Posição em qualidade de ensino")

for curso in sorted(df_filtered["Curso"].unique()):
    df_c = df_filtered[df_filtered["Curso"] == curso].sort_values("Ano")

    if len(df_c) <= 1:
        continue

    pos_ini = df_c.iloc[0]["Posição em qualidade de ensino"]
    pos_fim = df_c.iloc[-1]["Posição em qualidade de ensino"]

    if pos_fim < pos_ini:
        tendencia = "⬆️ Melhorou"
        cor = "green"
    elif pos_fim > pos_ini:
        tendencia = "⬇️ Piorou"
        cor = "red"
    else:
        tendencia = "➡️ Estável"
        cor = "DarkOrange"

    st.markdown(
        f"**{curso}**: posição {pos_ini:.0f} → {pos_fim:.0f} "
        f"<span style='color:{cor}'><b>{tendencia}</b></span>",
        unsafe_allow_html=True
    )

# ----------------------------------------------------------------------
# TABELA
# ----------------------------------------------------------------------
st.subheader("📋 Tabela Completa dos Dados Selecionados")
st.dataframe(df_filtered, use_container_width=True, height=350)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
