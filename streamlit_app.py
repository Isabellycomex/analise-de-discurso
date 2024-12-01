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

dados["hora_postagem"] = pd.to_datetime(dados["hora_postagem"], errors="coerce")
dados["hora_postagem_formatada"] = dados["hora_postagem"].dt.strftime("%d/%m/%Y %H:%M:%S")
dados["engajamento"] = dados["upvotes"] + dados["comentarios"]
dados["eh_discurso_odio"] = dados["resultado_analise"].apply(
    lambda x: "Discurso de Ódio" if x != "não é discurso de ódio" else "Não é Discurso de Ódio"
)

data_min = dados["hora_postagem"].min()
data_max = dados["hora_postagem"].max()
data_inicio_default = data_min.date() if pd.notnull(data_min) else None
data_fim_default = data_max.date() if pd.notnull(data_max) else None

# Filtros
st.subheader("Filtros")
import streamlit as st
from datetime import datetime

# Valores padrão para as datas
data_inicio_default = datetime(2017, 9, 1).strftime('%d/%m/%Y')  # 01/12/2024
data_fim_default = datetime(2024, 12, 31).strftime('%d/%m/%Y')  # 31/12/2024
data_min = datetime(2024, 1, 1)
data_max = datetime(2024, 12, 31)

col1, col2 = st.columns(2)

with col1:
    data_inicio_str = st.text_input(
        "Data Inicial",
        value=data_inicio_default,
        key="data_inicio"
    )
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y').date()
    except ValueError:
        st.error("Por favor, insira uma data válida no formato dd/mm/aaaa")
        data_inicio = None

with col2:
    data_fim_str = st.text_input(
        "Data Final",
        value=data_fim_default,
        key="data_fim"
    )
    try:
        data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y').date()
    except ValueError:
        st.error("Por favor, insira uma data válida no formato dd/mm/aaaa")
        data_fim = None

col3, col4 = st.columns(2)

with col3:
    filtro_discurso = st.multiselect(
        "Escolha o tipo de discurso que deseja visualizar",
        options=["Todos"] + list(dados["resultado_analise"].unique()),
        default=[],
        key="filtro_discurso"
    )
    if "Todos" in filtro_discurso:
        filtro_discurso = list(dados["resultado_analise"].unique())

with col4:
    filtro_emocao = st.multiselect(
        "Escolha o tipo de emoção que deseja visualizar",
        options=["Todas"] + list(dados["emocao"].unique()),
        default=[],
        key="filtro_emocao"
    )
    if "Todas" in filtro_emocao:
        filtro_emocao = list(dados["emocao"].unique())

# Verificação se os filtros foram preenchidos
if not data_inicio or not data_fim or not filtro_discurso or not filtro_emocao:
    st.warning("Preencha todos os filtros para continuar.")
    st.stop()

# Aplicação de filtros
data_filtered = dados[
    (dados["hora_postagem"].dt.date >= data_inicio) &
    (dados["hora_postagem"].dt.date <= data_fim) &
    (dados["resultado_analise"].isin(filtro_discurso)) &
    (dados["emocao"].isin(filtro_emocao))
]

import streamlit as st

# Configurar os títulos das colunas para a tabela
colunas_legiveis = {
    "hora_postagem": "Data e Hora em que a Publicação foi feita",
    "usuario": "Usuário",
    "resultado_analise": "Resultado da Análise do Discurso",
    "emocao": "Emoção Predominante",
    "upvotes": "Likes",
    "comentarios": "Comentários",
    "texto": "Publicação"
}

# Verificar se todas as colunas do dicionário estão presentes no DataFrame
colunas_existentes = [coluna for coluna in colunas_legiveis if coluna in data_filtered.columns]

# Configuração inicial de paginação
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 1

# Quantidade de itens por página
ITENS_POR_PAGINA = 10

# Configuração para limitar a navegação
PAGINA_MINIMA = 1
PAGINA_MAXIMA = 31

# Verificar se o DataFrame filtrado não está vazio
if not data_filtered.empty:
    # Número total de páginas dentro do limite
    total_itens = len(data_filtered)
    total_paginas = min(PAGINA_MAXIMA, (total_itens + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)

    # Ajustar a página atual para estar no intervalo permitido
    st.session_state.pagina_atual = max(
        PAGINA_MINIMA, min(st.session_state.pagina_atual, total_paginas)
    )

    # Instruções para o usuário
    st.markdown(
        """
        ### Publicações Filtradas
        #### Dicas de Uso:
        - Use os botões **Próximo** e **Anterior** para navegar entre as páginas.
        - Role a tabela para **baixo** ou para os **lados** para ver mais detalhes das publicações.
        - Cada página exibe até **10 publicações**.
        - Navegação limitada às páginas **1 a 31**.
        - Clique no **campo** que deseja visualizar para verificar todos os dados do mesmo.
        """
    )

    # Cálculo de índices de acordo com a página atual
    inicio = (st.session_state.pagina_atual - 1) * ITENS_POR_PAGINA
    fim = min(inicio + ITENS_POR_PAGINA, total_itens)  # Garantir que não ultrapasse o limite
    tabela_pagina = data_filtered.iloc[inicio:fim][colunas_existentes].rename(columns=colunas_legiveis)

    # Exibir a tabela formatada com largura maior
    st.dataframe(
        tabela_pagina,
        use_container_width=True,  # Largura total da tela
        height=350,  # Altura adequada para 10 linhas
    )

    # Botões de navegação
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Anterior", disabled=(st.session_state.pagina_atual <= PAGINA_MINIMA)):
            st.session_state.pagina_atual -= 1

    with col3:
        if st.button("Próximo", disabled=(st.session_state.pagina_atual >= PAGINA_MAXIMA)):
            st.session_state.pagina_atual += 1

    # Exibir página atual
    st.text(f"Página {st.session_state.pagina_atual} de {PAGINA_MAXIMA}")

else:
    # Caso o DataFrame esteja vazio
    st.error("Nenhuma publicação encontrada com os filtros selecionados. Ajuste os filtros e tente novamente.")

# Visualizações
st.subheader("Visualizações")
# Visualizações
st.subheader("Visualizações")

# Opções disponíveis
opcoes = [
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

# Multiselect com a opção "Todos" adicionada
visualizacoes = st.multiselect(
    "Escolha uma ou mais opções",
    ["Todos"] + opcoes  # "Todos" adicionado
)

# Lógica para tratar a seleção de "Todos"
if "Todos" in visualizacoes:
    visualizacoes = opcoes  # Seleciona todas as opções

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

# Verificando se 'hora_postagem' é datetime
if 'hora_postagem' in data_filtered.columns:
    data_filtered['hora_postagem'] = pd.to_datetime(data_filtered['hora_postagem'], errors='coerce')
else:
    st.error("A coluna 'hora_postagem' não está presente nos dados.")
    raise ValueError("A coluna 'hora_postagem' não foi encontrada.")

# Filtrar os dados para discurso de ódio
if "Frequência por tipo de discurso" in visualizacoes:
    # Filtrar os dados com base no tipo de discurso
    odio_tempo = data_filtered[data_filtered["resultado_analise"].isin(["racismo", "homofobia", "sexismo", "xenofobia", "transfobia", "não é discurso de ódio"])]
    
    # Agrupar por mês e tipo de discurso
    odio_tempo["mes_postagem"] = odio_tempo["hora_postagem"].dt.to_period("M").astype(str)  # Converter para string
    odio_por_tipo_tempo = odio_tempo.groupby(["mes_postagem", "resultado_analise"]).size().reset_index(name="count")

    # Criar o gráfico de linhas com Plotly Express
    fig3 = px.line(
        odio_por_tipo_tempo,
        x="mes_postagem",
        y="count",
        color="resultado_analise",
        title="Tipos de Discurso de Ódio ao Longo do Tempo",
        labels={"mes_postagem": "Mês", "count": "Quantidade", "resultado_analise": "Tipo de Discurso de Ódio"},
        markers=True  # Marca os pontos de cada linha
    )
    
    # Aplicar o estilo ao gráfico (caso haja uma função 'aplicar_estilo')
    fig3 = aplicar_estilo(fig3)
    
    # Exibir o gráfico
    st.plotly_chart(fig3)

if "Visualizações" in visualizacoes:
    # Agrupar os dados por tipo de análise, incluindo "não é discurso de ódio"
    visualizacoes_por_tipo = data_filtered.groupby("resultado_analise")["visualizacoes"].sum().reset_index()

    # Certificar-se de que todas as categorias (incluindo 'não é discurso de ódio') estão presentes
    tipos_discurso = ["não é discurso de ódio", "racismo", "homofobia", "machismo", "sexismo"]  # Adicione os tipos desejados aqui

    # Garantir que todos os tipos de discurso apareçam, mesmo os sem dados
    for tipo in tipos_discurso:
        if tipo not in visualizacoes_por_tipo["resultado_analise"].values:
            # Criar um DataFrame temporário para o tipo ausente
            temp_df = pd.DataFrame({"resultado_analise": [tipo], "visualizacoes": [0]})
            # Concatenar o DataFrame original com o novo DataFrame
            visualizacoes_por_tipo = pd.concat([visualizacoes_por_tipo, temp_df], ignore_index=True)

    # Ordenar as barras em ordem decrescente de visualizações
    visualizacoes_por_tipo = visualizacoes_por_tipo.sort_values("visualizacoes", ascending=False)

    # Criar gráfico de barras para visualizações por tipo de discurso
    fig_visualizacoes_tipo = px.bar(
        visualizacoes_por_tipo,
        x="resultado_analise",
        y="visualizacoes",
        title="Visualizações por Tipo de Discurso",
        labels={"resultado_analise": "Resultado da Análise", "visualizacoes": "Total de Visualizações"},
        color=None,  # Remover a diferenciação por cor
        color_discrete_sequence=["#1f77b4"]  # Aplicar uma cor única
    )

    # Ajustes de estilo e layout
    fig_visualizacoes_tipo.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(title="Tipos de Discurso", showgrid=False),
        yaxis=dict(title="Visualizações", showgrid=True, gridcolor="gray"),
        title=dict(font=dict(size=20)),
        showlegend=False  # Remover a legenda
    )

    # Aplicar estilo customizado
    aplicar_estilo(fig_visualizacoes_tipo)
    st.plotly_chart(fig_visualizacoes_tipo)

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

if "Frequência por usuário" in visualizacoes:
    # Filtrar dados para incluir apenas discursos de ódio
    data_usuarios = data_filtered[data_filtered["resultado_analise"] != "não é discurso de ódio"]

    # Calcular a frequência de postagens por usuário e pegar os 5 mais ativos
    frequencia_postagens = (
        data_usuarios.groupby("usuario")
        .size()
        .reset_index(name="quantidade_postagens")
        .sort_values(by="quantidade_postagens", ascending=False)
        .head(5)  # Exibir os 5 usuários mais ativos
    )

    # Criar o gráfico de barras
    fig_frequencia = px.bar(
        frequencia_postagens,
        x="usuario",
        y="quantidade_postagens",
        title="Top 5 Usuários que Mais Publicaram Discursos de Ódio",
        labels={"usuario": "Usuário", "quantidade_postagens": "Quantidade de Postagens"},
        text_auto=True,
    )

    # Estilo do gráfico
    fig_frequencia.update_traces(marker_color="pink")
    fig_frequencia.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(title="Usuários", showgrid=False),
        yaxis=dict(title="Frequência de Postagens", showgrid=True, gridcolor="gray"),
        title=dict(font=dict(size=20)),
    )
    
    # Aplicar estilo adicional, se necessário
    aplicar_estilo(fig_frequencia)
    
    # Exibir o gráfico
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
        title="Quantidade de Comentários por Tipo de Discurso de Ódio",
        labels={"resultado_analise": "Tipo de Discurso de Ódio", "comentarios": "Total de Comentários"}
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
