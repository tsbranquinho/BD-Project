from psycopg.rows import namedtuple_row
import os
from logging.config import dictConfig
import psycopg
from flask import Flask, jsonify, request
from psycopg.rows import namedtuple_row
# DATABASE_URL environment variable if it exists, otherwise use this.
 # Format postgres://username:password@hostname/database_name.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://bank:bank@postgres/bank")
pp.route("/", methods=("GET",))
@app.route("/accounts", methods=("GET",))
def account_index():
"""Show all the accounts, most recent first."""
with psycopg.connect(conninfo=DATABASE_URL) as conn:
    with conn.cursor(row_factory=namedtuple_row) as cur:
        accounts = cur.execute (
        """
        SELECT account_number, branch_name, balance
        FROM account
        ORDER BY account_number DESC;
        """,
        {},
        ).fetchall()
        log.debug(f"Found {cur.rowcount} rows.")
return jsonify(accounts)