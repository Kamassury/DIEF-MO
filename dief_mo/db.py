"""SQLite persistence for DIEF-MO master data and generated assays."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .encoder import generate_id

DB_PATH = Path(__file__).resolve().parent.parent / "dief_mo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS areas (
    code TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT
);
CREATE TABLE IF NOT EXISTS matrices (
    code TEXT PRIMARY KEY, name TEXT NOT NULL, matrix_type TEXT
);
CREATE TABLE IF NOT EXISTS experiments (
    code TEXT PRIMARY KEY, name TEXT NOT NULL, activity_code TEXT
);
CREATE TABLE IF NOT EXISTS assays (
    dief_id TEXT PRIMARY KEY, experiment_code TEXT NOT NULL,
    area_code TEXT NOT NULL, matrix_code TEXT NOT NULL,
    seq INTEGER NOT NULL, created_at TEXT NOT NULL
);
"""

_MASTER_TABLES = {"areas", "matrices", "experiments"}
_ALLOWED_TABLES = _MASTER_TABLES | {"assays"}


@contextmanager
def get_conn(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.executescript(SCHEMA)


def add_area(code, name, description="", db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute("INSERT OR REPLACE INTO areas(code, name, description) VALUES (?, ?, ?)",
                     (code.strip(), name.strip(), (description or "").strip()))


def add_matrix(code, name, matrix_type="", db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute("INSERT OR REPLACE INTO matrices(code, name, matrix_type) VALUES (?, ?, ?)",
                     (code.strip(), name.strip(), (matrix_type or "").strip()))


def add_experiment(code, name, activity_code="", db_path=DB_PATH):
    with get_conn(db_path) as conn:
        conn.execute("INSERT OR REPLACE INTO experiments(code, name, activity_code) VALUES (?, ?, ?)",
                     (code.strip(), name.strip(), (activity_code or "").strip()))


def code_exists(table, code, db_path=DB_PATH):
    if table not in _MASTER_TABLES:
        raise ValueError(f"Tabela desconhecida: {table}")
    with get_conn(db_path) as conn:
        row = conn.execute(f"SELECT 1 FROM {table} WHERE code = ?", (code.strip(),)).fetchone()
    return row is not None


def delete_row(table, code, db_path=DB_PATH):
    if table not in _MASTER_TABLES:
        raise ValueError(f"Tabela desconhecida: {table}")
    with get_conn(db_path) as conn:
        conn.execute(f"DELETE FROM {table} WHERE code = ?", (code.strip(),))


def list_table(table, db_path=DB_PATH):
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"Tabela desconhecida: {table}")
    with get_conn(db_path) as conn:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY code").fetchall()
    return [dict(r) for r in rows]


def list_assays(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM assays ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def enriched_assays(db_path=DB_PATH):
    sql = """
        SELECT a.dief_id, a.experiment_code, e.name AS experiment_name,
               e.activity_code, a.area_code, ar.name AS area_name,
               a.matrix_code, m.name AS matrix_name, m.matrix_type,
               a.seq, a.created_at
        FROM assays a
        LEFT JOIN experiments e ON e.code = a.experiment_code
        LEFT JOIN areas ar ON ar.code = a.area_code
        LEFT JOIN matrices m ON m.code = a.matrix_code
        ORDER BY a.created_at DESC
    """
    with get_conn(db_path) as conn:
        rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def counts(db_path=DB_PATH):
    with get_conn(db_path) as conn:
        return {
            "areas": conn.execute("SELECT COUNT(*) FROM areas").fetchone()[0],
            "matrices": conn.execute("SELECT COUNT(*) FROM matrices").fetchone()[0],
            "experiments": conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0],
            "assays": conn.execute("SELECT COUNT(*) FROM assays").fetchone()[0],
        }


def _next_seq(conn, experiment, area, matrix):
    row = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 AS nxt FROM assays "
        "WHERE experiment_code = ? AND area_code = ? AND matrix_code = ?",
        (experiment, area, matrix)).fetchone()
    return row["nxt"]


def create_assay(experiment, area, matrix, db_path=DB_PATH):
    with get_conn(db_path) as conn:
        seq = _next_seq(conn, experiment, area, matrix)
        dief_id = generate_id(experiment, area, matrix, seq)
        conn.execute(
            "INSERT INTO assays(dief_id, experiment_code, area_code, matrix_code, seq, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (dief_id, experiment, area, matrix, seq, datetime.now(timezone.utc).isoformat()))
    return dief_id
