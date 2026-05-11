import json
import math
import os
import tempfile

import delta_sharing
import pandas as pd

from fivetran_connector_sdk import Connector, Logging as log, Operations as op

TABLES = {
    "customer": "c_id",
    "district": "d_id",
}


def schema(configuration: dict):
    return [
        {"table": table_name, "primary_key": [pk]}
        for table_name, pk in TABLES.items()
    ]


def _build_profile(bearer_token: str, endpoint: str) -> dict:
    return {
        "shareCredentialsVersion": 1,
        "endpoint": endpoint,
        "bearerToken": bearer_token,
        "expirationTime": "9999-12-31T00:00:00.000Z",
    }


def _serialize_value(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if value is pd.NA:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def update(configuration: dict, state: dict):
    bearer_token = configuration.get("bearer_token", "")
    endpoint = configuration.get("endpoint", "")
    share_name = configuration.get("share_name", "")
    schema_name = configuration.get("schema_name", "")

    if not bearer_token:
        raise ValueError("Missing required config: bearer_token")
    if not endpoint:
        raise ValueError("Missing required config: endpoint")
    if not share_name:
        raise ValueError("Missing required config: share_name")
    if not schema_name:
        raise ValueError("Missing required config: schema_name")

    profile = _build_profile(bearer_token, endpoint)

    fd, profile_path = tempfile.mkstemp(suffix=".share", prefix="fivetran_delta_")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(profile, fh)

        for table_name in TABLES:
            table_url = f"{profile_path}#{share_name}.{schema_name}.{table_name}"
            log.info(f"Loading '{table_name}' from Delta Share.")

            try:
                df = delta_sharing.load_as_pandas(table_url)
            except Exception as exc:
                log.severe(f"Failed to load '{table_name}': {exc}")
                raise

            row_count = len(df)
            log.info(f"'{table_name}': {row_count} rows fetched.")

            for i, record in enumerate(df.to_dict(orient="records")):
                op.upsert(table_name, {k: _serialize_value(v) for k, v in record.items()})
                if (i + 1) % 10_000 == 0:
                    log.info(f"'{table_name}': upserted {i + 1}/{row_count} rows.")

            log.info(f"'{table_name}': done.")

        op.checkpoint(state={})
        log.info("All tables synced.")

    finally:
        try:
            os.remove(profile_path)
        except OSError as exc:
            log.warning(f"Could not remove temp profile '{profile_path}': {exc}")


connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    with open("configuration.json", "r") as f:
        configuration = json.load(f)
    connector.debug(configuration=configuration)
