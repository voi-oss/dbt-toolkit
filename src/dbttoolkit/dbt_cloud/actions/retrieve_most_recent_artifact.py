"""
https://docs.getdbt.com/dbt-cloud/api#section/How-to-use-this-API

curl --request GET \
  --url https://cloud.getdbt.com/api/v2/accounts/ \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token <your token>'
"""
import json
from pathlib import Path

import typer

from dbttoolkit.dbt_cloud.actions._docs import HELP
from dbttoolkit.dbt_cloud.clients.dbt_cloud_client import DbtCloudClient
from dbttoolkit.dbt_cloud.models.dbt_artifact import DbtArtifact
from dbttoolkit.utils.io import write_to_file
from dbttoolkit.utils.logger import get_logger

typer_app = typer.Typer()
logger = get_logger()


@typer_app.command("retrieve-most-recent-artifact")
def run(
    artifact_name: DbtArtifact = typer.Argument(..., help="which artifact you want to retrieve"),
    output_folder: Path = typer.Option(..., help=HELP["output_folder"]),
    preferred_commit: str = typer.Option(
        None,
        help="if provided, tries to find the most recent run from "
        "that commit. If nothing is found, falls back to the most "
        "recent run overall (always respecting the job_id argument)",
    ),
    environment_id: int = typer.Option(..., envvar="DBT_CLOUD_ENVIRONMENT_ID", help=HELP["environment_id"]),
    account_id: int = typer.Option(..., envvar="DBT_CLOUD_ACCOUNT_ID", help=HELP["account_id"]),
    project_id: int = typer.Option(..., envvar="DBT_CLOUD_PROJECT_ID", help=HELP["project_id"]),
    job_id: int = typer.Option(..., envvar="DBT_CLOUD_JOB_ID", help=HELP["job_id"]),
    token: str = typer.Option(..., envvar="DBT_CLOUD_TOKEN", help=HELP["token"]),
) -> None:
    """
    Retrieves the `artifact_name` from the latest run from a job.
    """
    client = DbtCloudClient(account_id=account_id, project_id=project_id, environment_id=environment_id, token=token)
    logger.info(f"Initializing dbt Cloud client for account {account_id}, project {project_id}, job {job_id}")

    run = client.retrieve_most_recent_run_for_job(job_id, preferred_commit)
    logger.info(f'Retrieved run {run["id"]} from {run["finished_at_humanized"]} ago (commit: {run["git_sha"]})')

    manifest = client.retrieve_artifact_from_run(run["id"], artifact_name)
    write_to_file(json.dumps(manifest, indent=2), output_folder, f"{artifact_name}.json")


# Entry point for direct execution
if __name__ == "__main__":
    typer_app()
