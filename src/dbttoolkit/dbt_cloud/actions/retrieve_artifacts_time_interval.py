"""
https://docs.getdbt.com/dbt-cloud/api#section/How-to-use-this-API

curl --request GET \
  --url https://cloud.getdbt.com/api/v2/accounts/ \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token <your token>'
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import requests
import typer

from dbttoolkit.dbt_cloud.actions._docs import HELP
from dbttoolkit.dbt_cloud.clients.dbt_cloud_client import DbtCloudClient
from dbttoolkit.dbt_cloud.models.dbt_artifact import DbtArtifact
from dbttoolkit.utils.io import persist
from dbttoolkit.utils.logger import get_logger

typer_app = typer.Typer()
logger = get_logger()

RELEVANT_ARTIFACTS = [DbtArtifact.sources, DbtArtifact.run_results, DbtArtifact.manifest]


def _process_run(client: DbtCloudClient, run: Mapping, output_folder: Path, bucket_name: str = None) -> None:
    """
    Processes an individual run, by writing a run metadata file and looping through the run steps
    """
    logger.info(f'Processing run {run["id"]} from {run["finished_at_humanized"]} ago')

    finished_at = datetime.fromisoformat(run["finished_at"])

    folder_path = Path(
        output_folder,
        "date={}".format(finished_at.date().isoformat()),
        "hour={}".format(finished_at.strftime("%H")),
        "job_id={}".format(run["job_id"]),
        "run_id={}".format(run["id"]),
    )

    persist(json.dumps(run, indent=2), folder_path, "_run.json", bucket_name=bucket_name)

    # Enumerate starting at 4 since dbt Cloud indexes steps starting at 1
    # and has 3 internal steps (clone, profile, dbt deps)
    for step_index, _ in enumerate(run["job"]["execute_steps"], 4):
        _process_step(client, run, step_index, folder_path, bucket_name)


def _process_step(
    client: DbtCloudClient, run: Mapping, step_index: int, folder_path: Path, bucket_name: str = None
) -> None:
    """
    Processes an individual run step, by writing the artifacts in the file system
    """
    step_folder_path = Path(folder_path, f"step={step_index}")

    for artifact_enum in RELEVANT_ARTIFACTS:
        logger.info(f"Downloading {artifact_enum.name}")

        try:
            artifact = client.retrieve_artifact_from_run(run["id"], artifact_enum.value, step=step_index)
            filename = _generate_step_filename(artifact, artifact_enum)
            persist(json.dumps(artifact, indent=2), step_folder_path, filename, bucket_name=bucket_name)
        except requests.exceptions.HTTPError:
            logger.debug(f"Artifact not found: {artifact_enum.name}")


def _generate_step_filename(artifact: Mapping, artifact_name: str):
    """
    If this is a run result, we append which command generated it to the filename.
    This makes it easier for consumers that are interested in only run results from tests
    or only run results from models to only open the files they need.
    """
    if artifact_name == DbtArtifact.run_results:
        command_executed = artifact["args"]["which"]
        return f"{command_executed}_{artifact_name}.json"

        # For all other artifacts, just use the original artifact_name
    return f"{artifact_name}.json"


@typer_app.command("retrieve-artifacts-time-interval")
def run(
    output_folder: Path = typer.Option(..., help=HELP["output_folder"]),
    gcs_bucket_name: str = typer.Option(
        None,
        help="if provided, it will write to a GCS bucket instead of in "
        "the local file system. Both `gcs_bucket_name` and `output_folder` "
        "can be provided, in case you want to add the files to a subfolder "
        "in the bucket.",
    ),
    start_time: datetime = typer.Option(..., help="the start time (inclusive), in UTC"),
    end_time: datetime = typer.Option(..., help="the end time (not inclusive), in UTC"),
    environment_id: int = typer.Option(..., envvar="DBT_CLOUD_ENVIRONMENT_ID", help=HELP["environment_id"]),
    account_id: int = typer.Option(..., envvar="DBT_CLOUD_ACCOUNT_ID", help=HELP["account_id"]),
    project_id: int = typer.Option(..., envvar="DBT_CLOUD_PROJECT_ID", help=HELP["project_id"]),
    token: str = typer.Option(..., envvar="DBT_CLOUD_TOKEN", help=HELP["token"]),
) -> None:
    """
    Retrieves artifacts from all runs between start_time (inclusive) and end_time (not inclusive).
    """
    start_time = start_time.replace(tzinfo=timezone.utc)
    end_time = end_time.replace(tzinfo=timezone.utc)

    client = DbtCloudClient(account_id=account_id, project_id=project_id, environment_id=environment_id, token=token)
    logger.info(f"Initializing dbt Cloud client for account {account_id}, project {project_id}")

    runs = client.retrieve_runs_finished_between(start_time, end_time)

    for run in runs:
        _process_run(client, run, output_folder, gcs_bucket_name)


# Entry point for direct execution
if __name__ == "__main__":
    typer_app()
