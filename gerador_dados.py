import argparse
import logging
import sys
import time
from pathlib import Path

import duckdb

LOGGER = logging.getLogger("dataset")
DEFAULT_OUTPUT = Path("data/people.csv")
DEFAULT_ROWS = 340_000_000
CITIES = (
    (0, "Sao Paulo", "SP"),
    (1, "Rio de Janeiro", "RJ"),
    (2, "Belo Horizonte", "MG"),
    (3, "Curitiba", "PR"),
    (4, "Salvador", "BA"),
    (5, "Recife", "PE"),
    (6, "Fortaleza", "CE"),
    (7, "Porto Alegre", "RS"),
    (8, "Goiania", "GO"),
    (9, "Brasilia", "DF"),
)


def sql_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def generate_dataset(
    output: Path = DEFAULT_OUTPUT,
    rows: int = DEFAULT_ROWS,
    force: bool = False,
) -> bool:
    """Generate the CSV atomically and return whether a file was created."""
    if output.exists() and not force:
        size_bytes = output.stat().st_size
        LOGGER.info(
            "event=dataset_reused | path=%s | expected_rows=%d | "
            "size_bytes=%d | size_gib=%.2f",
            output,
            rows,
            size_bytes,
            size_bytes / 1024**3,
        )
        return False

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(f"{output.suffix}.tmp")
    temporary.unlink(missing_ok=True)
    cities = ",\n".join(
        f"({city_id}, '{city}', '{state}')" for city_id, city, state in CITIES
    )
    started_at = time.perf_counter()

    LOGGER.info(
        "event=dataset_generation_started | path=%s | temporary_path=%s | rows=%d",
        output,
        temporary,
        rows,
    )
    try:
        with duckdb.connect() as connection:
            connection.execute("SET preserve_insertion_order = false")
            connection.execute(
                f"""
                COPY (
                    WITH cities(city_id, city, state) AS (
                        VALUES {cities}
                    )
                    SELECT
                        user_id,
                        'pessoa' || user_id AS name,
                        'user' || user_id || '@email.com' AS email,
                        city,
                        state
                    FROM range(1, {rows + 1}) AS people(user_id)
                    JOIN cities
                        ON city_id = (user_id - 1) % {len(CITIES)}
                ) TO '{sql_path(temporary)}' (FORMAT CSV, HEADER)
                """
            )
        temporary.replace(output)
    except BaseException:
        elapsed = time.perf_counter() - started_at
        partial_bytes = temporary.stat().st_size if temporary.exists() else 0
        temporary.unlink(missing_ok=True)
        LOGGER.exception(
            "event=dataset_generation_failed | path=%s | rows=%d | "
            "partial_bytes=%d | "
            "elapsed_seconds=%.2f",
            output,
            rows,
            partial_bytes,
            elapsed,
        )
        raise

    elapsed = time.perf_counter() - started_at
    size_bytes = output.stat().st_size
    LOGGER.info(
        "event=dataset_generation_completed | path=%s | rows=%d | "
        "size_bytes=%d | "
        "size_gib=%.2f | elapsed_seconds=%.2f | rows_per_second=%.0f",
        output,
        rows,
        size_bytes,
        size_bytes / 1024**3,
        elapsed,
        rows / elapsed,
    )
    return True


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
        description="Gera o CSV do benchmark.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="quantidade de registros gerados",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="caminho do CSV criado ou reutilizado",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="substitui o CSV caso ele já exista",
    )
    args = parser.parse_args()

    if args.rows < 1:
        parser.error("--rows deve ser maior que zero")
    generate_dataset(args.output, args.rows, args.force)


if __name__ == "__main__":
    main()
