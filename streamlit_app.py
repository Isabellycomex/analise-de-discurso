import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud

st.title("Análise de Discurso de Ódio no Reddit através do ChatGpt")
st.write("""
    Os gráficos a seguir apresentam os dados coletados ao longo do estudo realizado para o desenvolvimento do meu Trabalho de Conclusão de Curso.
""")

# Corrigir o caminho do arquivo
file_path = "publicacoes.csv"

# Carregar os dados do CSV
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    st.error("O arquivo não foi encontrado. Verifique o caminho.")
    st.stop()
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
    st.stop()

# Verificar se as colunas necessárias existem
required_columns = ["resultado_analise", "emocao", "hora_postagem", "upvotes", "comentarios", "texto"]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(f"As colunas ausentes são: {missing_columns}. Verifique o arquivo CSV.")
    st.stop()

# Tratar dados
data["hora_postagem"] = pd.to_datetime(data["hora_postagem"])  # Converter hora para datetime
data["engajamento"] = data["upvotes"] + data["comentarios"]  # Criar coluna de engajamento

# Marcar discursos de ódio
data["eh_discurso_odio"] = data["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

# Exibir os dados em tabela
st.subheader("Tabela de Dados")
st.dataframe(data)

# Filtro por data
st.sidebar.subheader("Filtros")
start_date = st.sidebar.date_input("Data Inicial", value=data["hora_postagem"].min())
end_date = st.sidebar.date_input("Data Final", value=data["hora_postagem"].max())

# Filtro por tipo de discurso
discurso_filter = st.sidebar.multiselect(
    "Filtrar por Tipo de Discurso", 
    options=data["resultado_analise"].unique(),
    default=data["resultado_analise"].unique()
)

# Filtro por emoção
emocao_filter = st.sidebar.multiselect(
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

# Gráfico 1: Relação entre publicações com e sem discurso de ódio
st.subheader("Publicações com Discurso de Ódio x Publicações sem Discurso de Ódio")

contagem_odio = data_filtered["eh_discurso_odio"].value_counts()
fig, ax = plt.subplots()
ax.pie(
    contagem_odio.values,
    labels=contagem_odio.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=["#ff9999", "#66b3ff"]
)
ax.set_title("Discurso de Ódio vs Não é Discurso de Ódio")
st.pyplot(fig)

# Gráfico 2: Tipos de discurso de ódio
st.subheader("Relação dos Tipos de Discursos de Ódio")

tipos_odio = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"]["resultado_analise"].value_counts()
fig_bar = px.bar(
    x=tipos_odio.index,
    y=tipos_odio.values,
    labels={"x": "Tipo de Discurso", "y": "Quantidade"},
    title="Distribuição dos Tipos de Discursos de Ódio",
    color=tipos_odio.index,
)
st.plotly_chart(fig_bar)

# Gráfico 3: Emoções por tipo de discurso de ódio
st.subheader("Emoções por Tipo de Discurso de Ódio")

emocao_por_tipo = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"].groupby(["resultado_analise", "emocao"]).size().reset_index(name="count")
fig_emocao = px.bar(
    emocao_por_tipo,
    x="resultado_analise",
    y="count",
    color="emocao",
    barmode="group",
    title="Emoções por Tipo de Discurso de Ódio",
    labels={"resultado_analise": "Tipo de Discurso", "count": "Quantidade", "emocao": "Emoção"}
)
st.plotly_chart(fig_emocao)

# Gráfico 4: Publicações com mais engajamento
st.subheader("Publicações com Mais Engajamento")

top_engajamento = data_filtered.sort_values(by="engajamento", ascending=False).head(10)
fig_top = px.bar(
    top_engajamento,
    x="hora_postagem",
    y="engajamento",
    color="resultado_analise",
    title="Top 10 Publicações com Mais Engajamento",
    labels={"hora_postagem": "Hora da Postagem", "engajamento": "Engajamento", "resultado_analise": "Tipo de Discurso"}
)
st.plotly_chart(fig_top)


# Gráfico 5: Relação de discurso de ódio por ordem cronológica
st.subheader("Discurso de Ódio por Ordem Cronológica")

odio_por_tempo = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"].groupby(data_filtered["hora_postagem"].dt.to_period("M")).size()
fig_tempo = px.line(
    x=odio_por_tempo.index.astype(str),
    y=odio_por_tempo.values,
    title="Discurso de Ódio ao Longo do Tempo",
    labels={"x": "Mês", "y": "Quantidade de Discursos de Ódio"}
)
st.plotly_chart(fig_tempo)

# Gráfico 6: Emoções Mais Encontradas
st.subheader("Emoções Mais Encontradas")
emocao_counts = data_filtered['emocao'].value_counts()

fig_emocao, ax_emocao = plt.subplots()
ax_emocao.bar(emocao_counts.index, emocao_counts.values, color="lightcoral")
ax_emocao.set_title('Distribuição das Emoções')
ax_emocao.set_xlabel('Emoções')
ax_emocao.set_ylabel('Contagem')
st.pyplot(fig_emocao)


# Criando o mapa de calor
plt.figure(figsize=(10, 6))
sns.heatmap(colunas_numericas.corr(), annot=True, cmap='coolwarm')
plt.title('Mapa de Calor - Correlação entre Métricas', fontsize=16)
plt.show()

# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
