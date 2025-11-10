import random
import math
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# ---------------------------
# Parâmetros gerais
# ---------------------------
CHROMOSOME_LEN = 44
BITS_PER_VAR = CHROMOSOME_LEN // 2
MAX_INIT_ATTEMPTS = 10000  # limite para gerar população sem duplicatas

# ------------------------------------------
# Função F6(x, y)
# ------------------------------------------
def f6(x, y):
    numerador = (math.sin(math.sqrt(x**2 + y**2)))**2 - 0.5
    denominador = (1.0 + 0.001*(x**2 + y**2))**2
    return 0.5 - (numerador / denominador)

# ------------------------------------------
# Evitar arredondamento em exibição da aptidão
# ------------------------------------------
def truncar_6(x):
    return math.floor(x * 10**8) / 10**8

# ------------------------------------------
# Conversão binária - real
# ------------------------------------------
def bin_to_real(binary):
    mid = len(binary)//2
    x_bits, y_bits = binary[:mid], binary[mid:]
    x_dec = int(x_bits, 2)
    y_dec = int(y_bits, 2)
    x = -100 + (200 * x_dec / (2**BITS_PER_VAR - 1))
    y = -100 + (200 * y_dec / (2**BITS_PER_VAR - 1))
    return x, y

# ------------------------------------------
# Inicialização, avaliação, seleção, crossover e mutação
# ------------------------------------------
def init_population(size):
    """Gera população garantindo (na medida do possível) cromossomos únicos."""
    pop = set()
    attempts = 0
    while len(pop) < size and attempts < MAX_INIT_ATTEMPTS:
        chrom = ''.join(random.choice('01') for _ in range(CHROMOSOME_LEN))
        if chrom not in pop:
            pop.add(chrom)
        attempts += 1
    while len(pop) < size:
        chrom = ''.join(random.choice('01') for _ in range(CHROMOSOME_LEN))
        pop.add(chrom)
    return list(pop)

def evaluate_population(population):
    return [f6(*bin_to_real(ind)) for ind in population]

def roulette_selection(population, fitness):
    # Escala as aptidões para aumentar contraste
    min_fit = min(fitness)
    scaled_fitness = [(f - min_fit + 1e-6)**2 for f in fitness] 
    total_fit = sum(scaled_fitness)

    if total_fit == 0:
        return random.choice(population)

    rand = random.uniform(0, total_fit)
    acum = 0.0
    for i, fit in enumerate(scaled_fitness):
        acum += fit
        if acum >= rand:
            return population[i]
    return population[-1]


def crossover(p1, p2, rate):
    if random.random() < rate:
        point = random.randint(1, len(p1)-1)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]
        return c1, c2, True
    return p1, p2, False

def mutate(individual, rate):
    out = []
    for b in individual:
        if random.random() < rate:
            out.append('0' if b == '1' else '1')
        else:
            out.append(b)
    return ''.join(out)

# ------------------------------------------
# Algoritmo Genético (com registro determinístico de pais)
# ------------------------------------------
def genetic_algorithm(pop_size, generations, crossover_rate, mutation_rate):
    random.seed()  # garante diversidade entre execuções
    population = init_population(pop_size)
    data = []  # id, geracao, cromossomo, x, y, aptidao, pai1, pai2
    id_counter = 1

    best_ind = None
    best_fit = -float('inf')
    best_parents = (None, None)
    best_gen = None

    best_per_gen = []
    avg_per_gen = []

    for gen in range(1, generations+1):
        fitness = evaluate_population(population)
        avg_per_gen.append(sum(fitness)/len(fitness))
        gen_best_fit = max(fitness)
        best_per_gen.append(gen_best_fit)

        # Registra população atual (pais) — sem pais conhecidos
        for ind, fit in zip(population, fitness):
            x, y = bin_to_real(ind)
            fit_trunc = truncar_6(fit)
            data.append([id_counter, gen, ind, x, y, fit_trunc, None, None])
            id_counter += 1

        # Atualiza melhor global
        if gen_best_fit > best_fit:
            best_fit = gen_best_fit
            best_ind = population[fitness.index(gen_best_fit)]
            best_gen = gen

        # Geração de filhos
        new_pop = []
        elite = population[fitness.index(gen_best_fit)]

        while len(new_pop) < pop_size:
            p1 = roulette_selection(population, fitness)
            p2 = roulette_selection(population, fitness)
            c1, c2, crossed = crossover(p1, p2, crossover_rate)
            c1 = mutate(c1, mutation_rate)
            c2 = mutate(c2, mutation_rate)

            # Avaliar filhos e registrar
            x1, y1 = bin_to_real(c1)
            fit_c1 = f6(x1, y1)
            fit_trunc = truncar_6(fit_c1)
            data.append([id_counter, gen+1, c1, x1, y1, fit_trunc, p1, p2])
            id_counter += 1

            x2, y2 = bin_to_real(c2)
            fit_c2 = f6(x2, y2)
            fit_trunc = truncar_6(fit_c2)
            data.append([id_counter, gen+1, c2, x2, y2, fit_trunc, p1, p2])
            id_counter += 1

            if fit_c1 > best_fit:
                best_fit = fit_c1
                best_ind = c1
                best_parents = (p1, p2)
                best_gen = gen+1
            if fit_c2 > best_fit:
                best_fit = fit_c2
                best_ind = c2
                best_parents = (p1, p2)
                best_gen = gen+1

            new_pop.extend([c1, c2])

        # elitismo
        new_pop[0] = elite
        population = new_pop[:pop_size]

    # Cria DataFrame e salva CSV
    df = pd.DataFrame(data, columns=["id","geracao","cromossomo","x","y","aptidao","pai1","pai2"])
    df.to_csv("resultados_ag.csv", index=False)

    # Top 5 globais (sem duplicatas)
    df_unique = df.sort_values(by="aptidao", ascending=False).drop_duplicates(subset="cromossomo", keep="first")
    top_df = df_unique.head(5)
    top5 = [(row["cromossomo"], row["x"], row["y"], row["aptidao"], int(row["geracao"])) for _, row in top_df.iterrows()]

    # Melhor global e pais
    best_row = df.loc[df["aptidao"].idxmax()]
    best_ind = best_row["cromossomo"]
    x_best, y_best = best_row["x"], best_row["y"]
    best_fit = best_row["aptidao"]
    best_gen = int(best_row["geracao"])
    best_parents = (best_row["pai1"], best_row["pai2"])

    return best_ind, x_best, y_best, best_fit, top5, best_parents, best_gen, df, best_per_gen, avg_per_gen

# ------------------------------------------
# Interface Streamlit
# ------------------------------------------
st.set_page_config(page_title="Algoritmo Genético F6", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "setup"

# ---------- Página Setup ----------
if st.session_state.page == "setup":
    st.title("🧬 Algoritmo Genético — Função F6")
    st.markdown("Configure os parâmetros do algoritmo genético abaixo:")

    pop_size = st.number_input("Tamanho da população (10 - 500)", min_value=10, max_value=500, value=100)
    generations = st.number_input("Número de gerações (1 - 5000)", min_value=1, max_value=5000, value=50)

    crossover_rate = st.number_input(
        "Taxa de Crossover (0.0 - 1.0)", min_value=0.0, max_value=1.0, value=0.65, format="%.2f", step=0.01
    )
    mutation_rate = st.number_input(
        "Taxa de Mutação (0.0 - 1.0)", min_value=0.0, max_value=1.0, value=0.008, format="%.3f", step=0.001
    )

    if st.button("🚀 Executar Algoritmo"):
        with st.spinner("Executando AG — isso pode levar alguns segundos/minutos..."):
            best, x, y, fit, top5, parents, best_gen, df, best_per_gen, avg_per_gen = genetic_algorithm(
                pop_size, generations, crossover_rate, mutation_rate
            )
        st.session_state.update({
            "best_tuple": (best, x, y, fit),
            "top5": top5,
            "parents": parents,
            "best_gen": best_gen,
            "df": df,
            "best_per_gen": best_per_gen,
            "avg_per_gen": avg_per_gen,
            "page": "results"
        })
        st.rerun()

# ---------- Página Results ----------
elif st.session_state.page == "results":
    if "best_tuple" not in st.session_state:
        st.warning("Nenhum resultado disponível. Execute uma simulação primeiro.")
        if st.button("Voltar para configuração"):
            st.session_state.page = "setup"
            st.rerun()
    else:
        best, x, y, fit = st.session_state.best_tuple
        top5 = st.session_state.top5
        parents = st.session_state.parents
        best_gen = st.session_state.best_gen

        st.title("🏆 Resultado do Algoritmo Genético")
        st.subheader("Melhor Indivíduo (Global)")
        st.code(f"Cromossomo: {best}", language="text")
        st.write(f"**X:** {truncar_6(x):.6f}   **Y:** {truncar_6(y):.6f}   **Aptidão:** {truncar_6(fit):.10f}   **Geração:** {best_gen}")

        if parents and (parents != (None, None)):
            p1, p2 = parents
            st.subheader("Pais do Melhor Indivíduo")
            if p1:
                x1, y1 = bin_to_real(p1)
                st.markdown(f"**Pai 1** — X={truncar_6(x1):.6f}, Y={truncar_6(y1):.6f}, Aptidão={truncar_6(f6(x1,y1)):.10f}, Geração={best_gen}")
                st.code(p1, language="text")
            if p2:
                x2, y2 = bin_to_real(p2)
                st.markdown(f"**Pai 2** — X={truncar_6(x2):.6f}, Y={truncar_6(y2):.6f}, Aptidão={truncar_6(f6(x2,y2)):.10f}, Geração={best_gen}")
                st.code(p2, language="text")
        else:
            st.info("Pais não identificados (indivíduo inicial).")

        st.subheader("Top 5 Globais (todas as gerações)")
        df_top5 = pd.DataFrame(top5, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_top5["Aptidao"] = df_top5["Aptidao"].apply(truncar_6)
        df_top5["X"] = df_top5["X"].apply(truncar_6)
        df_top5["Y"] = df_top5["Y"].apply(truncar_6)
        st.dataframe(
            df_top5.style.format({
                "X": lambda v: f"{truncar_6(v):.4f}",
                "Y": lambda v: f"{truncar_6(v):.4f}",
                "Aptidao": lambda v: f"{truncar_6(v):.10f}"
            }),
            width="stretch"
        )
        

        col1, col2 = st.columns(2)
        if col1.button("📊 Prosseguir para análise"):
            st.session_state.page = "analysis"
            st.rerun()
        if col2.button("🔁 Nova simulação"):
            st.session_state.page = "setup"
            st.rerun()

# ---------- Página Analysis ----------
elif st.session_state.page == "analysis":
    df = st.session_state.df
    best_per_gen = st.session_state.best_per_gen
    avg_per_gen = st.session_state.avg_per_gen
    top5 = st.session_state.top5

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
        ax.plot(best_per_gen, label="Melhor por geração")
        ax.plot(avg_per_gen, label="Média por geração")
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
        st.subheader("Top 5 Globais (todas as gerações)")
        df_top5 = pd.DataFrame(top5, columns=["Cromossomo", "X", "Y", "Aptidao", "Geração"])
        df_top5["Aptidao"] = df_top5["Aptidao"].apply(truncar_6)
        df_top5["X"] = df_top5["X"].apply(truncar_6)
        df_top5["Y"] = df_top5["Y"].apply(truncar_6)
        st.dataframe(
            df_top5.style.format({
                "X": lambda v: f"{truncar_6(v):.6f}",
                "Y": lambda v: f"{truncar_6(v):.6f}",
                "Aptidao": lambda v: f"{truncar_6(v):.10f}"
            }),
            width="stretch"
        )

        st.subheader("Estatísticas da população (arquivo resultados_ag.csv)")
        st.write(df["aptidao"].describe())
        high = df[df["aptidao"] > df["aptidao"].mean() + df["aptidao"].std()]
        st.markdown(f"🔹 Indivíduos acima da média + 1 desvio padrão: **{len(high)}**")

    if st.button("🔁 Nova simulação"):
        st.session_state.page = "setup"
        st.rerun()
