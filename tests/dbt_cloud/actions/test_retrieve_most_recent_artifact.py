import json
from pathlib import Path
from unittest.mock import patch

import responses
from pytest import fixture
from typer.testing import CliRunner

from dbttoolkit.dbt_cloud.actions import retrieve_most_recent_artifact
from dbttoolkit.dbt_cloud.actions.retrieve_most_recent_artifact import typer_app

runner = CliRunner()


def test_cli_has_mandatory_fields():
    result = runner.invoke(typer_app, ["manifest"])
    assert result.exit_code != 0
    assert "Missing option" in result.stdout


@responses.activate
def test_cli_execution(dbt_cloud_ids_cli, rest_api_run_result, manifest_json, job_id, account_id):
    path = Path("/tmp/")

    responses.add(
        responses.GET,
        f"https://cloud.getdbt.com/api/v2/accounts/{account_id}/runs",
        json=rest_api_run_result,
        status=200,
    )

    # Should pick job_id = 1 because it's the successful one, even if it's not the most recent
    responses.add(
        responses.GET,
        f"https://cloud.getdbt.com/api/v2/accounts/{account_id}/runs/1/artifacts/manifest.json",
        json=manifest_json,
        status=200,
    )

    with patch.object(retrieve_most_recent_artifact, "write_to_file", autospec=True) as mock:
        result = runner.invoke(typer_app, ["manifest", "--output-folder", path, "--job-id", job_id, *dbt_cloud_ids_cli])

        assert result.exit_code == 0

        assert mock.call_count == 1
        assert mock.call_args[0] == (json.dumps(manifest_json, indent=2), path, "manifest.json")


@fixture
def job_id():
    return 999


@fixture
def rest_api_run_result(job_id, dbt_cloud_ids):
    common = {**dbt_cloud_ids, "job_id": job_id, "finished_at_humanized": "1 hour ago", "git_sha": "abc123"}

    failure = {
        "id": 2,
        "is_complete": True,
        "is_success": False,
        "is_cancelled": False,
        "created_at": "2022-06-10 11:30:00.321339+00:00",
        **common,
    }

    cancelled = {
        "id": 3,
        "is_complete": True,
        "is_success": False,
        "is_cancelled": True,
        "created_at": "2022-06-10 11:30:00.321339+00:00",
        **common,
    }

    success = {
        "id": 1,
        "is_complete": True,
        "is_success": True,
        "is_cancelled": False,
        "created_at": "2022-06-09 11:30:00.321339+00:00",
        **common,
    }

    return {"data": [failure, cancelled, success]}


@fixture
def manifest_json():
    return {"manifest": "mock"}
