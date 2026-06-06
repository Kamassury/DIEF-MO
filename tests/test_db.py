import os
import sqlite3
import tempfile

import pytest

from dief_mo import db


@pytest.fixture
def temp_db():
    path = os.path.join(tempfile.mkdtemp(), "t.db")
    db.init_db(path)
    return path


def _seed(path):
    db.add_area("PRO", "Proteomics", db_path=path)
    db.add_matrix("M001", "E. coli", "Bacterial culture", db_path=path)
    db.add_experiment("E001", "Pilot", "EXP", db_path=path)
    db.add_batch("B001", "E001", "First batch", db_path=path)
    db.add_sample("S001", "B001", "M001", "Sample 1", db_path=path)


def test_generate_from_sample_derives_lineage(temp_db):
    _seed(temp_db)
    dief_id = db.create_assay_from_sample("S001", "PRO", db_path=temp_db)
    assert dief_id == "E001_PRO_M001_001"
    info = db.get_lineage(dief_id, db_path=temp_db)
    assert info["sample_code"] == "S001"
    assert info["batch_code"] == "B001"
    assert info["experiment_code"] == "E001"
    assert info["matrix_code"] == "M001"


def test_batch_requires_existing_experiment(temp_db):
    with pytest.raises(ValueError):
        db.add_batch("B999", "E_NOPE", "x", db_path=temp_db)


def test_sample_requires_existing_batch_and_matrix(temp_db):
    db.add_experiment("E001", "Pilot", "EXP", db_path=temp_db)
    db.add_batch("B001", "E001", "b", db_path=temp_db)
    with pytest.raises(ValueError):
        db.add_sample("S999", "B001", "M_NOPE", "x", db_path=temp_db)


def test_quality_report_flags_gaps(temp_db):
    _seed(temp_db)  # sample S001 has no assay yet
    rep = db.quality_report(db_path=temp_db)
    assert "S001" in rep["samples_without_assays"]
    db.create_assay_from_sample("S001", "PRO", db_path=temp_db)
    rep2 = db.quality_report(db_path=temp_db)
    assert "S001" not in rep2["samples_without_assays"]
    assert rep2["sample_coverage"] == 1.0


def test_migration_adds_sample_code_to_old_db():
    # Build an OLD-style assays table without sample_code, then migrate.
    path = os.path.join(tempfile.mkdtemp(), "old.db")
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE assays (dief_id TEXT PRIMARY KEY, experiment_code TEXT, "
        "area_code TEXT, matrix_code TEXT, seq INTEGER, created_at TEXT)")
    con.execute("INSERT INTO assays VALUES ('E001_PRO_M001_001','E001','PRO','M001',1,'t')")
    con.commit()
    con.close()
    db.init_db(path)  # should add the missing column without losing data
    # enriched_assays must work and keep the old row, now with a null sample_code
    rows = db.enriched_assays(path)
    assert any(r["dief_id"] == "E001_PRO_M001_001" for r in rows)
    assert rows[0]["sample_code"] is None