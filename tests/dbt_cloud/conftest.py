from pytest import fixture


@fixture
def account_id():
    return 123


@fixture
def project_id():
    return 456


@fixture
def environment_id():
    return 789


@fixture
def token():
    return "SECRET_TOKEN"


@fixture
def dbt_cloud_ids_cli(account_id, project_id, environment_id, token):
    return [
        "--account-id",
        account_id,
        "--project-id",
        project_id,
        "--environment-id",
        environment_id,
        "--token",
        token,
    ]


@fixture
def dbt_cloud_ids(account_id, project_id, environment_id):
    return dict(account_id=account_id, project_id=project_id, environment_id=environment_id)
