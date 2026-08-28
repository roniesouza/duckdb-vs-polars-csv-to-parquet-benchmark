# AGENTS.md

## Contexto do projeto

Este repositório mede a conversão de um CSV sintético para Parquet com DuckDB e
Polars. O benchmark cobre tempo de escrita, tempo de leitura com agregação e
tamanho final. Ele é educacional e não deve ser apresentado como uma conclusão
geral sobre as ferramentas.

O dataset padrão tem 340 milhões de registros e fica próximo de 20 GB. Ele deve
ser gerado localmente apenas quando `data/people.csv` não existir. A geração não
faz parte do tempo medido e o projeto não pode depender de datasets externos.

## Ambiente e comandos

- Use Python 3.13, definido em `.python-version`.
- Use exclusivamente `uv` para ambiente, dependências e execução.
- Instale ou sincronize com `uv sync`.
- Execute o benchmark completo com `uv run python main.py`.
- Valide alterações com um dataset pequeno e caminho separado:
  `uv run python main.py --csv data/smoke.csv --rows 100000 --repeats 1 --regenerate`.
- Não gere o dataset completo em testes automatizados.

## Regras de implementação

- Siga a PEP 8 e mantenha nomes, imports e linhas legíveis.
- Prefira o código mais compacto e simples possível, sem abstrações prematuras.
- Use a biblioteca padrão antes de adicionar dependências.
- Use `pathlib.Path` para caminhos e type hints nas funções.
- Mantenha o CSV e os dois arquivos Parquet gerados dentro de `data/`.
- Mantenha geração, escrita e leitura em etapas claramente separadas.
- Garanta observabilidade com logs claros tanto em `gerador_dados.py` quanto em
  `main.py`; use o módulo `logging` da biblioteca padrão para eventos
  operacionais.
- Reserve `stdout` e `print` para o relatório final legível pelo usuário; não
  misture mensagens de diagnóstico nessa saída.
- Na geração, registre início, reutilização, conclusão e falha, incluindo
  caminho, quantidade de registros, tamanho, duração e throughput.
- No benchmark, registre configuração, início e fim de cada rodada e ferramenta,
  tempos, tamanhos, resumo e falhas. Não gere logs por registro, pois isso
  prejudica a performance e polui a saída.
- Execute uma rodada de aquecimento por padrão e nunca inclua seus valores nas
  estatísticas do benchmark.
- Use quatro rodadas medidas por padrão e preserve um número par para equilibrar
  qual ferramenta inicia cada rodada.
- Apresente média, mediana e desvio padrão amostral; quando houver uma única
  medição, mostre o desvio padrão como indisponível.
- Não inclua a geração do dataset nas métricas do benchmark.
- Preserve o mesmo CSV, compressão Snappy e agregação de `user_id` para as duas
  ferramentas, garantindo uma comparação equivalente.
- Alterne qual ferramenta inicia cada rodada para reduzir viés de ordem.
- Atualize o README quando comandos, saídas ou metodologia mudarem.
- Nunca versione CSVs, Parquets, arquivos temporários ou outros dados gerados.
- Ao publicar resultados, registre sistema operacional, CPU, RAM,
  armazenamento, versões e parâmetros usados. A execução histórica foi feita
  no Windows 11, Intel Core i5-1135G7 (4 núcleos/8 threads), 16 GB de RAM e SSD
  NVMe; não reutilize seus números para o novo dataset.

## Git

Siga Conventional Commits em todos os commits. Mantenha os tipos e escopos
convencionais, mas escreva sempre a descrição em português. Use mensagens
curtas no formato `tipo(escopo): descrição`, por exemplo:

- `feat(dataset): gerar dados sintéticos localmente`
- `perf(benchmark): reduzir cópias durante a conversão`
- `docs(readme): documentar execução com uv`

Tipos comuns: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build` e
`chore`. Separe mudanças independentes em commits independentes.
