import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import STOPWORDS
from collections import Counter

# Carregar os dados do CSV
file_path = "publicacoes.csv"

# Função para carregar os dados e verificar erros
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

# Layout para seleção de gráficos
st.title("Análise de Discurso de Ódio no Reddit através do ChatGPT")

# Tratar dados
data["hora_postagem"] = pd.to_datetime(data["hora_postagem"])  # Converter hora para datetime
data["engajamento"] = data["upvotes"] + data["comentarios"]  # Criar coluna de engajamento

# Marcar discursos de ódio
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

# Aplicar filtros
data_filtered = data[
    (data["hora_postagem"] >= pd.to_datetime(start_date)) &
    (data["hora_postagem"] <= pd.to_datetime(end_date)) &
    (data["resultado_analise"].isin(discurso_filter)) &
    (data["emocao"].isin(emocao_filter))
]

# Visualizações
st.subheader("Visualizações")

# Gráfico de Pizza - Discurso de Ódio
fig1 = px.pie(
    data_filtered,
    names="eh_discurso_odio",
    title="Discurso de Ódio vs Não é Discurso de Ódio",
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Bold
)
st.plotly_chart(fig1)

# Boxplot - Distribuição de Upvotes por Emoção
if not data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"].empty:
    fig2 = px.box(
        data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"],
        x="emocao",
        y="upvotes",
        color="emocao",
        title="Distribuição de Upvotes por Emoção",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig2)

# Histograma - Distribuição de Upvotes e Engajamento por Tipo de Discurso
fig3 = px.histogram(
    data_filtered,
    x="resultado_analise",
    y=["upvotes", "engajamento"],
    barmode="group",
    title="Distribuição de Upvotes e Engajamento por Tipo de Discurso",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig3)

# Gráfico de Barras - Frequência de Palavras Associadas a Discursos de Ódio
if not data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"].empty:
    palavras = " ".join(data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]["texto"]).lower()
    palavras_filtradas = [p for p in palavras.split() if p not in STOPWORDS]
    contagem_palavras = Counter(palavras_filtradas).most_common(10)
    palavras_df = pd.DataFrame(contagem_palavras, columns=["palavra", "frequencia"])
    fig4 = px.bar(
        palavras_df,
        x="palavra",
        y="frequencia",
        title="Frequência de Palavras Associadas a Discursos de Ódio",
        color="frequencia",
        color_continuous_scale=px.colors.sequential.Reds
    )
    st.plotly_chart(fig4)

# Gráfico de Linhas - Evolução Temporal das Emoções
if not data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"].empty:
    data_filtered["mes_ano"] = data_filtered["hora_postagem"].dt.to_period("M").astype(str)
    emocao_tempo = data_filtered.groupby(["mes_ano", "emocao"]).size().reset_index(name="count")
    fig5 = px.line(
        emocao_tempo,
        x="mes_ano",
        y="count",
        color="emocao",
        title="Evolução Temporal das Emoções",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    st.plotly_chart(fig5)

# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 98837-2120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão  

""")
