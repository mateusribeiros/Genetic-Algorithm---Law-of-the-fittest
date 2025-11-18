import math, random, pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
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
        acumulado = 
        
        for i, apt in enumerate(escala_aptidao):
            acumulado += apt
            if acumulado >= aleatorio:
                return populacao[i]
    return random.choice(populacao)

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
def algoritmo_genetico(pop_tamanho,num_ger,taxa_crossover,taxa_mutacao,num_elites=1):
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
    historico_populacao = []

    for geracao in range(1,num_ger):
        aptidoes = obter_aptidao(populacao)

        melhor_apt_local = max(aptidoes)
        melhor_ind_local = populacao[aptidoes.index(melhor_apt_local)]
        x, y = converter_bin_dec(melhor_ind_local)

        melhor_ind_por_ger.append([melhor_ind_local, x, y, melhor_apt_local, geracao])
        media_por_ger.append(sum(aptidoes) / len(aptidoes))
        
        # Divide a geração em 20 partes iguais, obtendo um valor N que será
        # responsável por registrar os valores da geração a cada N gerações
        if geracao % max(1, num_ger // 20) == 0 or geracao == 1:
            valores_x_y = [converter_bin_dec(ind) for ind in populacao]
            historico_populacao.append((geracao, valores_x_y, aptidoes[:]))

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

        populacao_com_apt = list(zip(populacao, aptidoes))
        populacao_com_apt.sort(key=lambda x: x[1], reverse=True)
        elites = [ind for ind, _ in populacao_com_apt[:num_elites]]
        
        # Muda os piores da geração pelos elites
        for i, elite in enumerate(elites):
            nova_populacao[i] = elite
        
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

    return melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger, melhores_pais, df, geracao_pais, top8, melhor_ind_por_ger, media_por_ger, historico_populacao

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
    
    num_elites = st.number_input(
        "Número de Elites", min_value=1, max_value=50, value=1
    )

    if st.button("🚀 Executar Algoritmo"):
        with st.spinner("Executando AG — isso pode levar alguns segundos/minutos..."):
            melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger, melhores_pais, df, geracao_pais, top8, melhor_ind_por_ger, media_por_ger, historico_populacao = algoritmo_genetico(
                tamanho_populacao, geracoes, taxa_crossover, taxa_mutacao, num_elites
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
            "historico_populacao": historico_populacao,
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

        st.title("Resultado do Algoritmo Genético")
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
        if col2.button("📊 Análises e Gráficos"):
            st.session_state.page = "analysis"
            st.rerun()

# ---------- Página Analysis ----------
elif st.session_state.page == "analysis":
    df = st.session_state.df
    media_por_ger = st.session_state.media_por_ger
    top8 = st.session_state.top8
    melhor_ind_por_ger = st.session_state.melhor_ind_por_ger
    historico_populacao = st.session_state.historico_populacao
    melhor_tupla = st.session_state.melhor_tupla

    st.title("Análises e Gráficos")
    st.markdown("""
    **Descrição das análises disponíveis**
    - **Evolução da Aptidão**: curva do melhor e da média por geração.
    - **Convergência**: quando o algoritmo encontrou a melhor solução.
    - **Mapa 3D**: visualização da superfície da função com o ponto ótimo (x, y e f6(x,y))
    - **Animação**: evolução da população no espaço com base em X e Y.
    - **Distribuição das Aptidões**: concentração dos indivíduos por aptidão.
    - **Dispersão**: mapa colorido pelas aptidões gerais.
    - **Estatísticas**: informações complementares.
    """)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📉 Evolução", "🎯 Convergência", "🗻 Mapa 3D", 
        "🎬 Animação", "📊 Distribuição", "🧭 Dispersão & Estatísticas"
    ])

    with tab1:
        st.subheader("Evolução da Aptidão por Geração")
        fig, ax = plt.subplots(figsize=(10, 6))
        aptidoes_por_ger = [ind[3] for ind in melhor_ind_por_ger]
        ax.plot(aptidoes_por_ger, marker='o', label="Melhor por geração", linewidth=2)
        ax.plot(media_por_ger, marker='s', label="Média por geração", linewidth=2)
        ax.set_title("Evolução da Aptidão", fontsize=14, fontweight='bold')
        ax.set_xlabel("Geração", fontsize=12)
        ax.set_ylabel("Aptidão", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        st.pyplot(fig)

    with tab2:
        st.subheader("Análise de Convergência")
        melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger = melhor_tupla
        aptidoes_por_ger = [ind[3] for ind in melhor_ind_por_ger]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Melhor Aptidão", f"{melhor_aptidao:.10f}")
        col2.metric("Geração do Melhor", melhor_ger)
        col3.metric("Convergência Estimada", f"Geração {melhor_ger}")
        
        # Calcula a precisão com base na distância do melhor indivíduo ao ótimo teórico
        otimo_teorico = gerar_f6(0, 0)
        distancia_otimo = abs(melhor_aptidao - otimo_teorico)
        precisao = (1 - distancia_otimo) * 100
        
        st.success(f"✅ **Precisão**: {precisao:.6f}%")
        
        # Gráfico de convergência
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(aptidoes_por_ger, marker='o', linewidth=2, color='green')
        ax.axhline(y=melhor_aptidao, color='r', linestyle='--', label=f'Melhor Global ({melhor_aptidao:.6f})')
        ax.axvline(x=melhor_ger-1, color='orange', linestyle='--', label=f'Geração {melhor_ger}')
        ax.set_title("Gráfico de Convergência", fontsize=14, fontweight='bold')
        ax.set_xlabel("Geração", fontsize=12)
        ax.set_ylabel("Melhor Aptidão", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        st.pyplot(fig)

    with tab3:
        st.subheader("Heatmap 3D")
        
        # Criar grid para o heatmap
        x_range = np.linspace(-100, 100, 100)
        y_range = np.linspace(-100, 100, 100)
        X, Y = np.meshgrid(x_range, y_range)
        Z = np.zeros_like(X)
        
        for i in range(len(x_range)):
            for j in range(len(y_range)):
                Z[j, i] = gerar_f6(X[j, i], Y[j, i])
        
        # Criar figura 3D
        fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
        
        # Adicionar ponto do melhor indivíduo
        melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger = melhor_tupla
        fig.add_trace(go.Scatter3d(
            x=[x_melhor], y=[y_melhor], z=[melhor_aptidao],
            mode='markers',
            marker=dict(size=10, color='red', symbol='diamond'),
            name=f'Melhor ({x_melhor:.2f}, {y_melhor:.2f})'
        ))
        
        fig.update_layout(
            title="Gráfico de Heatmap",
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='F6(X, Y)'
            ),
            width=800,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with tab4:
        st.subheader("Evolução da População")

        if len(historico_populacao) > 0:
            frames = []
            for geracao, coords, apts in historico_populacao:
                xs = [c[0] for c in coords]
                ys = [c[1] for c in coords]
                
                frames.append(go.Frame(
                    data=[go.Scatter(
                        x=xs, y=ys, mode='markers',
                        marker=dict(size=6, color=apts, colorscale='Viridis', 
                                  showscale=True, colorbar=dict(title="Aptidão")),
                        text=[f"Apt: {a:.6f}" for a in apts],
                        hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>%{text}<extra></extra>'
                    )],
                    name=f"Geração {geracao}"
                ))
            
            geracao_inicial, coords_inicial, apts_inicial = historico_populacao[0]
            xs_inicial = [c[0] for c in coords_inicial]
            ys_inicial = [c[1] for c in coords_inicial]
            
            fig = go.Figure(
                data=[go.Scatter(
                    x=xs_inicial, y=ys_inicial, mode='markers',
                    marker=dict(size=6, color=apts_inicial, colorscale='Viridis',
                              showscale=True, colorbar=dict(title="Aptidão")),
                    text=[f"Apt: {a:.6f}" for a in apts_inicial],
                    hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>%{text}<extra></extra>'
                )],
                frames=frames
            )
            
            fig.update_layout(
                title="Representação da Evolução",
                xaxis=dict(range=[-100, 100], title="X"),
                yaxis=dict(range=[-100, 100], title="Y"),
                updatemenus=[{
                    "buttons": [
                        {"args": [None, {"frame": {"duration": 500, "redraw": True},
                                        "fromcurrent": True}],
                         "label": "▶ Iniciar",
                         "method": "animate"},
                        {"args": [[None], {"frame": {"duration": 0, "redraw": True},
                                          "mode": "immediate"}],
                         "label": "⏸ Pausar",
                         "method": "animate"}
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }],
                sliders=[{
                    "active": 0,
                    "steps": [{"args": [[f.name], {"frame": {"duration": 0, "redraw": True},
                                                   "mode": "immediate"}],
                              "label": f.name,
                              "method": "animate"}
                             for f in frames],
                    "x": 0.1,
                    "len": 0.9,
                    "xanchor": "left",
                    "y": 0,
                    "yanchor": "top",
                    "pad": {"b": 10, "t": 50}
                }],
                width=800,
                height=600
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Histórico de população não disponível.")

    with tab5:
        st.subheader("Distribuição das Aptidões")
        fig = px.histogram(df, x="aptidao", nbins=30, title="Distribuição das Aptidões")
        fig.update_layout(xaxis_title="Aptidão", yaxis_title="Frequência")
        st.plotly_chart(fig, width='stretch')

    with tab6:
        st.subheader("Dispersão X×Y")
        fig = px.scatter(df, x="x", y="y", color="aptidao", title="Dispersão X×Y", 
                        color_continuous_scale="Viridis")
        fig.update_layout(xaxis_title="X", yaxis_title="Y")
        st.plotly_chart(fig,width='stretch')
        
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
    
    st.subheader("💾 Exportar Resultados")
    col1, col2 = st.columns(2)
    with col1:
        # Exportar CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Baixar CSV Completo",
            data=csv,
            file_name="resultados_ag_completo.csv",
            mime="text/csv"
        )
    with col2:
        # Exportar TXT
        melhor_individuo, x_melhor, y_melhor, melhor_aptidao, melhor_ger = melhor_tupla
        melhores_pais = st.session_state.pais
        geracao_pais = st.session_state.geracao_pais
        resumo = f"""RELATÓRIO DO ALGORITMO GENÉTICO - FUNÇÃO F6
        {'='*50}

        PARÂMETROS DA EXECUÇÃO:
        - População: {len(df[df['geracao']==1])} indivíduos
        - Gerações: {max(df['geracao'])}

        MELHOR SOLUÇÃO ENCONTRADA:
        - Cromossomo: {melhor_individuo}
        - X: {x_melhor:.6f}
        - Y: {y_melhor:.6f}
        - Aptidão: {melhor_aptidao:.10f}
        - Geração: {melhor_ger}
        - Pais: {melhores_pais[0]}, {melhores_pais[1]} (Geração {geracao_pais})

        PRECISÃO ALCANÇADA:
        {(1 - abs(melhor_aptidao - gerar_f6(0, 0))) * 100:.6f}%

        ESTATÍSTICAS DA POPULAÇÃO:
        {df['aptidao'].describe().to_string()}

        TOP 8 SOLUÇÕES:
        """
        for i, (crom, x, y, apt, ger) in enumerate(top8, 1):
            resumo += f"\n{i}. X={x:.6f}, Y={y:.6f}, Apt={apt:.10f}, Geração={ger}"
        
        st.download_button(
            label="Baixar Relatório (TXT)",
            data=resumo,
            file_name="relatorio_ag.txt",
            mime="text/plain"
        )
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        st.session_state.page = "results"
        st.rerun()
    if col2.button("🔁 Nova simulação"):
        st.session_state.page = "setup"
        st.rerun()
