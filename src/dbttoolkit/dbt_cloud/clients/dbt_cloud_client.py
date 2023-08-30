from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Dict, Iterable, List, Mapping, Optional

import requests

from dbttoolkit.utils.logger import get_logger

logger = get_logger()

LARGE_PAGE_SIZE = 2000
STANDARD_PAGE_SIZE = 500


@dataclass
class DbtCloudClient:
    """
    A wrapper around the dbt Cloud REST API
    """

    account_id: int
    project_id: int
    environment_id: int
    token: str

    BASE_URL: ClassVar[str] = "https://cloud.getdbt.com/api/v2"

    def retrieve_runs_finished_between(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        Retrieves all runs that finished between start_time (inclusive) and end_time (not inclusive).

        :param start_time: the start time
        :param end_time: the end time
        :return: a list of runs
        """
        logger.info(f"Retrieving all production runs (between {start_time} and {end_time})")

        # As of 2021-08, a page size of 2000 will give us around 1 month worth of runs
        completed_runs = self.retrieve_completed_runs(page_size=LARGE_PAGE_SIZE, created_after=start_time)
        runs = [
            run
            for run in completed_runs
            if datetime.fromisoformat(run["finished_at"]) >= start_time
            and datetime.fromisoformat(run["finished_at"]) < end_time
        ]

        return runs

    def retrieve_most_recent_run_for_job(self, job_id: int, preferred_commit: str = None) -> Dict:
        """
        Retrieves the most successful run from `job_id`.

        If a preferred_commit SHA is provided, first we try to find the latest run from that
        commit before falling back to the latest run overall (always respecting the job_id)

        :param job_id: the id of the job
        :param preferred_commit: an optional commit SHA
        :return: one individual run
        """
        logger.info(f"Retrieving most recent run for job {job_id} (preferred commit: {preferred_commit})")

        completed_runs = self.retrieve_completed_runs()
        successful_runs = self.filter_successful_runs(completed_runs)
        successful_runs = [run for run in successful_runs if run["job_id"] == job_id]

        if preferred_commit:
            runs_from_preferred_commit = [run for run in successful_runs if run["git_sha"] == preferred_commit]

            if runs_from_preferred_commit:
                logger.info("Found run from preferred commit")
                return runs_from_preferred_commit[0]

        if not successful_runs:
            raise RuntimeError(f"No successful run found for job {job_id}")

        logger.info("Did not find run from preferred commit (or it was not provided). Picking the latest run instead.")
        return successful_runs[0]

    def retrieve_artifact_from_run(self, run_id: int, artifact_name: str, *, step: int = None) -> Dict:
        """
        Returns the artifact from a given run

        :param run_id: the id the the run
        :param artifact_name: the name of the artifact
        :param step: step index, starting at 1
        :return: the parsed (dict) artifact
        """

        params: Optional[Mapping] = None

        if step:
            params = {"step": step}

        response = requests.get(
            self.BASE_URL + f"/accounts/{self.account_id}/runs/{run_id}/artifacts/{artifact_name}.json",
            params=params,
            headers=self._default_headers(),
        )
        response.raise_for_status()

        return response.json()

    def retrieve_completed_runs(
        self, *, page_size: int = STANDARD_PAGE_SIZE, created_after: datetime = None
    ) -> List[Dict]:
        """
        Retrieves an arbitrary amount of recent completed runs

        :return: a list of runs
        """
        runs = []
        page = 0

        fetch_next_page = True

        while fetch_next_page:
            # A bit weird, but they do expect a string with an array inside
            params = {
                "order_by": "-id",
                "limit": str(page_size),
                "offset": str(page * page_size),
                "include_related": '["job", "environment", "trigger"]',
            }

            response = requests.get(
                self.BASE_URL + f"/accounts/{self.account_id}/runs", params=params, headers=self._default_headers()
            )
            response.raise_for_status()

            data = response.json()["data"]
            runs += data

            # Pagination: if the last record on this page was created after the time given, check the next page
            last_created_at = datetime.fromisoformat(data[-1]["created_at"])

            if created_after and last_created_at >= created_after:
                logger.info(f"Last result on page {page} ({last_created_at}) >= created after filter ({created_after})")
                page += 1
                fetch_next_page = True
            else:
                fetch_next_page = False

        completed_runs = [
            run
            for run in runs
            if run["is_complete"]
            and not run["is_cancelled"]
            and run["project_id"] == self.project_id
            and run["environment_id"] == self.environment_id
        ]

        return completed_runs

    @staticmethod
    def filter_successful_runs(runs: Iterable[Dict]) -> List[Dict]:
        """
        Retrieves an arbitrary amount of recent successful runs

        :return: a list of runs
        """
        successful_runs = [run for run in runs if run["is_success"]]

        return successful_runs

    def _default_headers(self) -> Dict:
        """
        The default headers for HTTP requests against the dbt Cloud API
        """
        return {"Content-Type": "application/json", "Authorization": f"Token {self.token}"}
