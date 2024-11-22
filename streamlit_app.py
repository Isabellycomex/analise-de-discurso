import streamlit as st
import pandas as pd
import plotly.express as px

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

col5, _ = st.columns(2)
with col5:
    max_publicacoes = st.slider(
        "Quantidade de Publicações para Analisar",
        min_value=1,
        max_value=min(len(data), 300),
        value=300
    )

# Aplicar filtros
data_filtered = data[
    (data["hora_postagem"] >= pd.to_datetime(start_date)) &
    (data["hora_postagem"] <= pd.to_datetime(end_date)) &
    (data["resultado_analise"].isin(discurso_filter)) &
    (data["emocao"].isin(emocao_filter))
].head(max_publicacoes)

# Seleção de gráficos
visualizacoes = st.multiselect(
    "Escolha os gráficos que deseja visualizar:",
    [
        "Gráfico de Pizza - Discurso de Ódio",
        "Emoções por Tipo de Discurso de Ódio",
        "Top Publicações com Engajamento",
        "Discurso de Ódio ao Longo do Tempo",
        "Média de Upvotes por Tipo de Discurso de Ódio",
        "Engajamento Médio por Emoção",
        "Engajamento Médio por Tipo de Discurso de Ódio"
    ]
)

# Visualizações
st.subheader("Visualizações")

if "Gráfico de Pizza - Discurso de Ódio" in visualizacoes:
    fig1 = px.pie(
        data_filtered,
        names="eh_discurso_odio",
        title="Discurso de Ódio vs Não é Discurso de Ódio",
        hole=0.3
    )
    st.plotly_chart(fig1)

if "Emoções por Tipo de Discurso de Ódio" in visualizacoes:
    emocao_contagem = data_filtered.groupby(["resultado_analise", "emocao"]).size().reset_index(name="count")
    fig2 = px.bar(
        emocao_contagem,
        x="emocao",
        y="count",
        color="resultado_analise",
        barmode="group",
        title="Distribuição de Emoções por Tipo de Discurso de Ódio"
    )
    st.plotly_chart(fig2)

if "Top Publicações com Engajamento" in visualizacoes:
    top_engajamento = data_filtered.sort_values(by="engajamento", ascending=False).head(10)
    fig3 = px.bar(
        top_engajamento,
        x="hora_postagem",
        y="engajamento",
        color="resultado_analise",
        title="Top 10 Publicações com Mais Engajamento"
    )
    st.plotly_chart(fig3)

if "Discurso de Ódio ao Longo do Tempo" in visualizacoes:
    data_filtered["mes_postagem"] = data_filtered["hora_postagem"].dt.to_period("M").astype(str)
    odio_tempo = data_filtered.groupby(["mes_postagem", "resultado_analise"]).size().reset_index(name="count")
    fig4 = px.line(
        odio_tempo,
        x="mes_postagem",
        y="count",
        color="resultado_analise",
        title="Discurso de Ódio ao Longo do Tempo"
    )
    st.plotly_chart(fig4)

if "Média de Upvotes por Tipo de Discurso de Ódio" in visualizacoes:
    media_upvotes = data_filtered.groupby("resultado_analise")["upvotes"].mean().reset_index()
    fig5 = px.bar(
        media_upvotes,
        x="resultado_analise",
        y="upvotes",
        title="Média de Upvotes por Tipo de Discurso de Ódio"
    )
    st.plotly_chart(fig5)

if "Engajamento Médio por Emoção" in visualizacoes:
    emocao_engajamento = data_filtered.groupby("emocao")["engajamento"].mean().reset_index()
    fig6 = px.bar(
        emocao_engajamento,
        x="emocao",
        y="engajamento",
        title="Engajamento Médio por Emoção"
    )
    st.plotly_chart(fig6)

if "Engajamento Médio por Tipo de Discurso de Ódio" in visualizacoes:
    tipo_engajamento = data_filtered.groupby("resultado_analise")["engajamento"].mean().reset_index()
    fig7 = px.bar(
        tipo_engajamento,
        x="resultado_analise",
        y="engajamento",
        title="Engajamento Médio por Tipo de Discurso de Ódio"
    )
    st.plotly_chart(fig7)

# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 98837-2120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão  
""")
