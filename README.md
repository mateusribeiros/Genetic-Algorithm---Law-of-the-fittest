# 🧬 Algoritmo Genético — Função F6

[🇬🇧 **Read in English**](./README_EN.md)

## 📘 Descrição
Este projeto implementa um **Algoritmo Genético (AG)** aplicado à **função F6**, com o objetivo de encontrar os valores de **X** e **Y** que maximizam sua aptidão.  
A aplicação foi desenvolvida em **Python** e utiliza **Streamlit** para fornecer uma interface visual interativa e intuitiva.

---

## 🚀 Funcionalidades
- Execução completa do **Algoritmo Genético** com parâmetros personalizáveis:
  - Tamanho da população  
  - Número de gerações  
  - Taxa de crossover  
  - Taxa de mutação  
- Exibição do **melhor indivíduo global** e dos **Top 5 mais aptos**  
- Identificação dos **pais do melhor indivíduo**  
- Geração automática de arquivo `.csv` com todos os indivíduos (substituído a cada execução)  
- Painel de **análises gráficas**:
  - Evolução da aptidão  
  - Distribuição das aptidões  
  - Dispersão X×Y  
  - Estatísticas populacionais  

---

## 🧬 Conceito Biológico e Funcionamento

O algoritmo genético é inspirado na **evolução natural das espécies**. Assim como em sistemas biológicos, a solução evolui ao longo do tempo por meio de seleção, cruzamento e mutação.

Cada **indivíduo** da população representa um possível conjunto de genes (cromossomo), que neste projeto é uma sequência binária dividida em duas partes — uma representando **X** e outra **Y**. Esses valores são convertidos em números reais e avaliados através da **função F6**, que define a aptidão do indivíduo (quão "ajustado" ele está ao ambiente).

Durante a execução:
- **População**: conjunto de indivíduos que coexistem e competem por sobrevivência.  
- **Aptidão (fitness)**: mede a qualidade de cada indivíduo segundo a função F6.  
- **Seleção por roleta**: simula a pressão evolutiva, onde indivíduos mais aptos têm mais chances de se reproduzir, mas os menos aptos ainda possuem pequenas chances de contribuir, garantindo diversidade genética.  
- **Crossover (recombinação genética)**: processo análogo à reprodução sexuada, no qual partes dos cromossomos dos pais são combinadas para formar descendentes com características mistas. Isso permite explorar novas regiões do espaço de soluções.  
- **Mutação**: representa pequenas alterações genéticas aleatórias. Apesar de raras, elas garantem variabilidade e evitam a estagnação populacional.  
- **Elitismo**: o melhor indivíduo de cada geração é preservado para que as boas características não sejam perdidas.

O ciclo evolutivo é repetido por várias gerações, permitindo que a população se adapte progressivamente. Ao final, são identificados:
- O **indivíduo mais apto de todas as gerações** (melhor solução global).  
- O **Top 5 mais aptos** (soluções de maior qualidade).  
- Os **pais do melhor indivíduo**, registrando a herança genética responsável pela melhor combinação.

O processo reflete, em termos computacionais, os princípios de **seleção natural**, **hereditariedade** e **variação genética**, amplamente estudados na biologia evolutiva.

---

## ⚙️ Instalação e Execução

### 1️⃣ Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/algoritmo_AG.git
cd algoritmo_AG

2️⃣ (Opcional) Crie e ative um ambiente virtual

python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/macOS
source venv/bin/activate

3️⃣ Instale as dependências

pip install -r requirements.txt

4️⃣ Execute a aplicação

streamlit run main.py

➡️ O navegador abrirá automaticamente o painel do AG.
```

### 🧩 Dependências Principais

random
math
pandas
matplotlib
plotly
streamlit

### 🧠 Observações

- O arquivo resultados_ag.csv é substituído a cada nova execução.
- A função f6(x, y) é uma função de benchmark usada para avaliar o desempenho de algoritmos de otimização.
- Os gráficos e resultados são exibidos na interface Streamlit após o processamento.

### 🔖 Licença

Este projeto é de uso acadêmico e educacional, podendo ser utilizado para fins de pesquisa e estudo de Algoritmos Genéticos.