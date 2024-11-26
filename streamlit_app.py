import streamlit as st
import pandas as pd
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
data_filtered = dados[ 
    (dados["hora_postagem"].dt.date >= data_inicio) &
    (dados["hora_postagem"].dt.date <= data_fim) &
    (dados["resultado_analise"].isin(filtro_discurso)) &
    (dados["emocao"].isin(filtro_emocao))
].head(max_publicacoes)

# Exibição dos dados filtrados
st.subheader("Publicações Filtradas")
st.write(data_filtered[["hora_postagem_formatada", "resultado_analise", "emocao", "upvotes", "comentarios", "texto"]])

# Seleção de gráficos
st.subheader("Visualizações")
visualizacoes = st.multiselect(
    "Escolha uma ou mais opções",
    [
        "Discurso (Ódio/Não Ódio)",
        "Tipo de Discurso de Ódio",
        "Emoções",
        "Quantidade de Comentários",
        "Quantidade de Compartilhamentos",
        "Visualizações",
        "Likes (Upvotes)",
        "Frequência por tipo de discurso",
        "Frequência por usuário",
        "Palavras mais comuns"
    ]
)

# Gráficos selecionados
st.subheader("Visualizações")

def aplicar_estilo(fig):
    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        title_font=dict(size=18, family="Arial, sans-serif", color="white"),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

if "Discurso (Ódio/Não Ódio)" in visualizacoes:
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
    fig1 = aplicar_estilo(fig1)
    st.plotly_chart(fig1)

if "Emoções" in visualizacoes:
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
    fig2 = aplicar_estilo(fig2)
    st.plotly_chart(fig2)

if "Frequência por tipo de discurso" in visualizacoes:
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
        # Criar o gráfico de linha
        fig3 = px.line(
            odio_por_tipo_tempo,
            x="mes_postagem",
            y="count",
            color="resultado_analise",
            title="Discurso de Ódio ao Longo do Tempo por Tipo de Discurso",
            labels={"mes_postagem": "Mês", "count": "Quantidade", "resultado_analise": "Tipo de Discurso de Ódio"},
            markers=True
        )
        fig3 = aplicar_estilo(fig3)
        st.plotly_chart(fig3)

# Verificação de se "Média de Upvotes por Tipo de Discurso de Ódio" está na lista de visualizações
if "Likes (Upvotes)" in visualizacoes:
    # Agrupar e calcular a média de upvotes por tipo de discurso
    media_upvotes = data_filtered.groupby("resultado_analise")["upvotes"].mean().reset_index()
    media_upvotes.columns = ["Tipo de Discurso", "Média de Upvotes"]
    
    # Verificar se há dados
    if not media_upvotes.empty:
        fig5 = px.bar(
            media_upvotes,
            x="Tipo de Discurso",
            y="Média de Upvotes",
            title="Média de Upvotes por Tipo de Discurso de Ódio",
            color="Tipo de Discurso",
            text_auto=True
        )
        fig5 = aplicar_estilo(fig5)
        st.plotly_chart(fig5)
    else:
        st.write("Não há dados de upvotes para os tipos de discurso de ódio.")

# Visualizações por Tipo de Discurso de Ódio
if "Visualizações" in visualizacoes:
    # Filtrar os dados para excluir "não é discurso de ódio"
    data_odio = data_filtered[data_filtered['resultado_analise'] != 'não é discurso de ódio']
    
    # Verificar se há dados após o filtro
    if not data_odio.empty:
        visualizacoes_por_tipo = data_odio.groupby("resultado_analise")["visualizacoes"].sum().reset_index()
        fig_visualizacoes_tipo = px.line(
            visualizacoes_por_tipo,
            x="resultado_analise",
            y="visualizacoes",
            title="Visualizações por Tipo de Discurso de Ódio",
            labels={"resultado_analise": "Tipo de Discurso de Ódio", "visualizacoes": "Total de Visualizações"},
            color_discrete_sequence=px.colors.qualitative.Bold
        )

        # Aplicar estilo e layout
        fig_visualizacoes_tipo.update_traces(mode="lines+markers", line=dict(width=3))

        # Função para aplicar o estilo de fundo e fontes
        aplicar_estilo(fig_visualizacoes_tipo)

        # Exibir o gráfico
        st.plotly_chart(fig_visualizacoes_tipo)
    else:
        st.write("Não há dados de discurso de ódio para exibir.")


import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import streamlit as st

if "Palavras mais comuns" in visualizacoes:
    # Filtrar os dados para considerar apenas discursos de ódio
    data_odio = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]
    
    if not data_odio.empty:
        stop_words = set(STOPWORDS)
        stop_words.update([
            "de", "como", "por", "mais", "quando", "se", "ele", "pra", "isso", "da", 
            "para", "com", "que", "em", "é", "e", "o", "a", "os", "como", "um", "uma", 
            "na", "no", "não", "mas", "ela", "eu", "você", "vocês", "nós", "eles", "elas", 
            "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas", "dele", "dela", 
            "deles", "delas", "esse", "essa", "esses", "essas", "este", "esta", "estes", 
            "estas", "aquele", "aquela", "aqueles", "aquelas", "lhe", "lhes", "do", "dos", 
            "das", "num", "numa", "neste", "nesta", "nisto", "naquele", "naquela", "nisso", 
            "daquilo", "e", "ou", "onde", "porque", "porquê", "lá", "aqui", "ali", "assim", 
            "tão", "já", "então", "também", "muito", "pouco", "sempre", "tudo", "nada", 
            "cada", "todos", "todas", "algum", "alguma", "nenhum", "nenhuma", "outro", 
            "outra", "outros", "outras", "seu", "sua", "seus", "suas", "me", "te", "nos", 
            "vos", "depois", "antes", "até", "ainda", "hoje", "ontem", "amanhã", "agora", 
            "lá", "cá", "sim", "não", "pois", "porém", "como", "sobre", "entre", "contra", 
            "sem", "baixo", "apenas", "mesmo", "era", "só", "coisa", "ser", "pessoa", "pai", 
            "cara", "tem", "bem", "foi", "pessoas", "ser", "sou", "ano", "vc", "queria", 
            "gente", "ao", "disse", "nunca", "sempre", "casa", "tempo", "nem", "mim", "q", 
            "que", "pq", "mãe", "mulher", "sala", "dia", "estava", "tenho", "vai", "começou", 
            "fazer", "são", "amigo", "namorada", "anos", "ter", "enquanto", "homem", "aí", 
            "tinha", "vida", "estou", "grupo", "coisas", "fui"
        ])

        # Gerar a nuvem de palavras a partir dos textos
        textos = " ".join(data_odio["texto"])  # Supondo que 'texto' seja a coluna com as postagens
        wordcloud = WordCloud(
            background_color="black",  # Fundo preto
            stopwords=stop_words,
            colormap="coolwarm",  # Escolher a coloração do gráfico
            width=800,
            height=400
        ).generate(textos)

        # Criando o gráfico com Matplotlib
        fig6, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")  # Remover os eixos

        # Estilo padronizado para o gráfico
        ax.set_facecolor("black")  # Cor do fundo do gráfico
        ax.title.set_color("white")  # Cor do título
        ax.xaxis.label.set_color("white")  # Cor do rótulo do eixo X
        ax.yaxis.label.set_color("white")  # Cor do rótulo do eixo Y
        ax.tick_params(axis='x', colors='white')  # Cor dos ticks do eixo X
        ax.tick_params(axis='y', colors='white')  # Cor dos ticks do eixo Y
        
        # Título do gráfico
        ax.set_title("Palavras Mais Comuns em Discurso de Ódio", fontsize=18, fontweight='bold', color="white", family="Arial, sans-serif")
        
        # Tornando o fundo da figura transparente
        fig6.patch.set_facecolor('none')  # Fundo transparente para o gráfico

        # Exibindo o gráfico com Streamlit
        st.pyplot(fig6)
    else:
        st.write("Não há dados de discurso de ódio para gerar a nuvem de palavras.")


# Frequência de Postagens por Usuário
if "Frequência por usuário" in visualizacoes:
    # Filtrar dados para incluir apenas discursos de ódio
    data_usuarios = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

    frequencia_postagens = (
        data_usuarios.groupby("usuario")
        .size()
        .reset_index(name="quantidade_postagens")
        .sort_values(by="quantidade_postagens", ascending=False)
        .head(10)  # Exibir os 10 usuários mais ativos
    )

    fig_frequencia = px.bar(
        frequencia_postagens,
        x="usuario",
        y="quantidade_postagens",
        title="Frequência de Postagens por Usuário (Discursos de Ódio)",
        labels={"usuario": "Usuário", "quantidade_postagens": "Quantidade de Postagens"},
        text_auto=True,
    )

    fig_frequencia.update_traces(marker_color="pink")
    fig_frequencia.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(title="Usuários", showgrid=False),
        yaxis=dict(title="Frequência de Postagens", showgrid=True, gridcolor="gray"),
        title=dict(font=dict(size=20)),
    )
    aplicar_estilo(fig_frequencia)
    st.plotly_chart(fig_frequencia)

# Quantidade de Respostas por Tipo de Discurso
# Quantidade de Respostas por Tipo de Discurso
if "Quantidade de Comentários" in visualizacoes:
    # Filtrar dados para discursos de ódio
    data_respostas = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]


    # Limpeza de espaços extras nas colunas, se necessário
    data_respostas.columns = data_respostas.columns.str.strip()

    # Agrupar pelos tipos de discurso e somar os comentários
    try:
        respostas_por_tipo = data_respostas.groupby("resultado_analise")["comentarios"].sum().reset_index()  # Alteração aqui

        # Criando o gráfico de barras
        fig_respostas_tipo = px.bar(
            respostas_por_tipo,
            x="resultado_analise",
            y="comentarios",  # Alterado de 'comentários' para 'comentarios'
            title="Quantidade de Respostas por Tipo de Discurso de Ódio",
            labels={"resultado_analise": "Tipo de Discurso de Ódio", "comentarios": "Total de Respostas"}  # Alterado aqui também
        )
        aplicar_estilo(fig_respostas_tipo)
        # Exibindo o gráfico
        st.plotly_chart(fig_respostas_tipo)
    except KeyError as e:
        st.error(f"Erro ao acessar a coluna: {e}")




# Nota de rodapé
st.write("""
---
Criado por: Isabelly Barbosa Gonçalves  
E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
Telefone: (13) 988372120  
Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
""")
