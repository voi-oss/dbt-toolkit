import typer

from dbttoolkit.dbt_cloud.actions import dbt_cloud_typer_app
from dbttoolkit.documentation.actions import documentation_typer_app

app = typer.Typer()

app.add_typer(documentation_typer_app, name="docs")
app.add_typer(dbt_cloud_typer_app, name="dbt-cloud")


def main():
    app()
