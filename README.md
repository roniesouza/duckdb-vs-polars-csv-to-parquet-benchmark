# 🚀 Benchmark: CSV para Parquet com DuckDB  vs Polars

Este repositório compara **DuckDB** e **Polars** em um cenário simples e prático:
converter um CSV grande para Parquet e medir **tempo de escrita**, **tempo de leitura** e **tamanho final do arquivo**.

Existem diversos outros pontos que podem ser observados e testados (como uso de memória, CPU, filtros, agregações e diferentes estratégias de leitura/escrita), mas o foco deste benchmark foi exatamente esse recorte que executamos.
O objetivo é educacional e não representa um veredito geral sobre qual ferramenta é “melhor” em todos os casos.

## 🧾 Sobre o script

O benchmark está implementado no arquivo `main.py`.
Nele, as execuções já ocorrem de forma alternada por rodada (`DuckDB 1 -> Polars 1 -> DuckDB 2 -> Polars 2...`), reduzindo viés de comparação por ordem fixa.

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
| Média de escrita | **49.2535s** | 60.9733s |
| Média de leitura | **0.7057s** | 0.9280s |
| Média de tamanho | **1458.98 MB** | 1596.53 MB |

Considerando que **menor é melhor** para tempo e tamanho, nesta execução alternada o **DuckDB** foi **19.22% mais rápido na escrita** (aprox. **1.24x**), **23.95% mais rápido na leitura** (aprox. **1.31x**) e gerou arquivo **8.62% menor**.
Na escrita, o DuckDB ficou mais estável (de `47.7623s` a `50.6153s`), enquanto o Polars mostrou queda progressiva após a 1ª rodada (`71.2344s` para a faixa de `55-58s`), sugerindo efeito de aquecimento.
Na leitura, ambos tiveram picos isolados: DuckDB na **4ª leitura** (`1.7089s`) e Polars na **1ª leitura** (`3.2355s`), com as demais rodadas bem menores.
 
### 🦆 DuckDB

- Escrita: 47.7623s, 47.9389s, 49.4063s, 50.5447s, 50.6153s
- Leitura: 1.1611s, 0.4066s, 0.0852s, 1.7089s, 0.1668s
- Tamanho: 1458.89 MB, 1459.13 MB, 1459.28 MB, 1459.02 MB, 1458.57 MB
- Média escrita: 49.2535s
- Média leitura: 0.7057s
- Média tamanho: 1458.98 MB

### 🐻‍❄️ Polars

- Escrita: 71.2344s, 64.1465s, 56.0259s, 55.8336s, 57.6260s
- Leitura: 3.2355s, 0.3895s, 0.3446s, 0.2952s, 0.3754s
- Tamanho: 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB
- Média escrita: 60.9733s
- Média leitura: 0.9280s
- Média tamanho: 1596.53 MB

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
