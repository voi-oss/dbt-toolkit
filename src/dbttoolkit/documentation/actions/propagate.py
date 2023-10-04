from pathlib import Path
from typing import Mapping, Optional

import typer
from rich import print

from dbttoolkit.documentation.models.column import Column, ColumnRegistry
from dbttoolkit.documentation.presentation.formatters import format_upstream_descriptions_to_human_readable
from dbttoolkit.documentation.presentation.stats import calculate_and_print
from dbttoolkit.utils.io import load_json_file, write_json_file
from dbttoolkit.utils.logger import init_logger

IGNORED_COLUMNS = ["id", "created_at", "updated_at", "_row_updated_at", "deleted_at"]

typer_app = typer.Typer()
logger = init_logger()


def traverse_upstream(column: Column, manifest: Mapping, catalog: Mapping, registry: ColumnRegistry) -> None:
    """
    Given our main column (expected to already have been added to the registry), traverse the project upstream
    looking for columns with the same name. If a match is found, make sure the upstream column is already
    in the catalog and register it as a dependency to the main column.

    :return: None. The results are stored in the column and registry objects.
    """
    depends_on = column.node.get("depends_on", {}).get("nodes")

    if not depends_on:
        # No upstream dependencies, nothing to do
        return None

    # Sources are stored in a different place, but we want to process them together
    manifest_nodes = {**manifest["nodes"], **manifest["sources"]}
    catalog_nodes = {**catalog["nodes"], **catalog["sources"]}

    # Support for our "column renaming"/alias feature
    column_alias = column.artifact_column.get("meta", {}).get("original_name")
    column_name = column_alias or column.name

    for upstream_node_key in depends_on:
        # For every upstream node, look for it in the manifest and in the catalog
        manifest_node = manifest_nodes.get(upstream_node_key, {})
        manifest_column_in_upstream_node = manifest_node.get("columns", {}).get(column_name.lower())

        # Might not in the catalog (eg: ephemeral models), so the get logic needs fallbacks
        # TODO: Assuming everything is uppercase in the catalog is probably Snowflake specific. Better to normalize it
        # from both sides (ours and from the artifact)
        catalog_node = catalog_nodes.get(upstream_node_key, {})
        catalog_column_in_upstream_node = catalog_node.get("columns", {}).get(column_name.upper())

        # If it's available in any of the two, add (or retrieve) it to the catalog and
        # register it in the column as an upstream dependency
        if manifest_column_in_upstream_node or catalog_column_in_upstream_node:
            upstream_column = registry.add_or_retrieve(
                column_in_manifest=manifest_column_in_upstream_node,
                column_in_catalog=catalog_column_in_upstream_node,
                node=manifest_node,
            )

            column.add_upstream_match(upstream_column)


def traverse_artifacts(catalog: Mapping, manifest: Mapping, registry: ColumnRegistry) -> None:
    """
    Traverse the catalog while using the manifest to look for information to populate the registry.

    * For every node in the catalog:
        * See if the node is available in the manifest
        * For every column in the catalog:
            * Check if the column is also represented in the manifest
            * Add both the catalog and manifest representation of that column on the registry
            * Look if any upstream model has the same column. That method is not recursive, but
              `traverse_artifacts` will navigate through all nodes, covering the entire project

    :return: None. The results are stored in the registry
    """
    for node_key, node_in_catalog in catalog["nodes"].items():
        node_in_manifest = manifest["nodes"][node_key]
        columns_in_catalog = node_in_catalog["columns"]

        for column_key, column_in_catalog in columns_in_catalog.items():
            column_key = column_key.lower()
            column_in_manifest = node_in_manifest["columns"].get(column_key)

            column = registry.add_or_retrieve(
                column_in_manifest=column_in_manifest, column_in_catalog=column_in_catalog, node=node_in_manifest
            )

            traverse_upstream(column, manifest, catalog, registry)


def propagate_documentation_in_the_manifest(registry: ColumnRegistry, manifest: Mapping) -> None:
    for column in registry.data.values():
        if column.description or not column.descriptions_from_upstream:
            # If the column is already documented or it is not, but there's no upstream documentation
            continue

        if column.name in IGNORED_COLUMNS:
            print(f"Ignoring column {column.name} in {column.node_id}")
            continue

        node_in_manifest = manifest["nodes"][column.node_id]

        print(f"[bold red]MISSING[/]: Column [bold]{column.node_id} → {column.name}[/] missing documentation")
        print(
            "  => 🔎 [bold green]FOUND[/]: Found {} candidate: {}\n".format(
                len(column.descriptions_from_upstream.keys()), list(column.descriptions_from_upstream.keys())
            )
        )

        formatted_description = format_upstream_descriptions_to_human_readable(column.descriptions_from_upstream)

        if column.name in node_in_manifest["columns"]:
            node_in_manifest["columns"][column.name]["description"] = formatted_description
        else:
            node_in_manifest["columns"][column.name] = dict(
                name=column.name, description=formatted_description, tags=["inherited-documentation"]
            )


@typer_app.command("propagate")
def run(
    artifacts_folder: Path = typer.Option(..., help="The path to the artifacts folder to be used as input"),
    input_manifest_filename: Optional[str] = typer.Option("manifest.json", help="The name of the manifest file"),
    output_manifest_path: Optional[Path] = typer.Option(
        None, help="The full path and filename to the modified manifest file."
    ),
):
    """
    If the output manifest path is not provided, the path to the input manifest is chosen as output and thus it is
    overwritten.
    """
    # Read artifacts
    manifest_path = artifacts_folder / input_manifest_filename  # type: ignore
    manifest = load_json_file(manifest_path)
    catalog = load_json_file(artifacts_folder / "catalog.json")

    # Create a data structure to hold all columns
    registry = ColumnRegistry()

    # Traverse the catalog and manifest and populate the registry
    traverse_artifacts(catalog, manifest, registry)

    # Use the registry to find which documentation can be propagated and write it back to the manifest
    propagate_documentation_in_the_manifest(registry, manifest)

    # Persist the modified manifest
    if output_manifest_path:
        output_path = output_manifest_path
    else:
        output_path = manifest_path

    write_json_file(manifest, output_path)

    # Calculate and print stats
    calculate_and_print(registry)


# Entry point for direct execution
if __name__ == "__main__":
    typer_app()
