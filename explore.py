#!/usr/bin/env python3
"""
Usage:
    python explore.py config.share                           # list all tables
    python explore.py config.share share.schema.table        # columns + sample
    python explore.py config.share share.schema.table --limit 25
"""
import argparse
import delta_sharing


def list_tables(profile_path: str):
    client = delta_sharing.SharingClient(profile_path)
    tables = client.list_all_tables()
    if not tables:
        print("No tables found.")
        return
    print(f"\n{len(tables)} table(s) available:\n")
    for t in tables:
        print(f"  {t.share}.{t.schema}.{t.name}")
    print()


def inspect_table(profile_path: str, table_ref: str, limit: int):
    table_url = f"{profile_path}#{table_ref}"
    print(f"\nTable: {table_ref}\n")

    df = delta_sharing.load_as_pandas(table_url, limit=limit)

    pad = max(len(c) for c in df.columns) if len(df.columns) > 0 else 10
    print(f"Columns ({len(df.columns)}):\n")
    for col in df.columns:
        print(f"  {col:<{pad}}  {df[col].dtype}")

    print(f"\nSample ({len(df)} row(s)):\n")
    print(df.to_string(index=False))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Explore a Delta Share: list tables, inspect schema, fetch samples."
    )
    parser.add_argument("profile", help="Path to .share profile file")
    parser.add_argument(
        "table", nargs="?",
        help="Fully qualified table: share_name.schema_name.table_name",
    )
    parser.add_argument("--limit", type=int, default=10, help="Sample rows (default: 10)")
    args = parser.parse_args()

    if args.table:
        inspect_table(args.profile, args.table, args.limit)
    else:
        list_tables(args.profile)


if __name__ == "__main__":
    main()
