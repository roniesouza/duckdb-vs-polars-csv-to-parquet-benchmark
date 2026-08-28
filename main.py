import argparse
import logging
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

import duckdb
import polars as pl

from gerador_dados import DEFAULT_OUTPUT, DEFAULT_ROWS, generate_dataset, sql_path

LOGGER = logging.getLogger("benchmark")
DEFAULT_REPEATS = 4
DEFAULT_WARMUPS = 1
DUCKDB_OUTPUT = DEFAULT_OUTPUT.parent / "duckdb.parquet"
POLARS_OUTPUT = DEFAULT_OUTPUT.parent / "polars.parquet"

type Results = dict[str, list[float]]
type RunResult = tuple[float, float, float]
type Runner = Callable[[], RunResult]
type Summary = dict[str, tuple[float, float, float | None]]


def run_duckdb_once(csv_path: Path) -> RunResult:
    DUCKDB_OUTPUT.unlink(missing_ok=True)
    started_at = time.perf_counter()

    with duckdb.connect() as connection:
        connection.execute("SET preserve_insertion_order = false")
        connection.execute(
            f"""
            COPY (
                SELECT * FROM read_csv_auto('{sql_path(csv_path)}')
            ) TO '{sql_path(DUCKDB_OUTPUT)}'
            (FORMAT PARQUET, COMPRESSION SNAPPY)
            """
        )
    write_time = time.perf_counter() - started_at
    size_mib = DUCKDB_OUTPUT.stat().st_size / 1024**2
    started_at = time.perf_counter()

    with duckdb.connect() as connection:
        connection.execute(
            f"SELECT sum(user_id) FROM read_parquet('{sql_path(DUCKDB_OUTPUT)}')"
        ).fetchone()
    return write_time, time.perf_counter() - started_at, size_mib


def run_polars_once(csv_path: Path) -> RunResult:
    POLARS_OUTPUT.unlink(missing_ok=True)
    started_at = time.perf_counter()
    pl.scan_csv(csv_path).sink_parquet(
        POLARS_OUTPUT,
        compression="snappy",
        maintain_order=False,
    )
    write_time = time.perf_counter() - started_at
    size_mib = POLARS_OUTPUT.stat().st_size / 1024**2
    started_at = time.perf_counter()
    (pl.scan_parquet(POLARS_OUTPUT).select(pl.col("user_id").sum()).collect())
    return write_time, time.perf_counter() - started_at, size_mib


def empty_results() -> Results:
    return {"write_times": [], "read_times": [], "file_sizes": []}


def add_result(results: Results, values: RunResult) -> None:
    write_time, read_time, file_size = values
    results["write_times"].append(write_time)
    results["read_times"].append(read_time)
    results["file_sizes"].append(file_size)


def run_tool(
    name: str,
    runner: Runner,
    phase: str,
    iteration: int,
    total: int,
) -> RunResult:
    LOGGER.info(
        "event=tool_started | phase=%s | iteration=%d | total=%d | tool=%s",
        phase,
        iteration,
        total,
        name,
    )
    try:
        values = runner()
    except BaseException:
        LOGGER.exception(
            "event=tool_failed | phase=%s | iteration=%d | tool=%s",
            phase,
            iteration,
            name,
        )
        raise
    if phase == "warmup":
        LOGGER.info(
            "event=tool_completed | phase=%s | iteration=%d | tool=%s",
            phase,
            iteration,
            name,
        )
    else:
        LOGGER.info(
            "event=tool_completed | phase=%s | iteration=%d | tool=%s | "
            "write_seconds=%.4f | read_seconds=%.4f | size_mib=%.2f",
            phase,
            iteration,
            name,
            *values,
        )
    return values


def execution_order(index: int) -> tuple[str, str]:
    return ("DuckDB", "Polars") if index % 2 == 0 else ("Polars", "DuckDB")


def benchmark(
    csv_path: Path,
    repeats: int,
    warmups: int,
) -> tuple[Results, Results]:
    DUCKDB_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results = {"DuckDB": empty_results(), "Polars": empty_results()}
    runners: dict[str, Runner] = {
        "DuckDB": lambda: run_duckdb_once(csv_path),
        "Polars": lambda: run_polars_once(csv_path),
    }

    LOGGER.info(
        "event=benchmark_started | csv=%s | warmups=%d | repeats=%d",
        csv_path,
        warmups,
        repeats,
    )

    for index in range(warmups):
        warmup_number = index + 1
        order = execution_order(index)
        LOGGER.info(
            "event=warmup_started | iteration=%d | total=%d | order=%s",
            warmup_number,
            warmups,
            " -> ".join(order),
        )
        for name in order:
            run_tool(name, runners[name], "warmup", warmup_number, warmups)
        LOGGER.info(
            "event=warmup_completed | iteration=%d | total=%d",
            warmup_number,
            warmups,
        )

    for index in range(repeats):
        order = execution_order(index)
        round_number = index + 1
        LOGGER.info(
            "event=round_started | round=%d | total=%d | order=%s",
            round_number,
            repeats,
            " -> ".join(order),
        )
        for name in order:
            values = run_tool(
                name,
                runners[name],
                "measurement",
                round_number,
                repeats,
            )
            add_result(results[name], values)
        LOGGER.info(
            "event=round_completed | round=%d | total=%d",
            round_number,
            repeats,
        )

    LOGGER.info(
        "event=benchmark_completed | csv=%s | warmups=%d | repeats=%d",
        csv_path,
        warmups,
        repeats,
    )
    return results["DuckDB"], results["Polars"]


def summarize(values: list[float]) -> tuple[float, float, float | None]:
    deviation = statistics.stdev(values) if len(values) > 1 else None
    return statistics.mean(values), statistics.median(values), deviation


def log_result(name: str, result: Results) -> Summary:
    LOGGER.info(
        "event=tool_results | tool=%s | write_seconds=[%s] | "
        "read_seconds=[%s] | size_mib=[%s]",
        name,
        ", ".join(f"{value:.4f}" for value in result["write_times"]),
        ", ".join(f"{value:.4f}" for value in result["read_times"]),
        ", ".join(f"{value:.2f}" for value in result["file_sizes"]),
    )
    summary = {
        "write": summarize(result["write_times"]),
        "read": summarize(result["read_times"]),
        "size": summarize(result["file_sizes"]),
    }
    for metric, (mean, median, deviation) in summary.items():
        LOGGER.info(
            "event=metric_summary | tool=%s | metric=%s | mean=%.4f | "
            "median=%.4f | standard_deviation=%s",
            name,
            metric,
            mean,
            median,
            f"{deviation:.4f}" if deviation is not None else "n/a",
        )
    return summary


def comparison(duckdb_value: float, polars_value: float) -> str:
    if duckdb_value == polars_value:
        return "Empate"
    winner = "DuckDB" if duckdb_value < polars_value else "Polars"
    difference = abs(duckdb_value - polars_value) / max(
        duckdb_value,
        polars_value,
    )
    return f"{winner} ({difference:.2%} menor)"


def show_results(
    duckdb_result: Results,
    polars_result: Results,
    warmups: int,
) -> None:
    results = {"DuckDB": duckdb_result, "Polars": polars_result}
    summaries = {name: log_result(name, result) for name, result in results.items()}
    duckdb_write = summaries["DuckDB"]["write"][1]
    duckdb_read = summaries["DuckDB"]["read"][1]
    duckdb_size = summaries["DuckDB"]["size"][1]
    polars_write = summaries["Polars"]["write"][1]
    polars_read = summaries["Polars"]["read"][1]
    polars_size = summaries["Polars"]["size"][1]
    width = 74
    columns = "{:<14}{:<17}{:>14}{:>14}{:>15}"
    metrics = (
        ("write", "Escrita (s)"),
        ("read", "Leitura (s)"),
        ("size", "Parquet (MiB)"),
    )
    report = [
        "",
        "=" * width,
        "RESULTADO FINAL".center(width),
        "Menor valor indica melhor resultado".center(width),
        "-" * width,
        columns.format(
            "Ferramenta",
            "Métrica",
            "Média",
            "Mediana",
            "Desvio padrão",
        ),
        "-" * width,
    ]
    for name, summary in summaries.items():
        for index, (metric, label) in enumerate(metrics):
            mean, median, deviation = summary[metric]
            report.append(
                columns.format(
                    name if index == 0 else "",
                    label,
                    f"{mean:.4f}",
                    f"{median:.4f}",
                    f"{deviation:.4f}" if deviation is not None else "n/a",
                )
            )
    report.extend(
        [
            "-" * width,
            f"Aquecimentos não medidos: {warmups}",
            f"Rodadas medidas: {len(duckdb_result['write_times'])}",
            "Compressão: Snappy",
            "",
            "DESTAQUES PELA MEDIANA",
            f"  Escrita : {comparison(duckdb_write, polars_write)}",
            f"  Leitura : {comparison(duckdb_read, polars_read)}",
            f"  Tamanho : {comparison(duckdb_size, polars_size)}",
            "",
            "ARQUIVOS",
            f"  DuckDB  : {DUCKDB_OUTPUT}",
            f"  Polars  : {POLARS_OUTPUT}",
            "=" * width,
        ]
    )
    print("\n".join(report))


def configure_logging() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="Compara conversão e leitura de CSV com DuckDB e Polars.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV usado pelas duas ferramentas; é gerado quando não existe",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="registros gerados para um CSV novo ou regenerado",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help="rodadas incluídas nas estatísticas",
    )
    parser.add_argument(
        "--warmups",
        type=int,
        default=DEFAULT_WARMUPS,
        help="rodadas de aquecimento descartadas das estatísticas",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="substitui o CSV antes de executar o benchmark",
    )
    args = parser.parse_args()

    if args.rows < 1 or args.repeats < 1 or args.warmups < 0:
        parser.error(
            "--rows e --repeats devem ser maiores que zero; "
            "--warmups não pode ser negativo"
        )

    LOGGER.info(
        "event=run_configured | csv=%s | expected_rows=%d | warmups=%d | "
        "repeats=%d | regenerate=%s | duckdb_version=%s | "
        "polars_version=%s | duckdb_output=%s | polars_output=%s",
        args.csv,
        args.rows,
        args.warmups,
        args.repeats,
        args.regenerate,
        duckdb.__version__,
        pl.__version__,
        DUCKDB_OUTPUT,
        POLARS_OUTPUT,
    )
    generate_dataset(args.csv, args.rows, args.regenerate)
    duckdb_results, polars_results = benchmark(
        args.csv,
        args.repeats,
        args.warmups,
    )
    show_results(duckdb_results, polars_results, args.warmups)


if __name__ == "__main__":
    main()
