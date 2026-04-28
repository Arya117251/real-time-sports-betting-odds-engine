"""Bulk-loads nba_games_raw.csv into BigQuery without DML (no billing required).
 
Deduplication is handled in pandas before upload. Table is overwritten each run
using WRITE_TRUNCATE — safe because the CSV is always the source of truth.
"""
 
import pathlib
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import Conflict
 
PROJECT_ID = "sports-odds-engine"
DATASET_ID = "nba_bronze"
TABLE_ID   = "raw_games"
CSV_PATH   = pathlib.Path(__file__).parent.parent / "data" / "nba_games_raw.csv"
 
SCHEMA = [
    bigquery.SchemaField("game_id",              "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("date",                 "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("home_team",            "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("away_team",            "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("home_score",           "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("away_score",           "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("status",               "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("home_wins",            "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("away_wins",            "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("home_losses",          "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("away_losses",          "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("season_home_win_pct",  "FLOAT",   mode="NULLABLE"),
    bigquery.SchemaField("season_away_win_pct",  "FLOAT",   mode="NULLABLE"),
    bigquery.SchemaField("home_rest_days",       "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("away_rest_days",       "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("home_is_back_to_back", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("away_is_back_to_back", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("score_diff",           "INTEGER", mode="NULLABLE"),
]
 
 
def get_client() -> bigquery.Client:
    """Return a BigQuery client using Application Default Credentials."""
    return bigquery.Client(project=PROJECT_ID)
 
 
def ensure_dataset(client: bigquery.Client) -> None:
    """Create the nba_bronze dataset if it does not already exist."""
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset_ref.location = "US"
    try:
        client.create_dataset(dataset_ref)
        print(f"Created dataset {PROJECT_ID}.{DATASET_ID}")
    except Conflict:
        print(f"Dataset {PROJECT_ID}.{DATASET_ID} already exists")
 
 
def ensure_table(client: bigquery.Client) -> None:
    """Create the raw_games table if it does not already exist."""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    table = bigquery.Table(table_ref, schema=SCHEMA)
    try:
        client.create_table(table)
        print(f"Created table {table_ref}")
    except Conflict:
        print(f"Table {table_ref} already exists")
 
 
def load_data(client: bigquery.Client) -> None:
    """Read CSV, deduplicate on game_id in pandas, then overwrite BigQuery table.
 
    Casts all columns to match the BigQuery schema explicitly to avoid
    pyarrow type conversion errors. Uses WRITE_TRUNCATE — no DML needed.
    """
    df = pd.read_csv(CSV_PATH)
 
    before = len(df)
    df = df.drop_duplicates(subset=["game_id"])
    after = len(df)
    print(f"Rows in CSV: {before} | After dedup: {after} | Dropped: {before - after}")
 
    # Cast columns to correct types
    df["date"] = df["date"].astype(str)
    int_cols = [
        "game_id", "home_score", "away_score", "home_wins", "away_wins",
        "home_losses", "away_losses", "home_rest_days", "away_rest_days",
        "home_is_back_to_back", "away_is_back_to_back", "score_diff"
    ]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
 
    float_cols = ["season_home_win_pct", "season_away_win_pct"]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
 
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
 
    load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    load_job.result()
 
    final = client.get_table(table_ref).num_rows
    print(f"✅ Loaded {final} rows into {table_ref}")
 
 
def main() -> None:
    """Orchestrate dataset/table creation and CSV load."""
    client = get_client()
    ensure_dataset(client)
    ensure_table(client)
    load_data(client)
 
 
if __name__ == "__main__":
    main()