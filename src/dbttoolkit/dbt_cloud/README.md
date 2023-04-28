# dbt Cloud REST API client

A simple client for the [dbt Cloud REST API](https://docs.getdbt.com/dbt-cloud/api-v2).

The main use-cases implemented are related to downloading 
[dbt artifacts](https://docs.getdbt.com/reference/artifacts/dbt-artifacts) from runs executed in a dbt Cloud project.

## Commands

### Common options

The following options are mandatory and required for all the commands below.
They can be provided either as CLI options or environment variables.

```
--account-id INTEGER      [env var: DBT_CLOUD_ACCOUNT_ID; required]
--project-id INTEGER      [env var: DBT_CLOUD_PROJECT_ID; required]
--environment-id INTEGER  [env var: DBT_CLOUD_ENVIRONMENT_ID; required]
--token TEXT              [env var: DBT_CLOUD_TOKEN; required]
```

In all examples above, it is assumed that those options have been passed as environment 
variables.

### Retrieve most recent artifact

Retrieves the most recent specified artifact from a specified job.

We use this command internally to retrieve the most recent `manifest` from our main
production job in order to use it for runs using dbt's 
[state-based](https://docs.getdbt.com/reference/node-selection/methods#the-state-method) 
selectors as part of our CI workflows.

Basic usage:
```shell
$ dbt-toolkit dbt-cloud retrieve-most-recent-artifact ARTIFACT_NAME \
    --output-folder PATH [required] \
    --job-id INTEGER     [env var: DBT_CLOUD_JOB_ID; required]
```

Example:
```shell
$ dbt-toolkit dbt-cloud retrieve-most-recent-artifact manifest \
    --output-folder "/tmp/" \
    --job-id 1234
```

The `PATH` (required option) must be a path to a folder and `ARTIFACT_NAME` must be one of the following: `catalog|manifest|run_results|sources`.

### Retrieve artifacts by time interval

Retrieves all the artifacts from all the jobs (in the given dbt Cloud project) that finished between
a specified time interval.

We use this internally to retrieve all the artifacts from all our jobs for further metadata analysis, such as historical
tracking of our documentation and test coverage.  The time interval help us execute this on an hourly basis in our
scheduler.

Basic usage:
```shell
$ dbt-toolkit dbt-cloud retrieve-artifacts-time-interval \
    --output-folder PATH              [required] \
    --start-time [%Y-%m-%dT%H:%M:%S]  [required] \
    --end-time   [%Y-%m-%dT%H:%M:%S]  [required]
```

Example:
```shell
$ dbt-toolkit dbt-cloud retrieve-artifacts-time-interval \
    --output-folder "/tmp/" \
    --start-time 2022-06-01T00:00:00 \
    --end-time 2022-06-01T01:00:00
```

The output files are partitioned by date, hour, `job_id`, `run_id` and `step`, as the following
example:

```
date=2022-06-01
└── hour=00
    ├── job_id=1234
    │   └── run_id=60060838
    │       ├── _run.json
    │       └── step=4
    │           ├── manifest.json
    │           └── test_run_results.json
    └── job_id=4567
        └── run_id=60061366
            ├── _run.json
            ├── step=4
            │   ├── manifest.json
            │   └── seed_run_results.json
            └── step=5
                ├── manifest.json
                └── run_run_results.json
```

On dbt Cloud, each job can have several steps. The first 3 steps are internal from dbt Cloud
(1: cloning the repository, 2: creating a profile file, 3: running `dbt deps`) and ignored.
The steps given by the dbt Cloud user starts from `step=4`.

For the file names: run results artifacts are prefixed by which command was executed
(eg: `run_run_results.json` for a `dbt run` execution, or `seed_run_results.json` for a `dbt seed` execution).
The other artifacts (manifest, catalog, sources) have their original names maintained.

A `_run.json` metadata file with the dbt Cloud API response is also persisted.

There is an optional argument to this command named `gcs_bucket_name`. If provided, all the folders and files will be 
written in a Google Cloud Storage bucket instead of in the local file system. Both `gcs_bucket_name` and `output_folder`
can be provided, in case you want to add the files to a subfolder in the bucket.
