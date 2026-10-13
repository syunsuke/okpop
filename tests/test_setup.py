import importlib

import pytest

workflow_setup = importlib.import_module("okpop.workflows.setup")


def test_prepare_directories(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    db_dir = data_dir / "db"
    output_dir = data_dir / "output"

    monkeypatch.setattr(workflow_setup, "DATA_DIR", data_dir)
    monkeypatch.setattr(workflow_setup, "RAW_DIR", raw_dir)
    monkeypatch.setattr(workflow_setup, "DB_DIR", db_dir)
    monkeypatch.setattr(workflow_setup, "OUTPUT_DIR", output_dir)

    workflow_setup.prepare_directories()

    assert data_dir.is_dir()
    assert raw_dir.is_dir()
    assert db_dir.is_dir()
    assert output_dir.is_dir()

    for datatype in workflow_setup.DATA_TYPES:
        assert (raw_dir / datatype).is_dir()


def test_setup_skips_existing_database(tmp_path, monkeypatch):
    db_path = tmp_path / "population_osaka.sqlite"
    db_path.write_bytes(b"existing database")

    monkeypatch.setattr(workflow_setup, "DB_PATH", db_path)
    monkeypatch.setattr(
        workflow_setup,
        "prepare_directories",
        lambda: None,
    )
    monkeypatch.setattr(
        workflow_setup,
        "download_data",
        lambda: None,
    )

    def unexpected_build(*args, **kwargs):
        pytest.fail("build_database should not be called")

    monkeypatch.setattr(
        workflow_setup,
        "build_database",
        unexpected_build,
    )

    workflow_setup.setup()

    assert db_path.read_bytes() == b"existing database"


def test_setup_build_failure(tmp_path, monkeypatch):
    db_path = tmp_path / "population_osaka.sqlite"
    db_dir = tmp_path / "db"

    monkeypatch.setattr(workflow_setup, "DB_PATH", db_path)
    monkeypatch.setattr(workflow_setup, "DB_DIR", db_dir)
    monkeypatch.setattr(
        workflow_setup,
        "prepare_directories",
        lambda: None,
    )
    monkeypatch.setattr(
        workflow_setup,
        "download_data",
        lambda: None,
    )

    def failing_build(db_path):
        raise RuntimeError("Import failed")

    monkeypatch.setattr(
        workflow_setup,
        "build_database",
        failing_build,
    )

    with pytest.raises(RuntimeError, match="Import failed"):
        workflow_setup.setup()

    assert not db_path.exists()


def test_setup_cleans_temporary_database(tmp_path, monkeypatch):
    db_dir = tmp_path / "db"
    db_dir.mkdir()

    db_path = db_dir / "population_osaka.sqlite"
    temporary_path = db_dir / "population_osaka.building.sqlite"

    monkeypatch.setattr(workflow_setup, "DB_DIR", db_dir)
    monkeypatch.setattr(workflow_setup, "DB_PATH", db_path)
    monkeypatch.setattr(
        workflow_setup, "prepare_directories", lambda: None
    )
    monkeypatch.setattr(
        workflow_setup, "download_data", lambda: None
    )

    def failing_build(path):
        path.write_bytes(b"incomplete database")
        raise RuntimeError("Import failed")

    monkeypatch.setattr(
        workflow_setup, "build_database", failing_build
    )

    with pytest.raises(RuntimeError, match="Import failed"):
        workflow_setup.setup()

    assert not temporary_path.exists()
    assert not db_path.exists()

