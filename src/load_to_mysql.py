from __future__ import annotations

from sqlalchemy import create_engine, text

from src.config import DATA_PATH, MYSQL_URL
from src.data_loader import load_csv, standardize_columns


def main() -> None:
    """Load the raw dataset into MySQL for SQL-based exploration."""
    if not MYSQL_URL:
        raise ValueError("Set MYSQL_URL in .env before loading data into MySQL.")

    df = standardize_columns(load_csv(DATA_PATH))
    engine = create_engine(MYSQL_URL)

    df.to_sql(
        "energy_data",
        con=engine,
        if_exists="replace",
        index=False,
    )

    with engine.connect() as connection:
        count = connection.execute(text("SELECT COUNT(*) FROM energy_data")).scalar_one()

    print(f"Loaded {count:,} rows into MySQL table 'energy_data'.")


if __name__ == "__main__":
    main()
