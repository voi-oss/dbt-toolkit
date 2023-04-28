import typer

from dbttoolkit.documentation.actions.propagate import typer_app as propagate_typer_app

documentation_typer_app = typer.Typer()
documentation_typer_app.registered_commands.append(*propagate_typer_app.registered_commands)
