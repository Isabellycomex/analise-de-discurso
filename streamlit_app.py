import streamlit as st
import pandas as pd
import plotly.express as px

# Exemplo de dados (substitua por seu próprio conjunto de dados)
data = pd.read_csv("seu_arquivo.csv")

# Definição das cores
cores = ['#FF69B4', '#00BFFF', '#32CD32', '#FF6347', '#FFD700']  # Rosa, Azul, Verde, Vermelho, Amarelo

# Filtros
graficos_selecionados = st.multiselect(
    "Selecione os gráficos que deseja visualizar:",
    [
        "Discurso de Ódio vs Não é Discurso de Ódio",
        "Evolução Temporal dos Tipos de Discurso de Ódio",
        "Evolução Temporal das Emoções",
        "Distribuição de Upvotes por Emoção",
        "Distribuição de Engajamento por Tipo de Discurso",
        "Correlação entre Upvotes e Comentários",
        "Histograma de Engajamento",
        "Relação de Emoção por Tipo de Discurso",
        "Gráfico de Linhas de Upvotes Médios por Tipo de Discurso"
    ]
)

# Filtro para publicações
filtro_publicacoes = st.selectbox(
    "Selecione o tipo de publicação para visualizar:",
    ["Todas as publicações", "Discurso de Ódio", "Não é Discurso de Ódio"]
)

# Filtrando os dados conforme a seleção
if filtro_publicacoes == "Discurso de Ódio":
    data_filtered = data[data['resultado_analise'] == "Discurso de Ódio"]
elif filtro_publicacoes == "Não é Discurso de Ódio":
    data_filtered = data[data['resultado_analise'] == "Não é Discurso de Ódio"]
else:
    data_filtered = data

# Mostrar as publicações filtradas
st.subheader(f"Publicações Selecionadas ({filtro_publicacoes})")
st.write(data_filtered)

# Exibindo os gráficos selecionados

# Gráfico de Pizza - Discurso de Ódio vs Não é Discurso de Ódio
if "Discurso de Ódio vs Não é Discurso de Ódio" in graficos_selecionados:
    discurso_odio_counts = data_filtered['resultado_analise'].value_counts()
    fig1 = px.pie(
        names=discurso_odio_counts.index,
        values=discurso_odio_counts.values,
        title="Discurso de Ódio vs Não é Discurso de Ódio",
        color=discurso_odio_counts.index,
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig1)

# Gráfico de Linhas - Evolução Temporal dos Tipos de Discurso de Ódio
if "Evolução Temporal dos Tipos de Discurso de Ódio" in graficos_selecionados:
    tipo_discurso_ano = data_filtered.groupby(['mes_ano', 'tipo_discurso'])['resultado_analise'].count().reset_index()
    fig2 = px.line(
        tipo_discurso_ano,
        x="mes_ano",
        y="resultado_analise",
        color="tipo_discurso",
        title="Evolução Temporal dos Tipos de Discurso de Ódio",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig2)

# Gráfico de Linhas - Evolução Temporal das Emoções
if "Evolução Temporal das Emoções" in graficos_selecionados:
    emocao_tempo = data_filtered.groupby(['mes_ano', 'emocao'])['resultado_analise'].count().reset_index()
    fig3 = px.line(
        emocao_tempo,
        x="mes_ano",
        y="resultado_analise",
        color="emocao",
        title="Evolução Temporal das Emoções",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig3)

# Gráfico de Barras - Distribuição de Upvotes por Emoção
if "Distribuição de Upvotes por Emoção" in graficos_selecionados:
    fig4 = px.bar(
        data_filtered,
        x="emocao",
        y="upvotes",
        color="emocao",
        title="Distribuição de Upvotes por Emoção",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig4)

# Gráfico de Barras - Distribuição de Engajamento por Tipo de Discurso
if "Distribuição de Engajamento por Tipo de Discurso" in graficos_selecionados:
    fig5 = px.box(
        data_filtered,
        x="resultado_analise",
        y="engajamento",
        color="resultado_analise",
        title="Distribuição de Engajamento por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig5)

# Gráfico de Correlação entre Upvotes e Comentários
if "Correlação entre Upvotes e Comentários" in graficos_selecionados:
    fig6 = px.scatter(
        data_filtered,
        x="upvotes",
        y="comentarios",
        color="resultado_analise",
        title="Correlação entre Upvotes e Comentários",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig6)

# Gráfico de Relação de Emoção por Tipo de Discurso
if "Relação de Emoção por Tipo de Discurso" in graficos_selecionados:
    fig7 = px.sunburst(
        data_filtered,
        path=["resultado_analise", "emocao"],
        title="Relação de Emoção por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig7)

# Gráfico de Linhas de Upvotes Médios por Tipo de Discurso
if "Gráfico de Linhas de Upvotes Médios por Tipo de Discurso" in graficos_selecionados:
    upvotes_medio = data_filtered.groupby(["mes_ano", "resultado_analise"])["upvotes"].mean().reset_index()
    fig8 = px.line(
        upvotes_medio,
        x="mes_ano",
        y="upvotes",
        color="resultado_analise",
        title="Gráfico de Linhas de Upvotes Médios por Tipo de Discurso",
        color_discrete_sequence=cores
    )
    st.plotly_chart(fig8)

# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
