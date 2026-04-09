import time
import os
import statistics
import duckdb
import polars as pl

CSV_PATH = "train_extra_radiussmote.csv"
REPEATS = 5

DUCK_OUT = "duckdb.parquet"
POLARS_OUT = "polars.parquet"


def run_duckdb_once():
    if os.path.exists(DUCK_OUT):
        os.remove(DUCK_OUT)

    start = time.perf_counter()
    with duckdb.connect() as con:
        con.execute("SET preserve_insertion_order = false;")
        con.execute(f"""
            COPY (
                SELECT * FROM read_csv_auto('{CSV_PATH}')
            ) TO '{DUCK_OUT}' (FORMAT PARQUET, COMPRESSION 'snappy')
        """)
    write_time = time.perf_counter() - start

    file_size = os.path.getsize(DUCK_OUT) / (1024 * 1024)

    start = time.perf_counter()
    with duckdb.connect() as con:
        con.execute(f"SELECT SUM(user_id) FROM read_parquet('{DUCK_OUT}')").fetchone()
    read_time = time.perf_counter() - start

    return write_time, read_time, file_size


def run_polars_once():
    if os.path.exists(POLARS_OUT):
        os.remove(POLARS_OUT)

    start = time.perf_counter()
    (
        pl.scan_csv(CSV_PATH)
        .sink_parquet(POLARS_OUT, compression="snappy", maintain_order=False)
    )
    write_time = time.perf_counter() - start

    file_size = os.path.getsize(POLARS_OUT) / (1024 * 1024)

    start = time.perf_counter()
    pl.scan_parquet(POLARS_OUT).select(pl.col("user_id").sum()).collect()
    read_time = time.perf_counter() - start

    return write_time, read_time, file_size


def benchmark_alternating():
    duck = {"write_times": [], "read_times": [], "file_sizes": []}
    polars = {"write_times": [], "read_times": [], "file_sizes": []}

    for i in range(REPEATS):
        duck_write, duck_read, duck_size = run_duckdb_once()
        duck["write_times"].append(duck_write)
        duck["read_times"].append(duck_read)
        duck["file_sizes"].append(duck_size)

        polars_write, polars_read, polars_size = run_polars_once()
        polars["write_times"].append(polars_write)
        polars["read_times"].append(polars_read)
        polars["file_sizes"].append(polars_size)

    return duck, polars


def avg(values):
    return statistics.mean(values)


def show_result(name, result):
    print(f"\n{name}")
    print(f"  Escrita: {', '.join(f'{x:.4f}s' for x in result['write_times'])}")
    print(f"  Leitura: {', '.join(f'{x:.4f}s' for x in result['read_times'])}")
    print(f"  Tamanho: {', '.join(f'{x:.2f} MB' for x in result['file_sizes'])}")

    print(f"  Média escrita: {avg(result['write_times']):.4f}s")
    print(f"  Média leitura: {avg(result['read_times']):.4f}s")
    print(f"  Média tamanho: {avg(result['file_sizes']):.2f} MB")


duck, polars = benchmark_alternating()

show_result("DuckDB", duck)
show_result("Polars", polars)
