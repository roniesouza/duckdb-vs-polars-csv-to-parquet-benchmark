# Benchmark: CSV para Parquet com DuckDB e Polars

Este projeto compara DuckDB e Polars na conversão de um CSV grande para
Parquet. Ele mede o tempo de escrita, o tempo de leitura e o tamanho final do
arquivo, sem depender de datasets ou serviços externos.

O objetivo é educacional. O resultado representa este cenário específico e
não determina qual ferramenta é melhor para todo tipo de carga de trabalho.

## Dataset local

Na primeira execução, o projeto gera `data/people.csv` com 340 milhões de
registros sintéticos. O arquivo deve ficar próximo de 20 GB, mas o tamanho pode
variar. As execuções seguintes reutilizam esse arquivo.

Cada registro tem as colunas `user_id`, `name`, `email`, `city` e `state`. A
geração é feita pelo DuckDB antes do cronômetro do benchmark e grava primeiro
em um arquivo temporário, evitando que uma geração interrompida seja tomada
como completa.

O volume exige espaço para o CSV e para os dois arquivos Parquet. Verifique o
espaço livre antes de executar o benchmark completo.

## Requisitos

- Python 3.13, conforme `.python-version`;
- [uv](https://docs.astral.sh/uv/);
- espaço em disco compatível com o dataset e os arquivos de saída.

## Execução

Instale o ambiente e execute:

```bash
uv sync
uv run python main.py
```

Na primeira vez, o comando gera o dataset, executa uma rodada de aquecimento
fora das estatísticas e depois inicia quatro rodadas medidas. Ao final,
permanecem disponíveis:

- `data/people.csv`;
- `data/duckdb.parquet`;
- `data/polars.parquet`.

Para descartar o CSV existente e criá-lo novamente:

```bash
uv run python main.py --regenerate
```

Também é possível gerar somente o dataset:

```bash
uv run python gerador_dados.py
```

## Parâmetros de execução

Todos os parâmetros são opcionais. Consulte a ajuda diretamente no terminal:

```bash
uv run python main.py --help
uv run python gerador_dados.py --help
```

### `main.py`

| Parâmetro | Padrão | Descrição |
| --- | --- | --- |
| `--csv CAMINHO` | `data/people.csv` | CSV usado pelas duas ferramentas. Se não existir, será gerado. |
| `--rows N` | `340000000` | Registros criados quando o CSV não existe ou quando `--regenerate` é usado. Não limita um CSV existente. |
| `--repeats N` | `4` | Rodadas medidas. Em cada rodada, DuckDB e Polars são executados uma vez. |
| `--warmups N` | `1` | Rodadas de aquecimento descartadas das estatísticas. Use `0` para desativar. |
| `--regenerate` | desativado | Substitui o CSV indicado por `--csv` antes do benchmark. |

Para executar somente uma rodada usando o dataset padrão existente:

```bash
uv run python main.py --repeats 1
```

Se `data/people.csv` ainda não existir, esse comando gera os 340 milhões de
registros antes do aquecimento e da rodada medida. Alterar `--repeats` ou
`--warmups` não altera o tamanho do dataset.

Quatro rodadas medidas mantêm o tempo total razoável e equilibram a ordem: cada
ferramenta inicia duas vezes. Para uma análise mais longa, aumente
`--repeats`; prefira sempre um número par.

### `gerador_dados.py`

| Parâmetro | Padrão | Descrição |
| --- | --- | --- |
| `--output CAMINHO` | `data/people.csv` | Caminho do CSV que será criado ou reutilizado. |
| `--rows N` | `340000000` | Quantidade de registros gerados. |
| `--force` | desativado | Substitui o CSV caso ele já exista. |

Esse script apenas gera ou reutiliza o CSV; ele não executa o benchmark.

## Teste com volume reduzido

Para validar o ambiente sem criar o arquivo completo, use outro caminho. O
argumento `--rows` só é considerado quando o CSV precisa ser gerado.

```bash
uv run python main.py --csv data/smoke.csv --rows 100000 --repeats 1 --regenerate
```

Se o caminho informado já existir, ele será reutilizado. Use `--regenerate`
para substituí-lo com a quantidade de registros solicitada.

## Observabilidade

Os dois scripts emitem logs com data, nível, componente e eventos estáveis no
formato `event=...`, acompanhados por campos em pares chave/valor. A geração
registra início, reutilização, conclusão ou falha, além de caminho, registros,
tamanho, duração e throughput. O benchmark registra configuração e versões,
ordem das rodadas, início e fim de cada ferramenta, métricas, resumo e falhas.

Não há logs por registro, e os logs de cada ferramenta ficam fora das janelas
cronometradas para não interferirem nas métricas.

Ao final, `main.py` apresenta um relatório separado dos logs, com média,
mediana, desvio padrão amostral, destaque pela mediana, diferença percentual,
quantidade de aquecimentos e rodadas, além dos caminhos dos Parquets. Com uma
única rodada medida, o desvio padrão aparece como `n/a`. A saída usa UTF-8 para
preservar acentos no terminal do Windows.

## Metodologia

Antes das medições, cada ferramenta executa uma vez para aquecer inicialização,
alocadores e cache. O início e a conclusão são observáveis nos logs, mas seus
tempos não aparecem no relatório nem entram nas estatísticas.

Cada rodada medida converte o mesmo CSV para Parquet com compressão Snappy. Em
seguida, cada ferramenta lê seu próprio Parquet e calcula a soma de `user_id`,
forçando uma operação sobre os dados. A ordem de início é invertida a cada
rodada: `DuckDB -> Polars` e depois `Polars -> DuckDB`.

A geração do CSV e o aquecimento não entram nas métricas. O benchmark apresenta
os valores de cada rodada, média, mediana e desvio padrão amostral de:

- tempo de escrita de CSV para Parquet;
- tempo de leitura e agregação do Parquet;
- tamanho do Parquet em MiB.

Feche aplicações que disputem CPU, memória ou disco e use a mesma máquina e as
mesmas versões ao comparar resultados. Cache do sistema operacional,
temperatura, processos em segundo plano e características do hardware podem
afetar as medições.

## Tecnologias

- [DuckDB](https://duckdb.org/): banco analítico SQL embutido;
- [Polars](https://pola.rs/): biblioteca de DataFrame colunar;
- [uv](https://docs.astral.sh/uv/): ambiente e dependências reproduzíveis.

As versões resolvidas estão registradas em `uv.lock`.

## Licença

Este projeto está licenciado sob a MIT License. Consulte `LICENSE`.
