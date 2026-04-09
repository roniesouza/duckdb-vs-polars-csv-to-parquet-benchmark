import time
import os
import statistics
import duckdb
import polars as pl

CSV_PATH = "train_extra_radiussmote.csv"
REPEATS = 5

DUCK_OUT = "duckdb.parquet"
POLARS_OUT = "polars.parquet"


def benchmark_duckdb():
    write_times = []
    read_times = []
    file_sizes = []

    for i in range(REPEATS):
        if os.path.exists(DUCK_OUT):
            os.remove(DUCK_OUT)

        start = time.perf_counter()
        with duckdb.connect() as con:
            con.execute(f"""
                COPY (
                    SELECT * FROM read_csv_auto('{CSV_PATH}')
                ) TO '{DUCK_OUT}' (FORMAT PARQUET, COMPRESSION 'snappy')
            """)
        write_times.append(time.perf_counter() - start)

        file_sizes.append(os.path.getsize(DUCK_OUT) / (1024 * 1024))

        start = time.perf_counter()
        with duckdb.connect() as con:
            con.execute(f"SELECT COUNT(*) FROM read_parquet('{DUCK_OUT}')").fetchone()
        read_times.append(time.perf_counter() - start)

    return {
        "write_times": write_times,
        "read_times": read_times,
        "file_sizes": file_sizes,
    }


def benchmark_polars():
    write_times = []
    read_times = []
    file_sizes = []

    for i in range(REPEATS):
        if os.path.exists(POLARS_OUT):
            os.remove(POLARS_OUT)

        start = time.perf_counter()
        df = pl.read_csv(CSV_PATH)
        df.write_parquet(POLARS_OUT, compression="snappy")
        write_times.append(time.perf_counter() - start)

        file_sizes.append(os.path.getsize(POLARS_OUT) / (1024 * 1024))

        start = time.perf_counter()
        pl.read_parquet(POLARS_OUT).height
        read_times.append(time.perf_counter() - start)

    return {
        "write_times": write_times,
        "read_times": read_times,
        "file_sizes": file_sizes,
    }


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


duck = benchmark_duckdb()
polars = benchmark_polars()

show_result("DuckDB", duck)
show_result("Polars", polars)