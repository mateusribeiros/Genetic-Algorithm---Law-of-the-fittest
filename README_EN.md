# 🧬 Genetic Algorithm — F6 Function

## 📘 Description
This project implements a **Genetic Algorithm (GA)** applied to the **F6 function**, aiming to find the values of **X** and **Y** that maximize fitness.  
The application was developed in **Python** and uses **Streamlit** to provide an interactive and intuitive visual interface.

---

## 🚀 Features
- Full execution of the **Genetic Algorithm** with customizable parameters:
  - Population size  
  - Number of generations  
  - Crossover rate  
  - Mutation rate  
- Display of the **best global individual** and the **Top 5 fittest**  
- Identification of the **parents of the best individual**  
- Automatic generation of a `.csv` file containing all individuals (replaced with each execution)  
- **Graphical analysis panel**:
  - Fitness evolution  
  - Fitness distribution  
  - X×Y dispersion  
  - Population statistics  

---

## 🧬 Biological Concept and Operation

The genetic algorithm is inspired by the **natural evolution of species**. Just like in biological systems, the solution evolves over time through selection, crossover, and mutation.

Each **individual** in the population represents a possible set of genes (chromosome), which in this project is a binary sequence divided into two parts — one representing **X** and the other **Y**. These values are converted into real numbers and evaluated through the **F6 function**, which defines the individual's fitness (how “well-adapted” it is to the environment).

During execution:
- **Population**: the set of individuals that coexist and compete for survival.  
- **Fitness**: measures the quality of each individual according to the F6 function.  
- **Roulette selection**: simulates evolutionary pressure — fitter individuals have a higher chance to reproduce, while less fit ones still have a small chance to contribute, ensuring genetic diversity.  
- **Crossover (genetic recombination)**: analogous to sexual reproduction, in which parts of the parents’ chromosomes are combined to form offspring with mixed traits. This allows the algorithm to explore new regions of the solution space.  
- **Mutation**: represents small random genetic changes. Although rare, they ensure variability and prevent population stagnation.  
- **Elitism**: the best individual from each generation is preserved so that advantageous traits are not lost.

The evolutionary cycle is repeated for several generations, allowing the population to progressively adapt. In the end, the algorithm identifies:
- The **fittest individual across all generations** (global best solution).  
- The **Top 5 fittest individuals** (highest-quality solutions).  
- The **parents of the best individual**, recording the genetic inheritance responsible for the optimal combination.

This process computationally reflects the biological principles of **natural selection**, **heredity**, and **genetic variation**, widely studied in evolutionary biology.

---

## ⚙️ Installation and Execution

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/algoritmo_AG.git
cd algoritmo_AG

2️⃣ (Optional) Create and activate a virtual environment
# On Windows
venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the application
streamlit run main.py

➡️ Your default browser will automatically open the GA interface.
```

---

### 🧩 Main Dependencies

random  
math  
pandas  
matplotlib  
plotly  
streamlit  

---

### 🧠 Notes

- The file `resultados_ag.csv` is replaced with each new execution.  
- The function `f6(x, y)` is a benchmark function used to evaluate optimization algorithms.  
- Graphs and results are displayed in the Streamlit interface after processing.  

---

### 🔖 License

This project is intended for **academic and educational purposes** and may be used for research and the study of Genetic Algorithms.
