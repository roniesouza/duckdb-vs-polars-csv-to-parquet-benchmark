# 🚀 Benchmark: CSV para Parquet com DuckDB  vs Polars

Este repositório compara **DuckDB** e **Polars** em um cenário simples e prático:
converter um CSV grande para Parquet e medir **tempo de escrita**, **tempo de leitura** e **tamanho final do arquivo**.

O objetivo é educacional. Não é um veredito geral sobre qual ferramenta é “melhor” em todos os casos.

## 🧾 Sobre o script

O script do benchmark já está no projeto, no arquivo `main.py`.
Por isso, ele não está duplicado neste README.

## 🗂️ Dataset

Dataset utilizado (Kaggle):
https://www.kaggle.com/datasets/anhtran10/lo-dataset

No teste deste projeto, o arquivo usado foi `train_extra_radiussmote.csv`.

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
| Média de escrita | **51.8635s** | 95.7238s |
| Média de leitura | **0.0395s** | 36.7030s |
| Média de tamanho | **1441.41 MB** | 1596.53 MB |

Considerando que **menor é melhor** para tempo e tamanho, neste dataset e nesta máquina o **DuckDB** foi **45.82% mais rápido** na escrita, **99.89% mais rápido** na leitura (aprox. **929x**) e gerou arquivo **9.72% menor**.

### 🦆 DuckDB

- Escrita: 48.7263s, 49.5103s, 47.0658s, 54.4691s, 59.5458s
- Leitura: 0.0499s, 0.0361s, 0.0336s, 0.0397s, 0.0382s
- Tamanho: 1441.22 MB, 1442.16 MB, 1441.22 MB, 1441.22 MB, 1441.22 MB
- Média escrita: 51.8635s
- Média leitura: 0.0395s
- Média tamanho: 1441.41 MB

### 🐻‍❄️ Polars

- Escrita: 50.4999s, 92.0701s, 91.9608s, 103.7149s, 140.3732s
- Leitura: 21.8974s, 29.3362s, 48.3157s, 37.5252s, 46.4402s
- Tamanho: 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB
- Média escrita: 95.7238s
- Média leitura: 36.7030s
- Média tamanho: 1596.53 MB

## 💻 Configuração da máquina de teste

 - Sistema operacional: Windows 11
 - CPU: Intel Core i5-1135G7 (4 núcleos / 8 threads)
 - RAM: 16 GB
 - Armazenamento: SSD NVMe

## 📚 Referências

- DuckDB: https://duckdb.org/
- Polars: https://pola.rs/
- uv (Astral): https://docs.astral.sh/uv/
- Dataset (Kaggle): https://www.kaggle.com/datasets/anhtran10/lo-dataset
