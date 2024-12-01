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
st.title("Análise de Discurso de Ódio no Reddit com ChatGPT")

# Tratamento de dados
dados["hora_postagem"] = pd.to_datetime(dados["hora_postagem"], errors="coerce")
dados["hora_postagem_formatada"] = dados["hora_postagem"].dt.strftime("%d/%m/%Y %H:%M:%S")

dados["engajamento"] = dados["upvotes"] + dados["comentarios"]
dados["eh_discurso_odio"] = dados["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

data_min = dados["hora_postagem"].min()
data_max = dados["hora_postagem"].max()

# Filtros
st.subheader("Filtros")

# Filtro por data
col1, col2 = st.columns(2)
with col1:
    data_inicio = st.date_input(
        "Data Inicial",
        min_value=data_min.date(),
        max_value=data_max.date()
    )
with col2:
    data_fim = st.date_input(
        "Data Final",
        min_value=data_min.date(),
        max_value=data_max.date()
    )

# Filtro por tipo de discurso e emoção
col3, col4 = st.columns(2)

with col3:
    filtro_discurso = st.multiselect(
        "Escolha o tipo de discurso que deseja visualizar",
        options=["todos"] + list(dados["resultado_analise"].unique())  # Adicionando "todos"
    )
with col4:
    filtro_emocao = st.multiselect(
        "Escolha o tipo de emoção que deseja visualizar",
        options=["todas"] + list(dados["emocao"].unique())  # Adicionando "todas"
    )

# Validação dos filtros
if not data_inicio or not data_fim:
    st.error("Por favor, selecione as datas inicial e final.")
    st.stop()

# Se não for selecionado nenhum filtro de discurso ou emoção, considerar todos
if "todos" in filtro_discurso:
    filtro_discurso = dados["resultado_analise"].unique().tolist()  # Seleciona todos os tipos de discurso
if "todas" in filtro_emocao:
    filtro_emocao = dados["emocao"].unique().tolist()  # Seleciona todas as emoções

# Aplicação de filtros
# Certifique-se de que a variável dados_filtrados está sendo definida corretamente
data_filtered = dados[
    (dados["hora_postagem"].dt.date >= data_inicio) & 
    (dados["hora_postagem"].dt.date <= data_fim) & 
    (dados["resultado_analise"].isin(filtro_discurso)) & 
    (dados["emocao"].isin(filtro_emocao))
]

# Verifique as colunas de dados_filtrados
st.write(data_filtered.columns)


# Exibição dos dados filtrados
st.subheader("Publicações Filtradas")
st.write(data_filtered[["hora_postagem_formatada", "resultado_analise", "emocao", "upvotes", "comentarios", "texto"]])

# Exibir contagem de discursos de ódio
if "eh_discurso_odio" in dados_filtrados.columns:
    contagem_odio = dados_filtrados["eh_discurso_odio"].value_counts()
    st.write("Contagem de Discurso de Ódio:")
    st.write(contagem_odio)
else:
    st.warning("A coluna 'eh_discurso_odio' não está disponível nos dados.")


import streamlit as st

# Seleção de gráficos
st.subheader("Visualizações")
visualizacoes = st.multiselect(
    "Escolha uma ou mais opções",  # Texto de escolha em português
    [
        "Discurso (Ódio/Não Ódio)",
        "Tipos de Discurso de Ódio",
        "Emoções",
        "Quantidade de Comentários",
        "Visualizações",
        "Likes (Upvotes)",
        "Frequência por tipo de discurso",
        "Frequência por usuário",
        "Palavras Mais Comuns"
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

    fig1 = aplicar_estilo(fig1)
    st.plotly_chart(fig1)

if "Tipos de Discurso de Ódio" in visualizacoes:
    # Certificando que a coluna 'hora_postagem' está em formato datetime
    if 'hora_postagem' in data_filtered.columns:
        data_filtered['hora_postagem'] = pd.to_datetime(data_filtered['hora_postagem'], errors='coerce')
    else:
        st.error("A coluna 'hora_postagem' não está presente nos dados.")
        raise ValueError("A coluna 'hora_postagem' não foi encontrada.")
    
    # Contar a quantidade de cada tipo de discurso de ódio
    discurso_tipo = data_filtered["resultado_analise"].value_counts().reset_index()
    discurso_tipo.columns = ["Tipo de Discurso", "Quantidade"]
    
    # Criando o gráfico de barras para visualizar os tipos de discurso de ódio
    fig8 = px.bar(
        discurso_tipo,
        x="Tipo de Discurso",
        y="Quantidade",
        title="Distribuição dos Tipos de Discurso de Ódio",
        labels={"Tipo de Discurso": "Tipo de Discurso de Ódio", "Quantidade": "Quantidade"},
        color="Tipo de Discurso",  # Diferencia as barras por tipo de discurso de ódio
        color_discrete_sequence=px.colors.qualitative.Set1  # Paleta de cores definida
    )
    
    # Aplicando o estilo ao gráfico
    fig8 = aplicar_estilo(fig8)
    
    # Exibindo apenas o gráfico
    st.plotly_chart(fig8)

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

        # Estilo e layout com fundo preto
        fig_visualizacoes_tipo.update_traces(mode="lines+markers", line=dict(width=3))
        fig_visualizacoes_tipo.update_layout(
            plot_bgcolor="black",
            paper_bgcolor="black",
            font=dict(color="white"),
            xaxis=dict(title="Tipos de Discurso de Ódio", showgrid=False),
            yaxis=dict(title="Visualizações", showgrid=True, gridcolor="gray"),
            title=dict(font=dict(size=20)),
            legend=dict(title="Tipos", font=dict(color="white"))
        )
        aplicar_estilo(fig_visualizacoes_tipo)
        st.plotly_chart(fig_visualizacoes_tipo)
    else:
        st.write("Não há dados de discurso de ódio para exibir.")

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import streamlit as st

if "Palavras Mais Comuns" in visualizacoes:
    # Filtrar os dados para excluir os que não são discurso de ódio
    if "resultado_analise" in data_filtered.columns and "texto" in data_filtered.columns:
        data_odio = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

        if not data_odio.empty:
            # Definir as stopwords
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

            # Combinar os textos para gerar a nuvem de palavras
            textos = " ".join(data_odio["texto"])  # Supondo que 'texto' seja a coluna com as postagens

            # Gerar a nuvem de palavras
            if textos.strip():
                wordcloud = WordCloud(
                    background_color="black", 
                    stopwords=stop_words,
                    colormap="coolwarm",
                    width=800,
                    height=400
                ).generate(textos)

                # Criar o gráfico
                fig6, ax = plt.subplots(figsize=(10, 5))

                # Configurar fundo e nuvem de palavras
                fig6.patch.set_facecolor("black")
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")

                # Configurar o título
                ax.set_title(
                    "Palavras Mais Comuns em Discurso de Ódio", 
                    fontsize=18, 
                    color="white", 
                    fontfamily="Arial", 
                    loc="left"
                )

                # Ajustar margens para alinhamento
                fig6.subplots_adjust(top=0.85)

                # Exibir no Streamlit
                st.pyplot(fig6, use_container_width=True)
            else:
                st.write("Nenhum texto disponível para gerar a nuvem de palavras.")
        else:
            st.write("Não há dados de discurso de ódio para gerar a nuvem de palavras.")
    else:
        st.write("A coluna 'resultado_analise' ou 'texto' não existe no DataFrame.")

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
if "Quantidade de Comentários" in visualizacoes:
    # Filtrar dados para discursos de ódio
    data_respostas = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

    respostas_por_tipo = data_respostas.groupby("resultado_analise")["comentarios"].sum().reset_index()

    fig_respostas_tipo = px.bar(
        respostas_por_tipo,
        x="resultado_analise",
        y="comentarios",
        title="Quantidade de Respostas por Tipo de Discurso de Ódio",
        labels={"resultado_analise": "Tipo de Discurso de Ódio", "comentarios": "Total de Respostas"}
    )
    aplicar_estilo(fig_respostas_tipo)
    st.plotly_chart(fig_respostas_tipo)


    # Nota de rodapé
    st.write("""
    ---
    Criado por: Isabelly Barbosa Gonçalves  
    E-mail: isabelly.barbosa@aluno.ifsp.edu.br  
    Telefone: (13) 988372120  
    Instituição de Ensino: Instituto Federal de Educação, Ciência e Tecnologia de São Paulo, Campus Cubatão
    """)
