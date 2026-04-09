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
| Média de escrita | 75.1811s | **70.9118s** |
| Média de leitura | **0.5891s** | 0.9952s |
| Média de tamanho | **1441.37 MB** | 1596.53 MB |

Considerando que **menor é melhor** para tempo e tamanho, nesta rodada o **Polars** foi **5.68% mais rápido na escrita**. Em contrapartida, o **DuckDB** foi **40.81% mais rápido na leitura** (aprox. **1.69x**) e gerou arquivo **9.72% menor**.
Na análise das execuções do Polars, a **primeira carga e a primeira leitura** ficaram acima das demais (`116.1837s` e `2.8842s`), enquanto as repetições seguintes ficaram em patamar menor, sugerindo um efeito inicial de aquecimento/estabilização do ambiente.

### 🦆 DuckDB

- Escrita: 76.4838s, 73.2865s, 71.0157s, 76.8969s, 78.2226s
- Leitura: 0.7973s, 0.5429s, 0.0750s, 1.3744s, 0.1556s
- Tamanho: 1441.22 MB, 1441.22 MB, 1441.22 MB, 1441.98 MB, 1441.22 MB
- Média escrita: 75.1811s
- Média leitura: 0.5891s
- Média tamanho: 1441.37 MB

### 🐻‍❄️ Polars

- Escrita: 116.1837s, 53.3307s, 77.4002s, 53.7433s, 53.9010s
- Leitura: 2.8842s, 1.3653s, 0.2100s, 0.2196s, 0.2967s
- Tamanho: 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB, 1596.53 MB
- Média escrita: 70.9118s
- Média leitura: 0.9952s
- Média tamanho: 1596.53 MB

## 🔭 Próximos passos

Atualmente, o benchmark mede primeiro todas as rodadas de um engine e depois do outro. Isso pode introduzir viés por **cache do sistema operacional**, estado do **SSD** e aquecimento do ambiente.

Para reduzir esse efeito, o ideal é alternar por repetição:
- DuckDB rodada 1 -> Polars rodada 1
- DuckDB rodada 2 -> Polars rodada 2
- DuckDB rodada 3 -> Polars rodada 3
- DuckDB rodada 4 -> Polars rodada 4
- DuckDB rodada 5 -> Polars rodada 5

Sem essa alternância, o segundo engine pode executar em condições diferentes da primeira etapa e influenciar a comparação.
 
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
