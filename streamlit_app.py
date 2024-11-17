import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

# Carregar os dados do CSV
file_path = "publicacoes.csv"

# Função para carregar os dados e verificar erros
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        # Verificar se as colunas necessárias existem
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

# Tratar dados
data["hora_postagem"] = pd.to_datetime(data["hora_postagem"])  # Converter hora para datetime
data["engajamento"] = data["upvotes"] + data["comentarios"]  # Criar coluna de engajamento

# Marcar discursos de ódio
data["eh_discurso_odio"] = data["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

# Filtros em tela
st.subheader("Filtros")
start_date = st.date_input("Data Inicial", value=data["hora_postagem"].min())
end_date = st.date_input("Data Final", value=data["hora_postagem"].max())

discurso_filter = st.multiselect(
    "Filtrar por Tipo de Discurso", 
    options=data["resultado_analise"].unique(),
    default=data["resultado_analise"].unique()
)

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

# Layout para seleção de gráficos
st.title("Análise de Discurso de Ódio no Reddit através do ChatGpt")

# Organizar gráficos em colunas
st.subheader("Seleção de Visualização")
visualizacao = st.multiselect(
    "Escolha os gráficos que deseja visualizar", 
    ["Discurso de Ódio x Não Discurso de Ódio", 
     "Tipos de Discursos de Ódio", 
     "Emoções por Tipo de Discurso de Ódio", 
     "Top Publicações com Engajamento", 
     "Discurso de Ódio ao Longo do Tempo"],
    default=["Discurso de Ódio x Não Discurso de Ódio"]
)

# Exibir gráficos de acordo com a seleção
if "Discurso de Ódio x Não Discurso de Ódio" in visualizacao:
    contagem_odio = data_filtered["eh_discurso_odio"].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(
        contagem_odio.values,
        labels=contagem_odio.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=["#ff9999", "#66b3ff"]
    )
    ax1.set_title("Discurso de Ódio vs Não é Discurso de Ódio")
    st.pyplot(fig1)

if "Tipos de Discursos de Ódio" in visualizacao:
    tipos_odio = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"]["resultado_analise"].value_counts()
    fig2 = px.bar(
        x=tipos_odio.index,
        y=tipos_odio.values,
        labels={"x": "Tipo de Discurso", "y": "Quantidade"},
        title="Distribuição dos Tipos de Discursos de Ódio",
        color=tipos_odio.index,
    )
    st.plotly_chart(fig2)

if "Emoções por Tipo de Discurso de Ódio" in visualizacao:
    emocao_por_tipo = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"].groupby(["resultado_analise", "emocao"]).size().reset_index(name="count")
    fig3 = px.bar(
        emocao_por_tipo,
        x="resultado_analise",
        y="count",
        color="emocao",
        barmode="group",
        title="Emoções por Tipo de Discurso de Ódio",
        labels={"resultado_analise": "Tipo de Discurso", "count": "Quantidade", "emocao": "Emoção"}
    )
    st.plotly_chart(fig3)

if "Top Publicações com Engajamento" in visualizacao:
    top_engajamento = data_filtered.sort_values(by="engajamento", ascending=False).head(10)
    fig4 = px.bar(
        top_engajamento,
        x="hora_postagem",
        y="engajamento",
        color="resultado_analise",
        title="Top 10 Publicações com Mais Engajamento",
        labels={"hora_postagem": "Hora da Postagem", "engajamento": "Engajamento", "resultado_analise": "Tipo de Discurso"}
    )
    st.plotly_chart(fig4)

if "Discurso de Ódio ao Longo do Tempo" in visualizacao:
    odio_por_tempo = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"].groupby(data_filtered["hora_postagem"].dt.to_period("M")).size()
    fig5 = px.line(
        x=odio_por_tempo.index.astype(str),
        y=odio_por_tempo.values,
        title="Discurso de Ódio ao Longo do Tempo",
        labels={"x": "Mês", "y": "Quantidade de Discursos de Ódio"}
    )
    st.plotly_chart(fig5)

# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
