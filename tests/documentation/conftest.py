from pathlib import Path

import pytest

CURRENT_FOLDER = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def dbt_sample_project_path():
    return (CURRENT_FOLDER / "../_fixtures/dbt_sample_project").resolve()
