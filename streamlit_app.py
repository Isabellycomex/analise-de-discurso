import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
st.title("Análise de Discurso de Ódio no Reddit através do ChatGpt")

# Tratar dados
data["hora_postagem"] = pd.to_datetime(data["hora_postagem"])  # Converter hora para datetime
data["engajamento"] = data["upvotes"] + data["comentarios"]  # Criar coluna de engajamento

# Marcar discursos de ódio
data["eh_discurso_odio"] = data["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

# Filtros em tela com organização lado a lado
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

# Filtro para selecionar a quantidade de publicações
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

# Tabela das publicações filtradas
st.subheader("Publicações Filtradas")
st.write(data_filtered[["hora_postagem", "resultado_analise", "emocao", "upvotes", "comentarios", "texto"]])

# Seleção de gráficos para visualização múltipla
visualizacoes = st.multiselect(
    "Escolha os gráficos que deseja visualizar:",
    [
        "Gráfico de Pizza - Discurso de Ódio",
        "Emoções por Tipo de Discurso de Ódio",
        "Visualizações por Tipo de Discurso de Ódio",
        "Discurso de Ódio ao Longo do Tempo",
        "Média de Upvotes por Tipo de Discurso de Ódio",
        "Palavras Mais Comuns em Discurso de Ódio"
    ]
)

# Gráficos selecionados
st.subheader("Visualizações")

if "Gráfico de Pizza - Discurso de Ódio" in visualizacoes:
    contagem_odio = data_filtered["eh_discurso_odio"].value_counts()

    # Criando o gráfico de pizza com modificações para um gráfico redondo e fundo preto
    fig1 = px.pie(
        data_filtered,
        names="eh_discurso_odio",
        title="Discurso de Ódio vs Não é Discurso de Ódio",
        hole=0,  # Retira o buraco central para um gráfico totalmente redondo
        color_discrete_sequence=["#ff6666", "#4C99FF"],  # Cores mais sóbrias
    )

    # Ajustes estéticos
    fig1.update_traces(
        hoverinfo="label+percent",  # Informação ao passar o mouse
        textinfo="value+percent",  # Exibe valor absoluto e percentagem
        textfont=dict(size=14, family="Arial, sans-serif"),  # Tamanho da fonte
        marker=dict(line=dict(color="white", width=2))  # Borda branca para dar um acabamento mais limpo
    )

    # Ajustar layout
    fig1.update_layout(
        showlegend=True,
        title_font=dict(size=18, family="Arial, sans-serif", color="white"),  # Fonte do título
        plot_bgcolor="black",  # Cor de fundo do gráfico
        paper_bgcolor="black",  # Cor de fundo da área externa do gráfico
        margin=dict(t=40, b=40, l=40, r=40),  # Ajuste de margens para deixar o gráfico mais próximo da borda
        font=dict(color="white")  # Cor da fonte do título e do texto
    )

    # Exibe o gráfico
    st.plotly_chart(fig1)


if "Emoções por Tipo de Discurso de Ódio" in visualizacoes:
    # Filtrar apenas discursos de ódio
    odio_emocoes = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"]
    emocao_contagem = odio_emocoes.groupby(["resultado_analise", "emocao"]).size().reset_index(name="count")
    
    fig2 = px.bar(
        emocao_contagem,
        x="emocao",
        y="count",
        color="resultado_analise",
        barmode="group",
        title="Distribuição de Emoções por Tipo de Discurso de Ódio",
        labels={"emocao": "Emoção", "count": "Quantidade", "resultado_analise": "Tipo de Discurso de Ódio"},
    )
    st.plotly_chart(fig2)




if "Discurso de Ódio ao Longo do Tempo" in visualizacoes:
    # Certificar-se de que a coluna 'hora_postagem' é datetime
    if 'hora_postagem' in data_filtered.columns:
        data_filtered['hora_postagem'] = pd.to_datetime(data_filtered['hora_postagem'], errors='coerce')
    else:
        st.error("A coluna 'hora_postagem' não está presente nos dados.")
        raise ValueError("A coluna 'hora_postagem' não foi encontrada.")

    # Filtrar discursos de ódio
    odio_tempo = data_filtered[data_filtered["eh_discurso_odio"] == "Discurso de Ódio"]

    # Agrupar por mês e tipo de discurso
    odio_tempo["mes_postagem"] = odio_tempo["hora_postagem"].dt.to_period("M").astype(str)  # Converter para string
    odio_por_tipo_tempo = odio_tempo.groupby(["mes_postagem", "resultado_analise"]).size().reset_index(name="count")

    # Verificar se a tabela está vazia
    if odio_por_tipo_tempo.empty:
        st.error("Não há dados suficientes para gerar o gráfico de Discurso de Ódio ao Longo do Tempo.")
    else:
        # Verificar se os dados contêm valores nulos
        if odio_por_tipo_tempo.isnull().values.any():
            st.warning("Alguns dados estão nulos, o que pode afetar o gráfico. Verifique os dados.")
            odio_por_tipo_tempo = odio_por_tipo_tempo.dropna()

        # Criar o gráfico
        try:
            fig4 = px.line(
                odio_por_tipo_tempo,
                x="mes_postagem",
                y="count",
                color="resultado_analise",
                title="Discurso de Ódio ao Longo do Tempo por Tipo de Discurso",
                labels={"mes_postagem": "Mês", "count": "Quantidade", "resultado_analise": "Tipo de Discurso de Ódio"},
                markers=True
            )
            st.plotly_chart(fig4)
        except Exception as e:
            st.error(f"Erro ao gerar o gráfico: {str(e)}")


if "Média de Upvotes por Tipo de Discurso de Ódio" in visualizacoes:
    media_upvotes = data_filtered.groupby("resultado_analise")["upvotes"].mean().reset_index()
    media_upvotes.columns = ["Tipo de Discurso", "Média de Upvotes"]
    fig5 = px.bar(
        media_upvotes,
        x="Tipo de Discurso",
        y="Média de Upvotes",
        title="Média de Upvotes por Tipo de Discurso de Ódio",
        color="Tipo de Discurso",
        text_auto=True
    )
    st.plotly_chart(fig5)
if "Visualizações por Tipo de Discurso de Ódio" in visualizacoes:
    # Filtrar os dados para excluir "não é discurso de ódio"
    data_odio = data_filtered[data_filtered['resultado_analise'] != 'não é discurso de ódio']

    # Verificar se há dados após o filtro
    if not data_odio.empty:
        # Agrupar os dados por tipo de discurso e somar as visualizações
        visualizacoes_por_tipo = data_odio.groupby("resultado_analise")["visualizacoes"].sum().reset_index()

        # Gerar gráfico de linhas
        fig_visualizacoes_tipo = px.line(
            visualizacoes_por_tipo,
            x="resultado_analise",
            y="visualizacoes",
            title="Visualizações por Tipo de Discurso de Ódio",
            labels={"resultado_analise": "Tipo de Discurso de Ódio", "visualizacoes": "Total de Visualizações"},
            color_discrete_sequence=px.colors.qualitative.Bold  # Paleta de cores vibrantes e distintas
        )

        # Estilo e layout com fundo preto
        fig_visualizacoes_tipo.update_traces(mode="lines+markers", line=dict(width=3))
        fig_visualizacoes_tipo.update_layout(
            plot_bgcolor="black",  # Fundo preto
            paper_bgcolor="black",  # Fundo do canvas também preto
            font=dict(color="white"),  # Texto branco
            xaxis=dict(title="Tipos de Discurso de Ódio", showgrid=False),
            yaxis=dict(title="Visualizações", showgrid=True, gridcolor="gray"),
            title=dict(font=dict(size=20)),  # Título maior e em branco
            legend=dict(title="Tipos", font=dict(color="white"))  # Legenda estilizada
        )

        # Exibir o gráfico
        st.plotly_chart(fig_visualizacoes_tipo)
    else:
        st.write("Não há dados de discurso de ódio para exibir.")


if "Palavras Mais Comuns em Discurso de Ódio" in visualizacoes:
    # Filtrar os dados para considerar apenas discursos de ódio
    data_odio = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

    # Verificar se há dados após o filtro
    if not data_odio.empty:
        from wordcloud import WordCloud, STOPWORDS
        import matplotlib.pyplot as plt

        # Combinar os textos em uma única string
        textos = " ".join(data_odio["texto"])

        # Stopwords padrão + palavras adicionais irrelevantes
        stop_words = set(STOPWORDS)
        stop_words.update([
            "de", "como", "por", "mais", "quando", "se", "ele", "pra", "isso", "da", "para", "com", "que", 
            "em", "é", "e", "o", "a", "os", "as", "um", "uma", "na", "no", "não", "mas", "ela", "eu", 
            "você", "vocês", "nós", "eles", "elas", "meu", "minha", "meus", "minhas", "teu", "tua", "teus", 
            "tuas", "dele", "dela", "deles", "delas", "esse", "essa", "esses", "essas", "este", "esta", 
            "estes", "estas", "aquele", "aquela", "aqueles", "aquelas", "lhe", "lhes", "do", "dos", 
            "das", "num", "numa", "neste", "nesta", "nisto", "naquele", "naquela", "nisso", "daquilo", 
            "e", "ou", "onde", "porque", "porquê", "lá", "aqui", "ali", "assim", "tão", "já", "então", 
            "também", "muito", "pouco", "sempre", "tudo", "nada", "cada", "todos", "todas", "algum", 
            "alguma", "nenhum", "nenhuma", "outro", "outra", "outros", "outras", "seu", "sua", "seus", 
            "suas", "me", "te", "nos", "vos", "depois", "antes", "até", "ainda", "hoje", "ontem", 
            "amanhã", "agora", "lá", "cá", "sim", "não", "pois", "porém", "como", "sobre", "entre", 
            "contra", "sem", "baixo", "apenas", "mesmo", "era", "só", "coisa", "ser", "pessoa"
        ])

        # Gerar nuvem de palavras
        wordcloud = WordCloud(
            background_color="black",
            stopwords=stop_words,
            colormap="coolwarm",
            width=800,
            height=400
        ).generate(textos)

        # Exibir gráfico no Streamlit
        fig6, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        ax.set_title("Palavras Mais Comuns em Discurso de Ódio", fontsize=18, color="white")
        st.pyplot(fig6)

    else:
        st.write("Não há dados de discurso de ódio para gerar a nuvem de palavras.")




# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
