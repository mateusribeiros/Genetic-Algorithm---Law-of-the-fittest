import math, random, pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Variáveis globais
VAR_REPRESENTACAO = 44


#---------------------------------------------------------------------------------------------------------------------------------
# FUNÇÕES ALEATÓRIAS E DE APTIDÃO
def aleatorizar_pop(populacao):
    pop_inicial = set()
    for _ in range(populacao):
        individuo = ''.join(random.choice('01') for _ in range(VAR_REPRESENTACAO))
        pop_inicial.add(individuo)
    return list(pop_inicial)

def obter_aptidao(populacao):
    aptidao = []
    for individuo in populacao:
        x, y = converter_bin_dec(individuo)
        apt = gerar_f6(x, y)
        aptidao.append(apt)
    return aptidao

#---------------------------------------------------------------------------------------------------------------------------------
# FUNÇÕES MATEMÁTICAS E DE TRANSFORMAÇÃO
def gerar_f6(x, y):
    numerador = math.sin(math.sqrt(x**2 + y**2))**2 - 0.5
    denominador = (1.0 + 0.001 * (x**2 + y**2))**2
    resultado = 0.5 - (numerador / denominador)
    return round(resultado, 7)

def converter_bin_dec(individuo):
    separacao = len(individuo) // 2
    var_x, var_y = individuo[:separacao], individuo[separacao:]
    x, y = int(var_x, 2), int(var_y, 2)
    bits = len(var_x)
    x_normalizado = -100 + (200 * x / (2**bits - 1)) 
    y_normalizado = -100 + (200 * y / (2**bits - 1))
    return x_normalizado, y_normalizado

#---------------------------------------------------------------------------------------------------------------------------------
# FUNÇÕES DE ROLETA, CROSSOVER E MUTAÇÃO
def roleta(populacao, aptidoes):
    menor_aptidao = min(aptidoes)

    # Essa escala de 1e-6 ajuda para diferenças pequenas entre as aptidões, identificando com mais precisão a fatia de cada
    escala_aptidao = [(apt - menor_aptidao + 1e-6)**2 for apt in aptidoes]
    soma_aptidoes = sum(escala_aptidao)

    if soma_aptidoes == 0:
        return random.choice(populacao)
    else:
        aleatorio = random.uniform(0, soma_aptidoes)
        acumulado = 0.0

        for i, apt in enumerate(escala_aptidao):
            acumulado += apt
            if acumulado >= aleatorio:
                return populacao[i]
    return populacao[-1]

def crossover (pai1, pai2, taxa_crossover):
    posicao = random.choice(range(1, int(VAR_REPRESENTACAO - 1)))

    p1_cabeca, p1_cauda = pai1[:posicao], pai1[posicao:]
    p2_cabeca, p2_cauda = pai2[:posicao], pai2[posicao:]

    if random.random() < taxa_crossover:
        cross1 = p1_cabeca + p2_cauda
        cross2 = p2_cabeca + p1_cauda
        return cross1, cross2
    
    return pai1, pai2

def mutacao(individuo, taxa_mutacao):
    novo_individuo = ''

    for cromossomo in individuo:
        if random.random() < taxa_mutacao:
            novo_cromossomo = '1' if cromossomo == '0' else '0'
            novo_individuo += novo_cromossomo
        else:
            novo_individuo += cromossomo

    return novo_individuo

#---------------------------------------------------------------------------------------------------------------------------------
# PRINCIPAL
def algoritmo_genetico(pop_tamanho,num_ger,taxa_crossover,taxa_mutacao):
    random.seed()
    # gerar populacao inicial
    populacao = aleatorizar_pop(pop_tamanho)
    dados = [] # Para gerar um arquivo csv

    melhor_individuo = None
    melhor_aptidao = float('inf')
    melhores_pais = (None, None)
    melhor_ger = None

    melhor_ind_por_ger = []
    media_por_ger = []

    for geracao in range(1,num_ger):
        aptidoes = obter_aptidao(populacao)

        melhor_apt_local = max(aptidoes)
        melhor_ind_local = populacao[aptidoes.index(melhor_apt_local)]
        x, y = converter_bin_dec(melhor_ind_local)

        melhor_ind_por_ger.append([melhor_ind_local, x, y, melhor_apt_local, geracao])
        media_por_ger.append(sum(aptidoes) / len(aptidoes))

        nova_populacao = []

        if geracao == 1:
            # Armazenar dados do indivíduo
            for individuo, aptidao in zip(populacao, aptidoes):
                x, y = converter_bin_dec(individuo)
                dados.append([geracao, individuo, x, y, aptidao, None, None, None])

            # Atualizar melhor indivíduo global
            if melhor_apt_local < melhor_aptidao:
                melhor_aptidao = melhor_apt_local
                melhor_individuo = populacao[aptidoes.index(melhor_apt_local)]
                melhor_ger = geracao

        while len(nova_populacao) < pop_tamanho:
            pai1 = roleta(populacao, aptidoes)
            pai2 = roleta(populacao, aptidoes)
            
            cross1, cross2 = crossover(pai1, pai2, taxa_crossover)

            mut_filho1 = mutacao(cross1, taxa_mutacao)
            mut_filho2 = mutacao(cross2, taxa_mutacao)

            x1, y1 = converter_bin_dec(mut_filho1)
            x2, y2 = converter_bin_dec(mut_filho2)

            apt_filho1 = gerar_f6(x1, y1)
            apt_filho2 = gerar_f6(x2, y2)

            dados.append([geracao+1, mut_filho1, x1, y1, apt_filho1, pai1, pai2, geracao])
            dados.append([geracao+1, mut_filho2, x2, y2, apt_filho2, pai1, pai2, geracao])

            # if apt_filho1 > melhor_aptidao:
            #     melhor_aptidao = apt_filho1
            #     melhor_individuo = mut_filho1
            #     melhor_ger = geracao+1
            # if apt_filho2 > melhor_aptidao:
            #     melhor_aptidao = apt_filho2
            #     melhor_individuo = mut_filho2
            #     melhor_ger = geracao+1

            nova_populacao.extend([mut_filho1, mut_filho2])

        nova_populacao[0] = melhor_individuo
        populacao = nova_populacao[:pop_tamanho]
    
    df = pd.DataFrame(dados, columns=["geracao","cromossomo","x","y","aptidao","pai1","pai2","geracao_pais"])
    df.to_csv("resultados_ag.csv", index=False)

    df_unique = df.sort_values(by="aptidao", ascending=False).drop_duplicates(subset="cromossomo", keep="first")
    top_df = df_unique.head(8)
    top8 = [(row["cromossomo"], row["x"], row["y"], row["aptidao"], int(row["geracao"])) for _, row in top_df.iterrows()]

    melhor_linha = df.loc[df["aptidao"].idxmax()]
    melhor_individuo = melhor_linha["cromossomo"]
    x_melhor, y_melhor = melhor_linha["x"], melhor_linha["y"]
    melhor_aptidao = melhor_linha["aptidao"]
    melhor_ger = int(melhor_linha["geracao"])
    melhores_pais = (melhor_linha["pai1"], melhor_linha["pai2"])
    geracao_pais = int(melhor_linha["geracao_pais"])

    return melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger, melhores_pais, df, geracao_pais, top8, melhor_ind_por_ger, media_por_ger

# Interface
st.set_page_config(page_title="Algoritmo Genético F6", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "setup"

# ---------- Página Setup ----------
if st.session_state.page == "setup":
    st.title("🧬 Algoritmo Genético — Função F6")
    st.markdown("Configure os parâmetros do algoritmo genético abaixo:")

    tamanho_populacao = st.number_input("Tamanho da população", min_value=10, max_value=10000, value=100)
    geracoes = st.number_input("Número de gerações", min_value=1, max_value=10000, value=50)

    taxa_crossover = st.number_input(
        "Taxa de Crossover (0.0 - 1.0)", min_value=0.0, max_value=1.0, value=0.65, format="%.2f", step=0.01
    )
    taxa_mutacao = st.number_input(
        "Taxa de Mutação (0.0 - 1.0)", min_value=0.0, max_value=1.0, value=0.008, format="%.3f", step=0.001
    )

    if st.button("🚀 Executar Algoritmo"):
        with st.spinner("Executando AG — isso pode levar alguns segundos/minutos..."):
            melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger, melhores_pais, df, geracao_pais, top8, melhor_ind_por_ger, media_por_ger = algoritmo_genetico(
                tamanho_populacao, geracoes, taxa_crossover, taxa_mutacao
            )
        st.session_state.update({
            "melhor_tupla": (melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger),
            "top8": top8,
            "pais": melhores_pais,
            "melhor_ger": melhor_ger,
            "geracao_pais": geracao_pais,
            "df": df,
            "melhor_ind_por_ger": melhor_ind_por_ger,
            "media_por_ger": media_por_ger,
            "page": "results"
        })
        st.rerun()

# ---------- Página Results ----------
elif st.session_state.page == "results":
    if "melhor_tupla" not in st.session_state:
        st.warning("Nenhum resultado disponível. Execute uma simulação primeiro.")
        if st.button("Voltar para configuração"):
            st.session_state.page = "setup"
            st.rerun()
    else:
        melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger = st.session_state.melhor_tupla
        top8 = st.session_state.top8
        pais = st.session_state.pais
        melhor_ger = st.session_state.melhor_ger
        geracao_pais = st.session_state.geracao_pais
        melhor_ind_por_ger = st.session_state.melhor_ind_por_ger

        st.title("🏆 Resultado do Algoritmo Genético")
        st.subheader("Melhor Indivíduo (Global)")
        st.code(f"Cromossomo: {melhor_individuo}", language="text")
        st.write(f"**X:** {(x_melhor):.6f}   **Y:** {(y_melhor):.6f}   **Aptidão:** {(melhor_aptidao):.10f}   **Geração:** {melhor_ger}")

        if pais and (pais != (None, None)):
            p1, p2 = pais
            st.subheader("Pais do Melhor Indivíduo")
            if p1:
                x1, y1 = converter_bin_dec(p1)
                st.markdown(f"**Pai 1** — X={(x1):.6f}, Y={(y1):.6f}, Aptidão={(gerar_f6(x1,y1)):.10f}, Geração={geracao_pais}")
                st.code(p1, language="text")
            if p2:
                x2, y2 = converter_bin_dec(p2)
                st.markdown(f"**Pai 2** — X={(x2):.6f}, Y={(y2):.6f}, Aptidão={(gerar_f6(x2,y2)):.10f}, Geração={geracao_pais}")
                st.code(p2, language="text")
        else:
            st.info("Pais não identificados (indivíduo inicial).")

        st.subheader("Top 8 Globais (todas as gerações)")
        df_top8 = pd.DataFrame(top8, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_top8["Aptidao"] = df_top8["Aptidao"]
        df_top8["Cromossomo"] = df_top8["Cromossomo"]
        df_top8["X"] = df_top8["X"]
        df_top8["Y"] = df_top8["Y"]
        st.dataframe(
            df_top8.style.format({
                "Cromossomo": lambda v: f"{v}",
                "X": lambda v: f"{(v):.6f}",
                "Y": lambda v: f"{(v):.6f}",
                "Aptidao": lambda v: f"{(v):.10f}",
                "Geração": lambda v: f"{v}",
            }),
            width="stretch"
        )

        st.subheader("Melhores Indivíduos por Geração")
        df_gen = pd.DataFrame(melhor_ind_por_ger, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_gen["Aptidao"] = df_gen["Aptidao"]
        df_gen["Cromossomo"] = df_gen["Cromossomo"]
        df_gen["Geração"] = df_gen["Geração"]
        df_gen["X"] = df_gen["X"]
        df_gen["Y"] = df_gen["Y"]
        st.dataframe(
            df_gen.style.format({
                "Cromossomo": lambda v: f"{v}",
                "X": lambda v: f"{(v):.4f}",
                "Y": lambda v: f"{(v):.4f}",
                "Aptidao": lambda v: f"{(v):.10f}",
                "Geração": lambda v: f"{v}",
            }),
            width="stretch"
        )

        col1, col2= st.columns(2)
        if col1.button("🔁 Nova simulação"):
            st.session_state.page = "setup"
            st.rerun()
        if col2.button("📊 Prosseguir para análise"):
            st.session_state.page = "analysis"
            st.rerun()

# ---------- Página Analysis ----------
elif st.session_state.page == "analysis":
    df = st.session_state.df
    media_por_ger = st.session_state.media_por_ger
    top8 = st.session_state.top8
    melhor_ind_por_ger = st.session_state.melhor_ind_por_ger

    st.title("📈 Análises e Gráficos da População")
    st.markdown("""
    **Descrição das análises disponíveis**
    - **Evolução da Aptidão**: curva do melhor e da média por geração.
    - **Distribuição das Aptidões**: histograma de concentração e caudas.
    - **Dispersão X×Y**: mapa colorido pela aptidão (regiões promissoras).
    - **Top5 Globais**: tabela comparativa.
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["📉 Evolução", "📊 Distribuição", "🧭 Dispersão X×Y", "📋 Top5 & Estatística"])

    with tab1:
        fig, ax = plt.subplots()
        aptidoes_por_ger = [ind[3] for ind in melhor_ind_por_ger]
        ax.plot(aptidoes_por_ger, label="Melhor por geração")
        ax.plot(media_por_ger, label="Média por geração")
        ax.set_title("Evolução da Aptidão")
        ax.set_xlabel("Geração")
        ax.set_ylabel("Aptidão")
        ax.legend()
        st.pyplot(fig)

    with tab2:
        fig = px.histogram(df, x="aptidao", nbins=30, title="Distribuição das Aptidões")
        st.plotly_chart(fig, width="stretch")

    with tab3:
        fig = px.scatter(df, x="x", y="y", color="aptidao", title="Dispersão X×Y", color_continuous_scale="viridis")
        st.plotly_chart(fig, width="stretch")

    with tab4:
        st.subheader("Top 8 Globais (todas as gerações)")
        df_top8 = pd.DataFrame(top8, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_top8["Aptidao"] = df_top8["Aptidao"]
        df_top8["Cromossomo"] = df_top8["Cromossomo"]
        df_top8["X"] = df_top8["X"]
        df_top8["Y"] = df_top8["Y"]
        st.dataframe(
            df_top8.style.format({
                "Cromossomo": lambda v: f"{v}",
                "X": lambda v: f"{(v):.6f}",
                "Y": lambda v: f"{(v):.6f}",
                "Aptidao": lambda v: f"{(v):.10f}",
                "Geração": lambda v: f"{v}",
            }),
            width="stretch"
        )

        st.subheader("Estatísticas da população (arquivo resultados_ag.csv)")
        st.write(df["aptidao"].describe())
        high = df[df["aptidao"] > df["aptidao"].mean() + df["aptidao"].std()]
        st.markdown(f"🔹 Indivíduos acima da média + 1 desvio padrão: **{len(high)}**")

        st.subheader("Melhores Indivíduos por Geração")
        df_gen = pd.DataFrame(melhor_ind_por_ger, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_gen["Aptidao"] = df_gen["Aptidao"]
        df_gen["Cromossomo"] = df_gen["Cromossomo"]
        df_gen["Geração"] = df_gen["Geração"]
        df_gen["X"] = df_gen["X"]
        df_gen["Y"] = df_gen["Y"]
        st.dataframe(
            df_gen.style.format({
                "Cromossomo": lambda v: f"{v}",
                "X": lambda v: f"{(v):.4f}",
                "Y": lambda v: f"{(v):.4f}",
                "Aptidao": lambda v: f"{(v):.10f}",
                "Geração": lambda v: f"{v}",
            }),
            width="stretch"
        )

    col1, col2 = st.columns(2)
    if col1.button("🔁 Nova simulação"):
        st.session_state.page = "setup"
        st.rerun()
    if col2.button("⬅️ Voltar"):
        st.session_state.page = "results"
        st.rerun()
