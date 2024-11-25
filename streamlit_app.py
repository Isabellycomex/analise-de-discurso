import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import nltk
from wordcloud import WordCloud, STOPWORDS
import datetime as dt


# Baixar os recursos necessários para o NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Carregar os dados do CSV
caminho_arquivo = "publicacoes.csv"

# Função para carregar os dados e verificar erros
def carregar_dados(caminho_arquivo):
    try:
        dados = pd.read_csv(caminho_arquivo)
        colunas_necessarias = ["resultado_analise", "emocao", "hora_postagem", "upvotes", "comentarios", "texto"]
        colunas_faltando = [col for col in colunas_necessarias if col not in dados.columns]
        if colunas_faltando:
            st.error(f"As colunas ausentes são: {colunas_faltando}. Verifique o arquivo CSV.")
            return None
        return dados
    except FileNotFoundError:
        st.error("O arquivo não foi encontrado. Verifique o caminho.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o arquivo: {e}")
    return None

dados = carregar_dados(caminho_arquivo)
if dados is None:
    st.stop()

# Configuração do layout e título
# Configuração do layout e título
st.title("Análise de Discurso de Ódio no Reddit com ChatGPT")

# Tratamento de dados
dados["hora_postagem"] = pd.to_datetime(dados["hora_postagem"], errors="coerce")  # Garantir conversão segura
dados["hora_postagem_formatada"] = dados["hora_postagem"].dt.strftime("%d/%m/%Y %H:%M:%S")  # Formatar para exibição

# Adicionar coluna de engajamento e de classificação
dados["engajamento"] = dados["upvotes"] + dados["comentarios"]
dados["eh_discurso_odio"] = dados["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

# Verificar valores mínimos e máximos para os filtros
data_min = dados["hora_postagem"].min()
data_max = dados["hora_postagem"].max()

# Evitar erro se os dados forem vazios ou NaT
data_inicio_default = data_min.date() if pd.notnull(data_min) else None
data_fim_default = data_max.date() if pd.notnull(data_max) else None

# Filtros
st.subheader("Filtros")

# Filtro por data
col1, col2 = st.columns(2)
with col1:
    data_inicio = st.date_input(
        "Data Inicial",
        value=data_inicio_default,
        min_value=data_min.date(),
        max_value=data_max.date(),
        key="data_inicio"
    )
with col2:
    data_fim = st.date_input(
        "Data Final",
        value=data_fim_default,
        min_value=data_min.date(),
        max_value=data_max.date(),
        key="data_fim"
    )

# Filtro por tipo de discurso e emoção
col3, col4 = st.columns(2)
with col3:
    filtro_discurso = st.multiselect(
        "Escolha uma ou mais opções",
        options=dados["resultado_analise"].unique(),
        default=dados["resultado_analise"].unique(),
        key="filtro_discurso"
    )
with col4:
    filtro_emocao = st.multiselect(
        "Escolha uma ou mais opções",
        options=dados["emocao"].unique(),
        default=dados["emocao"].unique(),
        key="filtro_emocao"
    )

# Filtro por quantidade de publicações
col5, _ = st.columns(2)
with col5:
    max_publicacoes = st.slider(
        "Quantidade de Publicações para Analisar",
        min_value=1,
        max_value=min(len(dados), 300),
        value=300,
        key="max_publicacoes"
    )

# Aplicação de filtros
dados_filtrados = dados[
    (dados["hora_postagem"].dt.date >= data_inicio) &
    (dados["hora_postagem"].dt.date <= data_fim) &
    (dados["resultado_analise"].isin(filtro_discurso)) &
    (dados["emocao"].isin(filtro_emocao))
].head(max_publicacoes)

# Exibição dos dados filtrados
st.subheader("Publicações Filtradas")
st.write(dados_filtrados[["hora_postagem_formatada", "resultado_analise", "emocao", "upvotes", "comentarios", "texto"]])

# Seleção de gráficos
st.subheader("Visualizações")
visualizacoes = st.multiselect(
    "Escolha uma ou mais opções",
    [
        "Gráfico de Pizza - Discurso de Ódio",
        "Emoções por Tipo de Discurso de Ódio",
        "Discurso de Ódio ao Longo do Tempo",
        "Média de Upvotes por Tipo de Discurso de Ódio",
        "Frequência de Postagens por Usuário",
        "Quantidade de Respostas por Tipo de Discurso",
        "Quantidade de Compartilhamentos por Tipo de Discurso"
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

# Certifique-se de baixar o corpus de stopwords do NLTK
nltk.download('stopwords')

# Extraia as stopwords em português do NLTK
nltk_stopwords = set(stopwords.words('portuguese'))


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

if "Frequência de Postagens por Usuário" in visualizacoes:
    # Filtrar dados para incluir apenas discursos de ódio
    data_usuarios = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

    # Agrupar por usuário e contar o número de postagens
    frequencia_postagens = (
        data_usuarios.groupby("usuario")
        .size()
        .reset_index(name="quantidade_postagens")
        .sort_values(by="quantidade_postagens", ascending=False)
        .head(10)  # Exibir os 10 usuários mais ativos
    )

    # Criar o gráfico
    fig_frequencia = px.bar(
        frequencia_postagens,
        x="usuario",
        y="quantidade_postagens",
        title="Frequência de Postagens por Usuário (Discursos de Ódio)",
        labels={"usuario": "Usuário", "quantidade_postagens": "Quantidade de Postagens"},
        text_auto=True,  # Mostrar valores nas barras
    )

    # Alterar a cor das barras para rosa
    fig_frequencia.update_traces(marker_color="pink")

    # Estilo do gráfico com fundo preto
    fig_frequencia.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(title="Usuários", showgrid=False),
        yaxis=dict(title="Frequência de Postagens", showgrid=True, gridcolor="gray"),
        title=dict(font=dict(size=20)),
    )

    # Exibir o gráfico
    st.plotly_chart(fig_frequencia)

if "Quantidade de Respostas por Tipo de Discurso" in visualizacoes:
    # Filtrar todas as postagens que não são "não é discurso de ódio"
    discurso_filtrado = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]
    
    # Verificar se existem dados após o filtro
    if not discurso_filtrado.empty:
        # Agrupar por tipo de discurso e somar a quantidade de respostas (comentários)
        resposta_contagem = discurso_filtrado.groupby("resultado_analise")["comentarios"].sum().reset_index()
        
        # Verificar se há dados após a agregação
        if not resposta_contagem.empty:
            # Criar gráfico de barras com escala vermelha
            fig = px.bar(
                resposta_contagem,
                x="resultado_analise",
                y="comentarios",
                title="Quantidade de Respostas por Tipo de Discurso",
                labels={"resultado_analise": "Tipo de Discurso", "comentarios": "Quantidade de Respostas (Comentários)"},
                color="comentarios",  # Cor das barras baseada no número de respostas
                color_continuous_scale="Viridis",  # Usar escala de cores vermelhas
            )
            st.plotly_chart(fig)
        else:
            st.write("Nenhuma resposta foi encontrada para os tipos de discurso considerados.")
    else:
        st.write("Não existem postagens classificadas como um tipo de discurso válido (diferente de 'não é discurso de ódio').")

if "Quantidade de Compartilhamentos por Tipo de Discurso" in visualizacoes:
    # Filtrar dados que não são "não é discurso de ódio"
    data_filtered = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]
    
    # Verificar se existem valores nulos na coluna de compartilhamentos e preencher com 0, caso existam
    data_filtered["compartilhamentos"] = data_filtered["compartilhamentos"].fillna(0)
    
    # Calcular a quantidade total de compartilhamentos por tipo de discurso
    compartilhamentos_por_tipo = data_filtered.groupby("resultado_analise")["compartilhamentos"].sum().reset_index()
    
    # Se houver tipos de discurso sem compartilhamentos, eles serão excluídos
    compartilhamentos_por_tipo = compartilhamentos_por_tipo[compartilhamentos_por_tipo["compartilhamentos"] > 0]

    # Verifique se o DataFrame de compartilhamentos_por_tipo tem dados
    if compartilhamentos_por_tipo.empty:
        st.write("Não há dados de compartilhamentos disponíveis para o gráfico.")
    else:
        # Criar gráfico de barras para os compartilhamentos por tipo de discurso
        fig = px.bar(
            compartilhamentos_por_tipo,
            x="resultado_analise",
            y="compartilhamentos",
            color="resultado_analise",
            title="Quantidade de Compartilhamentos por Tipo de Discurso",
            labels={"resultado_analise": "Tipo de Discurso", "compartilhamentos": "Quantidade de Compartilhamentos"},
            color_discrete_sequence=["#FF0000", "#FF6347", "#FF4500", "#FF1493"]  # Escolha de cores mais fortes
        )
        st.plotly_chart(fig)




# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
