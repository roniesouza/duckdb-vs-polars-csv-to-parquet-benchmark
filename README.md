# 🚀 Benchmark: CSV para Parquet com DuckDB  vs Polars

Este repositório compara **DuckDB** e **Polars** em um cenário simples e prático:
converter um CSV grande para Parquet e medir **tempo de escrita**, **tempo de leitura** e **tamanho final do arquivo**.

Existem diversos outros pontos que podem ser observados e testados (como uso de memória, CPU, filtros, agregações e diferentes estratégias de leitura/escrita), mas o foco deste benchmark foi exatamente esse recorte que executamos.
O objetivo é educacional e não representa um veredito geral sobre qual ferramenta é “melhor” em todos os casos.

## 🧾 Sobre o script

O benchmark está implementado no arquivo `main.py`.

## 🗂️ Dataset

Dataset utilizado (Kaggle):
https://www.kaggle.com/datasets/anhtran10/lo-dataset

No teste deste projeto, o arquivo usado foi `train_extra_radiussmote.csv`.

> ⚠️ **Tamanho do CSV utilizado: ~16,9 GB**  
> Esse volume é relevante para interpretar os resultados de performance deste benchmark.

## 🧰 Ferramentas utilizadas

### 🦆 DuckDB

O DuckDB é um banco analítico SQL embutido, muito forte para processar dados localmente com consultas SQL.

Mais indicado para:
- Exploração analítica rápida em arquivos grandes (CSV/Parquet)
- Pipelines locais de ETL/ELT com SQL
- Cenários em que você quer alta performance sem subir um servidor de banco

### 🐻‍❄️ Polars

O Polars é uma biblioteca de DataFrame colunar (com engine em Rust), focada em alta performance no ecossistema Python.

Mais indicado para:
- Transformações tabulares em pipelines Python
- Fluxos com DataFrames e operações vetorizadas
- Casos que se beneficiam de processamento eficiente e API moderna

### ⚡ uv (Astral)

O `uv` é o gerenciador de ambiente e dependências usado neste projeto.
Ele simplifica a reprodução do ambiente com rapidez e consistência.

## 🔢 Versões das bibliotecas (neste teste)

- 🦆 DuckDB: `1.5.1` (travado no `uv.lock`)
- 🐻‍❄️ Polars: `1.39.3` (travado no `uv.lock`)

## ✅ Requisitos

- Python 3.13 (arquivo `.python-version`)
- `uv` instalado

Instalação do `uv`:
https://docs.astral.sh/uv/

## 🔁 Como replicar com uv

1. Clone este repositório.
2. Baixe o dataset no Kaggle e coloque o CSV na raiz do projeto.
3. Garanta que o nome/caminho do CSV em `main.py` esteja correto na variável `CSV_PATH`.
4. Instale as dependências:

```bash
uv sync
```

5. Execute o benchmark:

```bash
uv run python main.py
```

Arquivos de saída esperados:
- `duckdb.parquet`
- `polars.parquet`

## 📏 O que o benchmark mede

- Tempo de escrita (CSV -> Parquet)
- Tempo de leitura (Parquet)
- Tamanho final do Parquet
- Média de 5 repetições

## 🏁 Resultados obtidos

### 📊 Resumo das médias

| Métrica | DuckDB 🦆 | Polars 🐻‍❄️ |
| --- | ---: | ---: |
| Média de escrita | 72.6091s | **65.2019s** |
| Média de leitura | **0.2495s** | 1.1116s |
| Média de tamanho | **1441.22 MB** | 1596.53 MB |

Considerando que **menor é melhor** para tempo e tamanho, nesta execução alternada o **Polars** foi **10.20% mais rápido na escrita**. Em contrapartida, o **DuckDB** foi **77.55% mais rápido na leitura** (aprox. **4.46x**) e gerou arquivo **9.73% menor**.
No Polars, a **primeira escrita** (`91.5338s`) e a **primeira leitura** (`1.2932s`) ficaram acima da maior parte das demais execuções; além disso, a **3ª leitura** teve um pico (`3.5508s`), indicando variabilidade entre rodadas.
 
### 🦆 DuckDB

- Escrita: 69.8735s, 69.0745s, 74.7388s, 73.0618s, 76.2969s
- Leitura: 0.1127s, 0.0929s, 0.0937s, 0.2156s, 0.7324s
- Tamanho: 1441.22 MB, 1441.22 MB, 1441.22 MB, 1441.22 MB, 1441.22 MB
- Média escrita: 72.6091s
- Média leitura: 0.2495s
- Média tamanho: 1441.22 MB

### 🐻‍❄️ Polars

- Escrita: 91.5338s, 59.0673s, 58.6942s, 61.3255s, 55.3888s
- Leitura: 1.2932s, 0.2215s, 3.5508s, 0.2335s, 0.2589s
- Tamanho: 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB
- Média escrita: 65.2019s
- Média leitura: 1.1116s
- Média tamanho: 1596.53 MB

## 🔭 Próximos passos

Com a versão atual do script, as rodadas já são executadas de forma alternada:
- DuckDB rodada 1 -> Polars rodada 1
- DuckDB rodada 2 -> Polars rodada 2
- DuckDB rodada 3 -> Polars rodada 3
- DuckDB rodada 4 -> Polars rodada 4
- DuckDB rodada 5 -> Polars rodada 5

Como refinamentos futuros, vale:
- randomizar a ordem por rodada (às vezes Polars primeiro);
- reportar desvio padrão junto com a média;
- separar cenários de leitura "cold" e "warm" para reduzir viés de cache.
 
## 💻 Configuração da máquina de teste

 - Sistema operacional: Windows 11
 - CPU: Intel Core i5-1135G7 (4 núcleos / 8 threads)
 - RAM: 16 GB
 - Armazenamento: SSD NVMe

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.  
Consulte o arquivo `LICENSE` para os detalhes.

> Observação: o dataset usado no benchmark (Kaggle) possui termos/licença próprios e independentes desta licença do código.

## 📚 Referências

- DuckDB: https://duckdb.org/
- Polars: https://pola.rs/
- uv (Astral): https://docs.astral.sh/uv/
- Dataset (Kaggle): https://www.kaggle.com/datasets/anhtran10/lo-dataset
