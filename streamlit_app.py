import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Carregar os dados do CSV
file_path = "publicacoes.csv"

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        required_columns = ["resultado_analise", "emocao", "hora_postagem", "upvotes", "comentarios", "texto"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"As colunas ausentes são: {missing_columns}. Verifique o arquivo CSV.")
            return None
        return data
    except FileNotFoundError:
        st.error("O arquivo não foi encontrado. Verifique o caminho.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
    return None

data = load_data(file_path)
if data is None:
    st.stop()

# Layout
st.title("Análise de Discurso de Ódio no Reddit através do ChatGPT")

# Tratar dados
data["hora_postagem"] = pd.to_datetime(data["hora_postagem"])  # Converter hora para datetime
data["engajamento"] = data["upvotes"] + data["comentarios"]  # Criar coluna de engajamento
data["eh_discurso_odio"] = data["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

# Filtros em tela
st.subheader("Filtros")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Data Inicial", value=data["hora_postagem"].min())
with col2:
    end_date = st.date_input("Data Final", value=data["hora_postagem"].max())

col3, col4 = st.columns(2)
with col3:
    discurso_filter = st.multiselect(
        "Filtrar por Tipo de Discurso",
        options=data["resultado_analise"].unique(),
        default=data["resultado_analise"].unique()
    )
with col4:
    emocao_filter = st.multiselect(
        "Filtrar por Emoção",
        options=data["emocao"].unique(),
        default=data["emocao"].unique()
    )

col5, col6 = st.columns(2)
with col5:
    publicacoes_min = st.number_input("Quantidade Mínima de Publicações", value=1, min_value=1, max_value=len(data))
with col6:
    publicacoes_max = st.number_input("Quantidade Máxima de Publicações", value=len(data), min_value=1, max_value=len(data))

# Aplicar filtros
data_filtered = data[
    (data["hora_postagem"] >= pd.to_datetime(start_date)) &
    (data["hora_postagem"] <= pd.to_datetime(end_date)) &
    (data["resultado_analise"].isin(discurso_filter)) &
    (data["emocao"].isin(emocao_filter))
]

# Aplicar filtro de publicações
data_filtered = data_filtered.iloc[int(publicacoes_min)-1:int(publicacoes_max)]

# Filtro de gráficos
st.subheader("Seleção de Gráficos")
graficos = [
    "Discurso de Ódio vs Não é Discurso de Ódio",
    "Evolução Temporal dos Tipos de Discurso de Ódio",
    "Evolução Temporal das Emoções",
    "Distribuição de Upvotes por Emoção",
    "Distribuição de Engajamento por Tipo de Discurso",
    "Correlação entre Upvotes e Comentários",
    "Histograma de Engajamento",
    "Boxplot de Comentários por Tipo de Discurso",
    "Gráfico de Linhas de Upvotes Médios por Tipo de Discurso",
    "Boxplot de Emoções por Engajamento"
]
graficos_selecionados = st.multiselect("Selecione os gráficos para visualizar", options=graficos, default=graficos)

# Cores consistentes
cores = ["#FF69B4", "#1E90FF", "#32CD32", "#FF4500", "#FFD700"]  # Rosa, Azul, Verde, Vermelho, Amarelo

# Gráficos selecionados
if "Discurso de Ódio vs Não é Discurso de Ódio" in graficos_selecionados:
    fig1 = px.pie(
        data_filtered,
        names="eh_discurso_odio",
        title="Discurso de Ódio vs Não é Discurso de Ódio",
        hole=0.3,
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig1)
    st.dataframe(data_filtered[["hora_postagem", "resultado_analise", "texto"]])

if "Evolução Temporal dos Tipos de Discurso de Ódio" in graficos_selecionados:
    data_filtered["mes_ano"] = data_filtered["hora_postagem"].dt.to_period("M").astype(str)
    evolucao_tipos = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]
    evolucao_tipos = evolucao_tipos.groupby(["mes_ano", "resultado_analise"]).size().reset_index(name="count")
    fig2 = px.line(
        evolucao_tipos,
        x="mes_ano",
        y="count",
        color="resultado_analise",
        title="Evolução Temporal dos Tipos de Discurso de Ódio",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig2)

if "Evolução Temporal das Emoções" in graficos_selecionados:
    data_filtered["mes_ano"] = data_filtered["hora_postagem"].dt.to_period("M").astype(str)
    emocao_tempo = data_filtered[data_filtered["emocao"] != "não identificada"]
    emocao_tempo = emocao_tempo.groupby(["mes_ano", "emocao"]).size().reset_index(name="count")
    fig3 = px.line(
        emocao_tempo,
        x="mes_ano",
        y="count",
        color="emocao",
        title="Evolução Temporal das Emoções",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig3)

if "Distribuição de Upvotes por Emoção" in graficos_selecionados:
    fig4 = px.violin(
        data_filtered,
        x="emocao",
        y="upvotes",
        color="emocao",
        title="Distribuição de Upvotes por Emoção",
        box=True,
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig4)

if "Distribuição de Engajamento por Tipo de Discurso" in graficos_selecionados:
    fig5 = px.box(
        data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"],
        x="resultado_analise",
        y="engajamento",
        color="resultado_analise",
        title="Distribuição de Engajamento por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig5)

if "Correlação entre Upvotes e Comentários" in graficos_selecionados:
    fig6 = px.density_heatmap(
        data_filtered,
        x="upvotes",
        y="comentarios",
        title="Correlação entre Upvotes e Comentários",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig6)

if "Histograma de Engajamento" in graficos_selecionados:
    fig7 = px.histogram(
        data_filtered,
        x="engajamento",
        nbins=20,
        title="Histograma de Engajamento",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig7)

if "Boxplot de Comentários por Tipo de Discurso" in graficos_selecionados:
    fig8 = px.box(
        data_filtered,
        x="resultado_analise",
        y="comentarios",
        color="resultado_analise",
        title="Boxplot de Comentários por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig8)

if "Gráfico de Linhas de Upvotes Médios por Tipo de Discurso" in graficos_selecionados:
    upvotes_medio = data_filtered.groupby(["mes_ano", "resultado_analise"])["upvotes"].mean().reset_index()
    fig9 = px.line(
        upvotes_medio,
        x="mes_ano",
        y="upvotes",
        color="resultado_analise",
        title="Gráfico de Linhas de Upvotes Médios por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig9)

if "Boxplot de Emoções por Engajamento" in graficos_selecionados:
    fig10 = px.box(
        data_filtered,
        x="emocao",
        y="engajamento",
        color="emocao",
        title="Boxplot de Emoções por Engajamento",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig10)
# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
